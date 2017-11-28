FROM haproxy:1.7-alpine
COPY haproxy.cfg url-whitelist.lst long-requests-whitelist.lst /usr/local/etc/haproxy/

HEALTHCHECK --interval=5m --timeout=2s \
  CMD ls /safe-socket/docker.sock

