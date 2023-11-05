import json
import logging
import os
import shutil
import urllib.parse
from pathlib import Path
from typing import Any

import yaml
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver

logging.basicConfig(filename="alipan_redirect",
                    format='%(asctime)s - %(name)s - %(levelname)s -%(module)s:  %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S ',
                    level=logging.INFO)
logger = logging.getLogger()
KZT = logging.StreamHandler()
KZT.setLevel(logging.DEBUG)
logger.addHandler(KZT)


class FileMonitorHandler(FileSystemEventHandler):
    """
    目录监控响应类
    """

    def __init__(self, watching_path: str, file_change: Any, **kwargs):
        super(FileMonitorHandler, self).__init__(**kwargs)
        self._watch_path = watching_path
        self.file_change = file_change

    def on_any_event(self, event):
        logger.info(f"目录监控event_type::: {event.event_type}")
        logger.info(f"目录监控on_any_event事件路径::: {event.src_path}")

    def on_created(self, event):
        logger.info(f"目录监控created事件路径::: {event.src_path}")
        self.file_change.event_handler(event=event, source_dir=self._watch_path, event_path=event.src_path)

    # def on_deleted(self, event):
    #     logger.info(f"目录监控deleted事件路径 src_path::: {event.src_path}")
    #     self.file_change.event_handler(event=event, event_path=event.src_path)

    def on_moved(self, event):
        logger.info(f"目录监控moved事件路径 src_path::: {event.src_path}")
        logger.info(f"目录监控moved事件路径 dest_path::: {event.dest_path}")
        logger.info("fast模式能触发，暂不处理")
        # self.file_change.event_handler(event=event, source_dir=self._watch_path, event_path=event.dest_path)


