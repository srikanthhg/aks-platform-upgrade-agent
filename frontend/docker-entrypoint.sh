#!/bin/sh
set -eu

: "${BACKEND_API_HOST:?BACKEND_API_HOST must be set to the internal backend Container App FQDN}"

case "$BACKEND_API_HOST" in
  *://*|*/*|*\:* )
    echo "BACKEND_API_HOST must be a hostname only (no scheme, path, or port)." >&2
    exit 1
    ;;
esac

mkdir -p /tmp/client_temp /tmp/proxy_temp /tmp/fastcgi_temp /tmp/uwsgi_temp /tmp/scgi_temp

envsubst '${BACKEND_API_HOST}' < /etc/nginx/nginx.conf.template > /tmp/nginx.conf
nginx -t -c /tmp/nginx.conf
exec nginx -c /tmp/nginx.conf -g 'daemon off;'
