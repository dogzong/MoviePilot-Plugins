import json
import os
import shutil
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Dict, Tuple, Optional

import pytz
import requests
import re
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.core.event import eventmanager, Event
from app.log import logger
from app.plugins import _PluginBase
from app.schemas.types import EventType


class CloudStrmAINamer:
    """AI智能命名助手 - 使用DeepSeek API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        # 文件夹命名缓存，避免重复调用API
        self._folder_cache: Dict[str, Dict] = {}
    
    @staticmethod
    def _is_season_folder(folder_name: str) -> bool:
        """判断是否为季度文件夹
        
        Args:
            folder_name: 文件夹名称
        
        Returns:
            bool: 是否为季度文件夹
        """
        season_patterns = [
            r'[Ss](eason)?\s*0?\d+',  # S01, S1, Season 1, season 01
            r'第\s*[\d一二三四五六七八九十]+\s*季',  # 第一季, 第1季
            r'Season\s*\d+',  # Season 1, Season 01
        ]
        
        for pattern in season_patterns:
            if re.search(pattern, folder_name, re.IGNORECASE):
                return True
        return False
        
    def get_folder_info(self, folder_name: str, sample_filename: str) -> Optional[Dict]:
        """获取文件夹的基础信息（只调用一次API）
        
        Returns:
            Dict: 包含剧集基础信息的字典
        """
        # 检查缓存
        if folder_name in self._folder_cache:
            logger.info(f"📦 [CloudStrmAI] 使用缓存: {folder_name}")
            return self._folder_cache[folder_name]
        
        try:
            prompt = self._build_prompt(folder_name, sample_filename)
            response = self._call_deepseek_api(prompt)
            
            if not response:
                logger.warning(f"[CloudStrmAI] API无响应: {folder_name}")
                return None
            
            response = re.sub(r'^```json\s*|\s*```$', '', response.strip(), flags=re.MULTILINE)
            data = json.loads(response)
            
            # 缓存结果
            self._folder_cache[folder_name] = data
            logger.info(f"💾 [CloudStrmAI] 已缓存: {folder_name}")
            
            return data
            
        except Exception as e:
            logger.error(f"[CloudStrmAI] 获取文件夹信息失败: {str(e)}")
            return None
    
    def get_ai_filename(self, folder_name: str, original_filename: str, folder_info: Dict = None) -> Optional[Tuple[str, str]]:
        """使用AI生成标准化的文件名和文件夹名
        
        Args:
            folder_name: 原文件夹名
            original_filename: 原文件名
            folder_info: 文件夹基础信息（由get_folder_info获取）
        
        Returns:
            Tuple[str, str]: (新文件名, 新文件夹名) 或 None
        """
        try:
            if not folder_info:
                # 如果没有提供folder_info，则调用API获取
                folder_info = self.get_folder_info(folder_name, original_filename)
                if not folder_info:
                    return None
            
            result = self._parse_ai_response_with_episode(folder_info, original_filename)
            if result:
                new_filename, new_foldername = result
                logger.info(f"✨ [CloudStrmAI] 命名: {original_filename} -> {new_filename}")
            
            return result
            
        except Exception as e:
            logger.error(f"[CloudStrmAI] AI命名异常: {str(e)}")
            return None
    
    def _build_prompt(self, folder_name: str, original_filename: str) -> str:
        return f"""你是媒体文件命名专家。根据文件夹名和文件名，生成MoviePilot标准文件名和文件夹名。

文件夹: {folder_name}
文件名: {original_filename}

规则:
1. 识别类型(电影/剧集)
2. 提取中英文标题、年份
3. 剧集提取S##E##
4. 保留质量(4K/2160p/1080p/H265)
5. 保留音频(DDP5.1/Atmos/AAC)
6. 对于包含特殊字符或难以解析的中文标题：
   - 尝试识别并还原可能被拆分的汉字部件
   - 参考已知影视作品数据库进行匹配
   - 优先考虑完整的中文剧名而非字面拆分
