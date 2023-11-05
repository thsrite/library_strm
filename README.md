# 支持多路径目录监控配置

```
compatibility:                                                                  
    fast:性能模式，内部处理系统操作类型选择最优解;                                       
    compatibility:兼容模式，目录同步性能降低且NAS不能休眠，但可以兼容挂载的远程共享目录如SMB   
source_dir:网盘挂载本地资源路径（监控路径）                                            
dest_dir:strm保存路径（转移路径）                                                    
library_dir:媒体库容器内挂载网盘路径（非strm路径！！意味着要把挂载到网盘的本地路径映射到媒体服务器中）                                                    
cloud_type:cd2/alist
cloud_path:cd2/alist挂载本地跟路径（不带最后的/）
cloud_url:cd2/alist服务地址（ip:port）
copy_img:True/False  是否开启复制图片
create_strm:True/False  是否开启strm链接,否的的话媒体也会复制
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

启动服务等一会再……

阿里云盘创建文件后，容器内监测有点延迟
