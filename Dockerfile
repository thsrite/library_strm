FROM python:3.9-slim
ENV LANG="C.UTF-8" \
    HOME="/alipan_strm" \
    TZ="Asia/Shanghai" \
    PUID=0 \
    PGID=0 \
    UMASK=000
WORKDIR ./alipan_strm
ADD . .
RUN apt-get update \
    && apt-get -y install \
        gosu \
        bash \
        dumb-init \
   && cp -f /alipan_strm/entrypoint /entrypoint \
   && chmod +x /entrypoint \
   && groupadd -r strm -g 911 \
   && useradd -r strm -g strm -d /alipan_strm -s /bin/bash -u 911 \
   && pip install -r requirements.txt

ENTRYPOINT [ "/entrypoint" ]