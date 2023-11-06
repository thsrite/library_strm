# 支持多路径目录监控配置

[![Github][Github-image]][Github-url]
[![commit activity][commit-activity-image]][commit-activity-url]
[![docker version][docker-version-image]][docker-version-url]
[![docker pulls][docker-pulls-image]][docker-pulls-url]
[![docker stars][docker-stars-image]][docker-stars-url]
[![docker image size][docker-image-size-image]][docker-image-size-url]

[Github-image]: https://img.shields.io/static/v1?label=Github&message=library_strm&color=brightgreen
[Github-url]: https://github.com/thsrite/library_strm
[commit-activity-image]: https://img.shields.io/github/commit-activity/m/thsrite/library_strm
[commit-activity-url]: https://github.com/thsrite/library_strm
[docker-version-image]: https://img.shields.io/docker/v/thsrite/library-strm?style=flat
[docker-version-url]: https://hub.docker.com/r/thsrite/library-strm/tags?page=1&ordering=last_updated
[docker-pulls-image]: https://img.shields.io/docker/pulls/thsrite/library-strm?style=flat
[docker-pulls-url]: https://hub.docker.com/r/thsrite/library-strm
[docker-stars-image]: https://img.shields.io/docker/stars/thsrite/library-strm?style=flat
[docker-stars-url]: https://hub.docker.com/r/thsrite/library-strm
[docker-image-size-image]: https://img.shields.io/docker/image-size/thsrite/library-strm?style=flat
[docker-image-size-url]: https://hub.docker.com/r/thsrite/library-strm


```
相关参数
compatibility: fast:性能模式，内部处理系统操作类型选择最优解; compatibility:兼容模式，目录同步性能降低且NAS不能休眠，但可以兼容挂载的远程共享目录如SMB   
source_dir:网盘挂载本地资源路径（监控路径）                                            
dest_dir:strm保存路径（转移路径）                                                    
library_dir:媒体库容器内挂载网盘路径（非strm路径！！意味着要把挂载到网盘的本地路径映射到媒体服务器中）                                                    
cloud_type:cd2/alist
cloud_path:cd2/alist挂载本地跟路径（不带最后的/）
cloud_url:cd2/alist服务地址（ip:port）
copy_img:True/False  是否开启复制图片
create_strm:True/False  是否开启strm链接,否的的话媒体也会复制

支持两种配置方式
公有字段monitoring_mode、source_dir、dest_dir
1.本地模式：library_dir
2.api模式: cloud_type、cloud_path、cloud_url

注：
1.本地模式需要把source_dir挂载到媒体服务器，library_dir为挂载后媒体服务器路径
2.api模式需要正确填写相关配置，目前只支持cd2/alist两种。

优缺点：
1.本地模式读取快，不需要进过api处理。（实际感觉相差不多）
2.api模式优势在于：cd2/alist重启后，媒体服务器必须重启才能识别到cd2/alist挂载本地的路径，但是api不需要！！！
```

```
sync:
  monitor_confs: [
    {
      "monitoring_mode": "compatibility",
      "source_dir": "/mnt/user/downloads/cloud/aliyun/emby",
      "dest_dir": "/mnt/user/downloads/link/aliyun",
      "library_dir": "/cloud/aliyun/emby"
    },
    {
      "monitoring_mode": "compatibility",
      "source_dir": "/mnt/user/downloads/cloud/aliyun/emby",
      "dest_dir": "/mnt/user/downloads/link/aliyun",
      "cloud_type": "cd2",
      "cloud_path": "/mnt/user/downloads/cloud",
      "cloud_url": "192.168.31.103:19798"
    }
  ]

```

```
docker run -d --name library_strm \
    -v /mnt/user/downloads/:/mnt/user/downloads/ \
    -v /mnt/config.yaml:/mnt/config.yaml \
    thsrite/library-strm:latest
```

支持amd、arm

首次全量运行需要进容器执行 python test.py