class FileChange:
    _dirconf = {}
    _modeconf = {}
    _libraryconf = {}
    _cloudtypeconf = {}
    _cloudurlconf = {}
    _cloudpathconf = {}

    def __init__(self):
        """
        初始化参数
        """

        filepath = os.path.join("/mnt", "config.yaml")
        with open(filepath, 'r') as f:  # 用with读取文件更好
            configs = yaml.load(f, Loader=yaml.FullLoader)  # 按字典格式读取并返回

        self.monitor_confs = configs["sync"]["monitor_confs"]
        if not isinstance(self.monitor_confs, list):
            self.monitor_confs = [self.monitor_confs]

        # 存储目录监控配置
        for monitor_conf in self.monitor_confs:
            if not isinstance(monitor_conf, dict):
                monitor_conf = json.loads(monitor_conf)
            self._dirconf[monitor_conf.get("source_dir")] = monitor_conf.get("dest_dir")
            self._modeconf[monitor_conf.get("source_dir")] = monitor_conf.get("monitoring_mode")
            self._libraryconf[monitor_conf.get("source_dir")] = monitor_conf.get("library_dir")
            self._cloudtypeconf[monitor_conf.get("source_dir")] = monitor_conf.get("cloud_type")
            self._cloudpathconf[monitor_conf.get("source_dir")] = monitor_conf.get("cloud_path")
            self._cloudurlconf[monitor_conf.get("source_dir")] = monitor_conf.get("cloud_url")

    def start(self):
        """
        开始目录监控
        """
        if not self._dirconf or not self._dirconf.keys():
            logger.error(f"未获取到目录监控配置，请检查配置文件填写是否正确")

        # 遍历  开启多路径目录监控
        for source_dir in list(self._dirconf.keys()):
            # 转移方式
            monitoring_mode = self._modeconf.get(source_dir)
            if str(monitoring_mode) == "compatibility":
                # 兼容模式，目录同步性能降低且NAS不能休眠，但可以兼容挂载的远程共享目录如SMB
                observer = PollingObserver(timeout=10)
            else:
                # 内部处理系统操作类型选择最优解
                observer = Observer(timeout=10)
            observer.schedule(event_handler=FileMonitorHandler(str(source_dir), self),
                              path=str(source_dir),
                              recursive=True)
            logger.info(f"开始监控文件夹 {str(source_dir)} 转移方式 {str(monitoring_mode)}")
            observer.daemon = True
            observer.start()

    def event_handler(self, event, source_dir: str, event_path: str):
        """
        文件变动handler
        :param event:
        :param source_dir:
        :param event_path:
        """
        # 回收站及隐藏的文件不处理
        if (event_path.find("/@Recycle") != -1
                or event_path.find("/#recycle") != -1
                or event_path.find("/.") != -1
                or event_path.find("/@eaDir") != -1):
            logger.info(f"{event_path} 是回收站或隐藏的文件，跳过处理")
            return

        logger.info(f"event_type::: {event.event_type}")

        logger.info(f"event_path {event_path} source_path {source_dir}")
        if event.event_type == "created":
            self.event_handler_created(event, event_path, source_dir)
        # if event.event_type == "deleted":
        #     self.event_handler_deleted(event_path, source_dir)

    def event_handler_created(self, event, event_path: str, source_dir: str):
        try:
            logger.info(f"event_handler_created event_path:::{event_path}")
            # 转移路径
            dest_dir = self._dirconf.get(source_dir)
            # 媒体库容器内挂载路径
            library_dir = self._libraryconf.get(source_dir)
            # 云服务类型
            cloud_type = self._cloudtypeconf.get(source_dir)
            # 云服务挂载本地跟路径
            cloud_path = self._cloudpathconf.get(source_dir)
            # 云服务地址
            cloud_url = self._cloudurlconf.get(source_dir)
            # 文件夹同步创建
            if event.is_directory:
                target_path = event_path.replace(source_dir, dest_dir)
                # 目标文件夹不存在则创建
                if not Path(target_path).exists():
                    logger.info(f"创建目标文件夹 {target_path}")
                    os.makedirs(target_path)
            else:
                # 文件：nfo、图片、视频文件
                dest_file = event_path.replace(source_dir, dest_dir)

                # 目标文件夹不存在则创建
                if not Path(dest_file).parent.exists():
                    logger.info(f"创建目标文件夹 {Path(dest_file).parent}")
                    os.makedirs(Path(dest_file).parent)

                # 视频文件创建.strm文件
                video_formats = (
                    '.mp4', '.avi', '.rmvb', '.wmv', '.mov', '.mkv', '.flv', '.ts', '.webm', '.iso', '.mpg')
                if event_path.lower().endswith(video_formats):
                    # 如果视频文件小于1MB，则直接复制，不创建.strm文件
                    if os.path.getsize(event_path) < 1024 * 1024:
                        shutil.copy2(event_path, dest_file)
                        logger.info(f"复制视频文件 {event_path} 到 {dest_file}")
                    else:
                        # 创建.strm文件
                        self.__create_strm_file(dest_file=dest_file,
                                                dest_dir=dest_dir,
                                                library_dir=library_dir,
                                                cloud_type=cloud_type,
                                                cloud_path=cloud_path,
                                                cloud_url=cloud_url)
                else:
                    # 其他nfo、jpg等复制文件
                    shutil.copy2(event_path, dest_file)
                    logger.info(f"复制其他文件 {event_path} 到 {dest_file}")

        except Exception as e:
            logger.error(f"event_handler_created error: {e}")
            print(str(e))

    def event_handler_deleted(self, event_path: str, source_dir: str):
        # 转移路径
        dest_dir = self._dirconf.get(source_dir)
        deleted_target_path = event_path.replace(source_dir, dest_dir)

        # 只删除不存在的目标路径
        if not Path(deleted_target_path).exists():
            logger.info(f"目标路径不存在，跳过删除::: {deleted_target_path}")
        else:
            logger.info(f"目标路径存在，删除::: {deleted_target_path}")

            if Path(deleted_target_path).is_file():
                Path(deleted_target_path).unlink()
            else:
                # 非根目录，才删除目录
                shutil.rmtree(deleted_target_path)
        self.__delete_empty_parent_directory(event_path)

    @staticmethod
    def __delete_empty_parent_directory(file_path):
        parent_dir = Path(file_path).parent
        if (
                parent_dir != Path("/")
                and parent_dir.is_dir()
                and not any(parent_dir.iterdir())
                and parent_dir.exists()
        ):
            try:
                parent_dir.rmdir()
                logger.info(f"删除空的父文件夹: {parent_dir}")
            except OSError as e:
                logger.error(f"删除空父目录失败: {e}")

    @staticmethod
    def __create_strm_file(dest_file: str, dest_dir: str, library_dir: str, cloud_type: str = None,
                           cloud_path: str = None, cloud_url: str = None):
        """
        生成strm文件
        :param library_dir:
        :param dest_dir:
        :param dest_file:
        """
        try:
            # 获取视频文件名和目录
            video_name = Path(dest_file).name
            # 获取视频目录
            dest_path = Path(dest_file).parent

            if not dest_path.exists():
                logger.info(f"创建目标文件夹 {dest_path}")
                os.makedirs(str(dest_path))

            # 构造.strm文件路径
            strm_path = os.path.join(dest_path, f"{os.path.splitext(video_name)[0]}.strm")
            logger.info(f"替换前本地路径:::{dest_file}")

            # 云盘模式
            if cloud_type:
                # 替换路径中的\为/
                dest_file = dest_file.replace("\\", "/")
                dest_file = dest_file.replace(cloud_path, "")
                # 对盘符之后的所有内容进行url转码
                dest_file = urllib.parse.quote(dest_file, safe='')
                if str(cloud_type) == "cd2":
                    # 将路径的开头盘符"/mnt/user/downloads"替换为"http://localhost:19798/static/http/localhost:19798/False/"
                    dest_file = f"http://{cloud_url}/static/http/{cloud_url}/False/{dest_file}"
                    logger.info(f"替换后cd2路径:::{dest_file}")
                elif str(cloud_type) == "alist":
                    dest_file = f"http://{cloud_url}/d/{dest_file}"
                    logger.info(f"替换后alist路径:::{dest_file}")
                else:
                    logger.error(f"云盘类型 {cloud_type} 错误")
                    return
            else:
                # 本地挂载路径转为emby路径
                dest_file = dest_file.replace(dest_dir, library_dir)
                logger.info(f"替换后emby容器内路径:::{dest_file}")

            # 写入.strm文件
            with open(strm_path, 'w') as f:
                f.write(dest_file)

            logger.info(f"创建strm文件 {strm_path}")
        except Exception as e:
            logger.error(f"创建strm文件失败")
            print(str(e))
