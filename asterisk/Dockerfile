FROM andrius/asterisk:alpine_glibc-18.1.1
COPY conf/ /
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh && apk add asterisk-curl
WORKDIR /etc/asterisk