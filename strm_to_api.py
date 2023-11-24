import re
import urllib.parse
from pathlib import Path
from typing import List


def list_files(directory: Path, extensions: list, min_filesize: int = 0) -> List[Path]:
    """
    获取目录下所有指定扩展名的文件（包括子目录）
    """

    if not min_filesize:
        min_filesize = 0

    if not directory.exists():
        return []

    if directory.is_file():
        return [directory]

    if not min_filesize:
        min_filesize = 0

    files = []
    pattern = r".*(" + "|".join(extensions) + ")$"

    # 遍历目录及子目录
    for path in directory.rglob('**/*'):
        if path.is_file() \
                and re.match(pattern, path.name, re.IGNORECASE) \
                and path.stat().st_size >= min_filesize * 1024 * 1024:
            files.append(path)

    return files

# nas上strm视频根路径  /mnt/user/downloads/link/aliyun/tvshow/爸爸去哪儿/Season 5/14.特别版.strm
source_path = "/mnt/user/downloads/link/aliyun"
# 云盘源文件挂载本地后 挂载进媒体服务器的根路径，与上方对应   /aliyun/emby/tvshow/爸爸去哪儿/Season 5/14.特别版.mp4
library_path = "/aliyun/emby"

files = list_files(Path(source_path), ['.strm'])

for f in files:
    print(f"开始处理文件 {f}")
    try:
        library_file = str(f).replace(source_path, library_path)
        # 对盘符之后的所有内容进行url转码
        library_file = urllib.parse.quote(library_file, safe='')

        # 将路径的开头盘符"/mnt/user/downloads"替换为"http://localhost:19798/static/http/localhost:19798/False/"
        # http://192.168.31.103:19798/static/http/192.168.31.103:19798/False/%2F115%2Femby%2Fanime%2F%20%E4%B8%83%E9%BE%99%E7%8F%A0%20%281986%29%2FSeason%201.%E5%9B%BD%E8%AF%AD%2F%E4%B8%83%E9%BE%99%E7%8F%A0%20-%20S01E002%20-%201080p%20AAC%20h264.mp4
        api_file = f"http://192.168.31.103:19798/static/http/192.168.31.103:19798/False/{library_file}"
        with open(f, 'w') as file2:
            print(f"开始写入 api路径 {api_file}")
            file2.write(str(api_file))
    except Exception as e:
        print(e)