7. 季数识别：
   - "第X季"格式优先识别为季节信息
   - 括号中的数字优先识别为年份
8. 文件夹命名规则：
   - 电影: "中文标题 英文标题 (年份)"
   - 剧集: "中文标题 英文标题 (年份)"
   - 必须包含年份，格式为 (YYYY)

输出JSON(纯JSON,不要markdown):
{{
  "type": "movie或tv",
  "chinese_title": "中文标题",
  "english_title": "英文标题",
  "year": "年份",
  "season": "S##(仅剧集)",
  "episode": "E##(仅剧集)",
  "quality": "质量",
  "audio": "音频",
  "other": "其他",
  "folder_name": "标准化的文件夹名称"
}}

示例:
输入: 文件夹="飞驰人生2 (2024) 4K", 文件="Pegasus.2.2024.2160p.WEB-DL.H265.DDP5.1.mkv"
输出: {{"type":"movie","chinese_title":"飞驰人生2","english_title":"Pegasus 2","year":"2024","quality":"4K 2160p H265","audio":"DDP5.1","other":"WEB-DL","folder_name":"飞驰人生2 Pegasus 2 (2024)"}}

现在分析:"""

    def _call_deepseek_api(self, prompt: str) -> Optional[str]:
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 500
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                logger.error(f"[CloudStrmAI] DeepSeek API错误 [{response.status_code}]")
                return None
                
        except Exception as e:
            logger.error(f"[CloudStrmAI] API调用异常: {str(e)}")
            return None
    
    def _extract_episode_number(self, filename: str) -> Optional[Tuple[str, str]]:
        """从文件名中提取季集信息
        
        Returns:
            Tuple[str, str]: (season, episode) 或 None
        """
        # 匹配各种集数格式
        patterns = [
            r'[Ss](\d{1,2})[Ee](\d{1,2})',  # S01E01
            r'第\s*(\d+)\s*季.*?第\s*(\d+)\s*集',  # 第1季第1集
            r'[Ee][Pp]?(\d{1,2})',  # EP01, E01
            r'第\s*(\d+)\s*集',  # 第1集
            r'^\.?(\d{1,2})\.',  # 开头的数字: 01., .01.
            r'[^\d](\d{1,2})\.',  # 中间的数字
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename)
            if match:
                groups = match.groups()
                if len(groups) == 2:
                    return (f"S{int(groups[0]):02d}", f"E{int(groups[1]):02d}")
                elif len(groups) == 1:
                    return ("S01", f"E{int(groups[0]):02d}")
        
        return None
    
    def _parse_ai_response_with_episode(self, folder_info: Dict, original_filename: str) -> Optional[Tuple[str, str]]:
        """基于文件夹信息和文件名生成标准文件名
        
        Args:
            folder_info: AI返回的文件夹基础信息
            original_filename: 原始文件名
        
        Returns:
            Tuple[str, str]: (新文件名, 新文件夹名) 或 None
        """
        try:
            media_type = folder_info.get("type", "").lower()
            chinese_title = folder_info.get("chinese_title", "")
            english_title = folder_info.get("english_title", "")
            year = folder_info.get("year", "")
            quality = folder_info.get("quality", "")
            audio = folder_info.get("audio", "")
            other = folder_info.get("other", "")
            folder_name = folder_info.get("folder_name", "")
            ext = Path(original_filename).suffix
            
            # 从文件名中提取集数
            episode_info = self._extract_episode_number(original_filename)
            
            # 构建文件名
            parts = []
            if chinese_title:
                parts.append(chinese_title)
            if english_title:
                parts.append(english_title)
            
            filename = " ".join(parts) if parts else Path(original_filename).stem
            
            if media_type == "movie":
                if year:
                    filename += f" ({year})"
                details = [d for d in [quality, audio, other] if d]
                if details:
                    filename += " - " + " ".join(details)
            elif media_type == "tv":
                if year:
                    filename += f" ({year})"
                
                # 添加季集信息
                if episode_info:
                    season, episode = episode_info
                    filename += f" {season}{episode}"
                else:
                    # 如果无法提取集数，保留原始文件名的集数部分
                    logger.warning(f"⚠️ [CloudStrmAI] 无法提取集数: {original_filename}")
                
                details = [d for d in [quality, audio, other] if d]
                if details:
                    filename += " - " + " ".join(details)
            else:
                return None
            
            filename = re.sub(r'\s+', ' ', filename).replace('/', '-').replace('\\', '-')
            filename += ext
            
            # 生成文件夹名
            if not folder_name:
                folder_parts = []
                if chinese_title:
                    folder_parts.append(chinese_title)
                if english_title:
                    folder_parts.append(english_title)
                folder_name = " ".join(folder_parts) if folder_parts else ""
                if folder_name and year:
                    folder_name += f" ({year})"
            
            if not folder_name and chinese_title:
                folder_name = chinese_title
                if year:
                    folder_name += f" ({year})"
            
            if folder_name:
                folder_name = re.sub(r'\s+', ' ', folder_name).replace('/', '-').replace('\\', '-')
            
            return (filename, folder_name)
            
        except Exception as e:
            logger.error(f"[CloudStrmAI] 解析异常: {str(e)}")
            return None
    
    def _parse_ai_response(self, response: str, original_filename: str) -> Optional[Tuple[str, str]]:
        """解析AI响应，返回文件名和文件夹名
        
        Returns:
            Tuple[str, str]: (新文件名, 新文件夹名) 或 None
        """
        try:
            response = re.sub(r'^```json\s*|\s*```$', '', response.strip(), flags=re.MULTILINE)
            data = json.loads(response)
            
            media_type = data.get("type", "").lower()
            chinese_title = data.get("chinese_title", "")
            english_title = data.get("english_title", "")
            year = data.get("year", "")
            quality = data.get("quality", "")
            audio = data.get("audio", "")
            other = data.get("other", "")
            folder_name = data.get("folder_name", "")
            ext = Path(original_filename).suffix
            
            # 生成文件名
            if media_type == "movie":
                parts = []
                if chinese_title:
                    parts.append(chinese_title)
                if english_title:
                    parts.append(english_title)
                
                filename = " ".join(parts) if parts else Path(original_filename).stem
                if year:
                    filename += f" ({year})"
                
                details = [d for d in [quality, audio, other] if d]
                if details:
                    filename += " - " + " ".join(details)
                    
                filename += ext
                
            elif media_type == "tv":
                season = data.get("season", "")
                episode = data.get("episode", "")
                
                parts = []
                if chinese_title:
                    parts.append(chinese_title)
                if english_title:
                    parts.append(english_title)
                    
                filename = " ".join(parts) if parts else Path(original_filename).stem
                if year:
                    filename += f" ({year})"
                if season and episode:
                    filename += f" {season}{episode}"
                elif season:
                    filename += f" {season}"
                    
                details = [d for d in [quality, audio, other] if d]
                if details:
                    filename += " - " + " ".join(details)
                    
                filename += ext
            else:
                return None
            
            filename = re.sub(r'\s+', ' ', filename).replace('/', '-').replace('\\', '-')
            
            # 生成文件夹名（如果AI没有返回，则自动构建）
            if not folder_name:
                folder_parts = []
                if chinese_title:
                    folder_parts.append(chinese_title)
                if english_title:
                    folder_parts.append(english_title)
                folder_name = " ".join(folder_parts) if folder_parts else ""
                if folder_name and year:
                    folder_name += f" ({year})"
            
            # 如果还是没有文件夹名，并且至少有标题，则生成一个基础版本
            if not folder_name and chinese_title:
                folder_name = chinese_title
                if year:
                    folder_name += f" ({year})"
            
            # 清理文件夹名
            if folder_name:
                folder_name = re.sub(r'\s+', ' ', folder_name).replace('/', '-').replace('\\', '-')
            
            return (filename, folder_name)
            
        except json.JSONDecodeError as e:
            logger.error(f"[CloudStrmAI] JSON解析失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"[CloudStrmAI] 解析异常: {str(e)}")
            return None


class CloudStrmAI(_PluginBase):
    # 插件名称
    plugin_name = "云盘StrmAI"
    # 插件描述
    plugin_desc = "AI智能命名的云盘Strm生成器，自动识别中英文标题提高刮削准确率。支持多季嵌套结构智能识别。"
    # 插件图标
    plugin_icon = "https://raw.githubusercontent.com/thsrite/MoviePilot-Plugins/main/icons/create.png"
    # 插件版本
    plugin_version = "1.0.1"
    # 插件作者
    plugin_author = "dogzong"
    # 作者主页
    author_url = "https://github.com"
    # 插件配置项ID前缀
    plugin_config_prefix = "cloudstrmai_"
    # 加载顺序
    plugin_order = 27
    # 可使用的用户级别
    auth_level = 1

    # 私有属性
    _enabled = False
    _cron = None
    _rebuild_cron = None
    _monitor_confs = None
    _onlyonce = False
    _copy_files = False
    _rebuild = False
    _https = False
    _enable_ai_naming = True
    _deepseek_api_key = None
    __cloud_files_json = "cloudstrmai_files.json"

    _dirconf = {}
    _libraryconf = {}
    _cloudtypeconf = {}
    _cloudurlconf = {}
    _cloudpathconf = {}
    __cloud_files = []
    _ai_namer: Optional[CloudStrmAINamer] = None
    _scheduler: Optional[BackgroundScheduler] = None

    def init_plugin(self, config: dict = None):
        # 清空配置
        self._dirconf = {}
        self._libraryconf = {}
        self._cloudtypeconf = {}
        self._cloudurlconf = {}
        self._cloudpathconf = {}
        self.__cloud_files_json = os.path.join(self.get_data_path(), self.__cloud_files_json)

        if config:
            self._enabled = config.get("enabled")
            self._cron = config.get("cron")
            self._rebuild_cron = config.get("rebuild_cron")
            self._onlyonce = config.get("onlyonce")
            self._rebuild = config.get("rebuild")
            self._https = config.get("https")
            self._copy_files = config.get("copy_files")
            self._monitor_confs = config.get("monitor_confs")
            self._enable_ai_naming = config.get("enable_ai_naming", True)
            self._deepseek_api_key = config.get("deepseek_api_key")
            
        # 初始化AI
        if self._enable_ai_naming and self._deepseek_api_key:
            try:
                self._ai_namer = CloudStrmAINamer(self._deepseek_api_key)
                logger.info("✨ [CloudStrmAI] AI智能命名已启用")
            except Exception as e:
                logger.error(f"[CloudStrmAI] AI初始化失败: {str(e)}")
                self._ai_namer = None
        else:
            self._ai_namer = None

        self.stop_service()

        if self._enabled or self._onlyonce:
            self._scheduler = BackgroundScheduler(timezone=settings.TZ)

            monitor_confs = self._monitor_confs.split("\n") if self._monitor_confs else []
            if not monitor_confs:
                logger.warning("[CloudStrmAI] 未配置监控目录")
                return
                
            for monitor_conf in monitor_confs:
                if not monitor_conf or str(monitor_conf).startswith("#"):
                    continue
                    
                if str(monitor_conf).count("#") == 2:
                    parts = str(monitor_conf).split("#")
                    source_dir, target_dir, library_dir = parts[0], parts[1], parts[2]
                    self._libraryconf[source_dir] = library_dir
                    self._dirconf[source_dir] = target_dir
                elif str(monitor_conf).count("#") == 4:
                    parts = str(monitor_conf).split("#")
                    source_dir = parts[0]
                    target_dir = parts[1]
                    cloud_type = parts[2]
                    cloud_path = parts[3]
                    cloud_url = parts[4]
                    self._cloudtypeconf[source_dir] = cloud_type
                    self._cloudpathconf[source_dir] = cloud_path
                    self._cloudurlconf[source_dir] = cloud_url
                    self._dirconf[source_dir] = target_dir

            if self._onlyonce:
                logger.info("[CloudStrmAI] 立即执行一次")
                self._scheduler.add_job(
                    func=self.scan, 
                    trigger='date',
                    run_date=datetime.now(tz=pytz.timezone(settings.TZ)) + timedelta(seconds=3),
                    name="CloudStrmAI立即执行"
                )
                self._onlyonce = False
                self.__update_config()

            if self._cron:
                try:
                    self._scheduler.add_job(
                        func=self.scan,
                        trigger=CronTrigger.from_crontab(self._cron),
                        name="CloudStrmAI定时生成"
                    )
                except Exception as err:
                    logger.error(f"[CloudStrmAI] Cron配置错误：{err}")

            if self._rebuild_cron:
                try:
                    self._scheduler.add_job(
                        func=self.__init_cloud_files_json,
                        trigger=CronTrigger.from_crontab(self._rebuild_cron),
                        name="CloudStrmAI重建索引"
                    )
                except Exception as err:
                    logger.error(f"[CloudStrmAI] Cron配置错误：{err}")

            if self._scheduler.get_jobs():
                self._scheduler.print_jobs()
                self._scheduler.start()

    @eventmanager.register(EventType.PluginAction)
    def scan(self, event: Event = None):
        """扫描生成strm"""
        if not self._enabled:
            logger.error("[CloudStrmAI] 插件未启用")
            return
        if not self._dirconf:
            logger.error("[CloudStrmAI] 未配置监控目录")
            return

        if event:
            event_data = event.event_data
            if not event_data or event_data.get("action") != "cloudstrmai_scan":
                return
            logger.info("[CloudStrmAI] 收到扫描命令")

        logger.info("[CloudStrmAI] 🚀 任务开始")
        
        __init_flag = False
        if self._rebuild or not Path(self.__cloud_files_json).exists():
            logger.info("[CloudStrmAI] 重建索引...")
            self.__init_cloud_files_json()
            self._rebuild = False
            self.__update_config()
            __init_flag = True
        else:
            try:
                with open(self.__cloud_files_json, 'r') as file:
                    content = file.read()
                    if content:
                        self.__cloud_files = json.loads(content)
            except Exception as e:
                logger.error(f"[CloudStrmAI] 加载缓存失败: {e}")

        if not self.__cloud_files and not __init_flag:
            self.__init_cloud_files_json()
            __init_flag = True

        if not __init_flag:
            __save_flag = False
            for source_dir in self._dirconf.keys():
                logger.info(f"[CloudStrmAI] 扫描目录: {source_dir}")
                
                # 按文件夹分组新文件
                new_folder_files = {}
                for root, dirs, files in os.walk(source_dir):
                    if "extrafanart" in dirs:
                        dirs.remove("extrafanart")

                    for file in files:
                        source_file = os.path.join(root, file)
                        
                        if any(x in source_file for x in ["/@Recycle", "/#recycle", "/.", "/@eaDir"]):
                            continue

                        if not self._copy_files and Path(file).suffix.lower() not in settings.RMT_MEDIAEXT:
                            continue

                        if source_file not in self.__cloud_files:
                            folder_path = str(Path(source_file).parent)
                            if folder_path not in new_folder_files:
                                new_folder_files[folder_path] = []
                            new_folder_files[folder_path].append(source_file)
                
                # 按文件夹批量处理新文件
                for folder_path, files in new_folder_files.items():
                    logger.info(f"[CloudStrmAI] 📂 新文件夹: {Path(folder_path).name} ({len(files)}个新文件)")
                    
                    # 获取文件夹信息（智能识别嵌套结构）
                    folder_info = None
                    if self._ai_namer:
                        folder_name = Path(folder_path).name
                        sample_file = Path(files[0]).name
                        
                        # 判断是否为季度文件夹（嵌套结构）
                        if self._ai_namer._is_season_folder(folder_name):
                            # 使用父文件夹名称获取信息
                            parent_folder = Path(folder_path).parent.name
                            logger.info(f"📚 [CloudStrmAI] 检测到季度文件夹，使用父文件夹: {parent_folder}")
                            folder_info = self._ai_namer.get_folder_info(parent_folder, sample_file)
                        else:
                            # 普通文件夹
                            folder_info = self._ai_namer.get_folder_info(folder_name, sample_file)
                        
                        if folder_info:
                            logger.info(f"✨ [CloudStrmAI] 文件夹信息: {folder_info.get('chinese_title', '')} {folder_info.get('english_title', '')} ({folder_info.get('year', '')})")
                    
                    # 处理该文件夹下的所有新文件
                    for source_file in files:
                        self.__cloud_files.append(source_file)
                        self.__strm(source_file, folder_info)
                        __save_flag = True

            if __save_flag:
                self.__save_json()

        logger.info("[CloudStrmAI] ✅ 任务完成")

    def __init_cloud_files_json(self):
        """初始化文件列表（按文件夹批量处理）"""
        self.__cloud_files = []
        for source_dir in self._dirconf.keys():
            # 按文件夹分组
            folder_files = {}
            for root, dirs, files in os.walk(source_dir):
                if "extrafanart" in dirs:
                    dirs.remove("extrafanart")

                for file in files:
                    source_file = os.path.join(root, file)
                    
                    if any(x in source_file for x in ["/@Recycle", "/#recycle", "/.", "/@eaDir"]):
                        continue

                    if not self._copy_files and Path(file).suffix.lower() not in settings.RMT_MEDIAEXT:
                        continue

                    # 按文件夹分组
                    folder_path = str(Path(source_file).parent)
                    if folder_path not in folder_files:
                        folder_files[folder_path] = []
                    folder_files[folder_path].append(source_file)
            
            # 按文件夹批量处理
            for folder_path, files in folder_files.items():
                logger.info(f"[CloudStrmAI] 📂 处理文件夹: {Path(folder_path).name} ({len(files)}个文件)")
                
                # 获取文件夹信息（智能识别嵌套结构）
                folder_info = None
                if self._ai_namer and files:
                    folder_name = Path(folder_path).name
                    sample_file = Path(files[0]).name
                    
                    # 判断是否为季度文件夹（嵌套结构）
                    if self._ai_namer._is_season_folder(folder_name):
                        # 使用父文件夹名称获取信息
                        parent_folder = Path(folder_path).parent.name
                        logger.info(f"📚 [CloudStrmAI] 检测到季度文件夹，使用父文件夹: {parent_folder}")
                        folder_info = self._ai_namer.get_folder_info(parent_folder, sample_file)
                    else:
                        # 普通文件夹
                        folder_info = self._ai_namer.get_folder_info(folder_name, sample_file)
                    
                    if folder_info:
                        logger.info(f"✨ [CloudStrmAI] 文件夹信息: {folder_info.get('chinese_title', '')} {folder_info.get('english_title', '')} ({folder_info.get('year', '')})")
                
                # 处理该文件夹下的所有文件
                for source_file in files:
                    self.__cloud_files.append(source_file)
                    self.__strm(source_file, folder_info)

        if self.__cloud_files:
            self.__save_json()

    def __save_json(self):
        """保存文件列表"""
        with open(self.__cloud_files_json, 'w') as file:
            file.write(json.dumps(self.__cloud_files))

    def __strm(self, source_file, folder_info: Dict = None):
        """生成strm文件"""
        try:
            for source_dir in self._dirconf.keys():
                if not str(source_file).startswith(source_dir):
                    continue
                    
                dest_dir = self._dirconf.get(source_dir)
                library_dir = self._libraryconf.get(source_dir)
                cloud_type = self._cloudtypeconf.get(source_dir)
                cloud_path = self._cloudpathconf.get(source_dir)
                cloud_url = self._cloudurlconf.get(source_dir)

                dest_file = source_file.replace(source_dir, dest_dir)
                
                if Path(dest_file).suffix.lower() in settings.RMT_MEDIAEXT:
                    self.__create_strm_file(
                        scheme="https" if self._https else "http",
                        dest_file=dest_file,
                        dest_dir=dest_dir,
                        source_file=source_file,
                        library_dir=library_dir,
                        cloud_type=cloud_type,
                        cloud_path=cloud_path,
                        cloud_url=cloud_url,
                        ai_namer=self._ai_namer,
                        folder_info=folder_info
                    )
                elif self._copy_files:
                    if not Path(dest_file).parent.exists():
                        os.makedirs(Path(dest_file).parent, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
                    
        except Exception as e:
            logger.error(f"[CloudStrmAI] 处理失败: {e}")

    @staticmethod
    def __create_strm_file(dest_file: str, dest_dir: str, source_file: str, library_dir: str = None,
                           cloud_type: str = None, cloud_path: str = None, cloud_url: str = None,
                           scheme: str = None, ai_namer: Optional[CloudStrmAINamer] = None,
                           folder_info: Dict = None):
        """创建strm文件(支持AI命名，包括文件夹重命名)"""
        try:
            video_name = Path(dest_file).name
            dest_path = Path(dest_file).parent
            
            # AI智能命名（文件名和文件夹名）
            if ai_namer:
                try:
                    folder_name = Path(source_file).parent.name
                    original_filename = Path(source_file).name
                    
                    # 使用缓存的folder_info
                    ai_result = ai_namer.get_ai_filename(folder_name, original_filename, folder_info)
                    
                    if ai_result:
                        ai_filename, ai_foldername = ai_result
                        video_name = ai_filename
                        
                        # 使用AI生成的文件夹名重构路径
                        if ai_foldername:
                            # 获取dest_path的父目录，然后拼接新的文件夹名
                            parent_path = dest_path.parent
                            dest_path = parent_path / ai_foldername
                        
                        dest_file = str(dest_path / ai_filename)
                except Exception as e:
                    logger.error(f"[CloudStrmAI] AI命名失败: {str(e)}")

            if not dest_path.exists():
                os.makedirs(str(dest_path), exist_ok=True)

            strm_path = os.path.join(dest_path, f"{os.path.splitext(video_name)[0]}.strm")
            
            if Path(strm_path).exists():
                return

            # 云盘模式
            if cloud_type:
                dest_file = source_file.replace("\\", "/").replace(cloud_path, "")
                dest_file = urllib.parse.quote(dest_file, safe='')
                
                if str(cloud_type) == "cd2":
                    dest_file = f"{scheme}://{cloud_url}/static/{scheme}/{cloud_url}/False/{dest_file}"
                elif str(cloud_type) == "alist":
                    dest_file = f"{scheme}://{cloud_url}/dav/{dest_file}"
                else:
                    logger.error(f"[CloudStrmAI] 未知云盘类型: {cloud_type}")
                    return
            else:
                dest_file = dest_file.replace(dest_dir, library_dir)

            with open(strm_path, 'w', encoding='utf-8') as f:
                f.write(dest_file)

            logger.info(f"[CloudStrmAI] ✅ 创建: {Path(strm_path).name}")
            
        except Exception as e:
            logger.error(f"[CloudStrmAI] 创建失败: {e}")

    def __update_config(self):
        """更新配置"""
        self.update_config({
            "enabled": self._enabled,
            "onlyonce": self._onlyonce,
            "rebuild": self._rebuild,
            "copy_files": self._copy_files,
            "https": self._https,
            "cron": self._cron,
            "rebuild_cron": self._rebuild_cron,
            "monitor_confs": self._monitor_confs,
            "enable_ai_naming": self._enable_ai_naming,
            "deepseek_api_key": self._deepseek_api_key,
        })

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        """远程命令"""
        return [{
            "cmd": "/cloudstrmai",
            "event": EventType.PluginAction,
            "desc": "云盘StrmAI生成",
            "category": "",
            "data": {"action": "cloudstrmai_scan"}
        }]

    def get_api(self) -> List[Dict[str, Any]]:
        pass

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """配置表单"""
        return [
            {
                'component': 'VForm',
                'content': [
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'enabled', 'label': '启用插件'}
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'onlyonce', 'label': '立即运行一次'}
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'rebuild', 'label': '重建索引'}
                                }]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [{
                                    'component': 'VTextField',
                                    'props': {
                                        'model': 'cron',
                                        'label': '执行周期',
                                        'placeholder': '*/30 * * * * (每30分钟)'
                                    }
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 6},
                                'content': [{
                                    'component': 'VTextField',
                                    'props': {
                                        'model': 'rebuild_cron',
                                        'label': '重建周期',
                                        'placeholder': '0 2 * * * (每天2点)'
                                    }
                                }]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': [{
                                'component': 'VTextarea',
                                'props': {
                                    'model': 'monitor_confs',
                                    'label': '监控目录',
                                    'rows': 5,
                                    'placeholder': '源目录#目标目录#媒体库路径\n例: /dav/quark/quark/movies#/downloads/complete/movies#/media/movies'
                                }
                            }]
                        }]
                    },
                    {
                        'component': 'VRow',
                        'content': [
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'copy_files', 'label': '复制非媒体文件'}
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'https', 'label': '启用HTTPS'}
                                }]
                            },
                            {
                                'component': 'VCol',
                                'props': {'cols': 12, 'md': 4},
                                'content': [{
                                    'component': 'VSwitch',
                                    'props': {'model': 'enable_ai_naming', 'label': '✨ AI智能命名'}
                                }]
                            }
                        ]
                    },
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': [{
                                'component': 'VTextField',
                                'props': {
                                    'model': 'deepseek_api_key',
                                    'label': '🤖 DeepSeek API Key',
                                    'placeholder': 'sk-...',
                                    'type': 'password'
                                }
                            }]
                        }]
                    },
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': [{
                                'component': 'VAlert',
                                'props': {
                                    'type': 'success',
                                    'variant': 'tonal',
                                    'text': '✨ AI智能命名：自动分析文件夹和文件名，智能提取中英文标题、年份、季集信息，大幅提高刮削准确率！API Key申请: https://platform.deepseek.com'
                                }
                            }]
                        }]
                    },
                    {
                        'component': 'VRow',
                        'content': [{
                            'component': 'VCol',
                            'props': {'cols': 12},
                            'content': [{
                                'component': 'VAlert',
                                'props': {
                                    'type': 'info',
                                    'variant': 'tonal',
                                    'text': '📁 监控格式：\n基础: 源目录#目标目录#媒体库路径\nCD2: 源目录#目标目录#cd2#挂载路径#服务地址\nAlist: 源目录#目标目录#alist#挂载路径#服务地址'
                                }
                            }]
                        }]
                    }
                ]
            }
        ], {
            "enabled": False,
            "cron": "",
            "rebuild_cron": "",
            "onlyonce": False,
            "rebuild": False,
            "copy_files": False,
            "https": False,
            "enable_ai_naming": True,
            "deepseek_api_key": "",
            "monitor_confs": "",
        }

    def get_page(self) -> List[dict]:
        pass

    def stop_service(self):
        """停止服务"""
        try:
            if self._scheduler:
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
        except Exception as e:
            logger.error(f"[CloudStrmAI] 停止失败: {str(e)}")
