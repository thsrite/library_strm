import re
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
# 云盘源文件挂载本地后 挂载进媒体服务器的路径，与上方对应   /mount/cloud/aliyun/emby/tvshow/爸爸去哪儿/Season 5/14.特别版.mp4
library_path = "/mount/cloud/aliyun/emby"

files = list_files(Path(source_path), ['.strm'])

for f in files:
    print(f"开始处理文件 {f}")
    try:
        with open(f, 'r') as file:
            content = file.read()
            # 获取扩展名
            ext = str(content).split(".")[-1]
            library_file = str(f).replace(source_path, library_path)
            library_file = Path(library_file).parent.joinpath(Path(library_file).stem + "." + ext)
            with open(f, 'w') as file2:
                print(f"开始写入 媒体库路径 {library_file}")
                file2.write(str(library_file))
    except Exception as e:
        print(e)
