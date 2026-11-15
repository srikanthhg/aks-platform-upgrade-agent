#!/bin/sh
set -eu

: "${BACKEND_API_HOST:?BACKEND_API_HOST must be set to the internal backend Container App FQDN}"
: "${ENTRA_TENANT_ID:?ENTRA_TENANT_ID must be set in the Container App environment}"
: "${ENTRA_CLIENT_ID:?ENTRA_CLIENT_ID must be set in the Container App environment}"
: "${API_SCOPE:?API_SCOPE must be set in the Container App environment}"

case "$BACKEND_API_HOST" in
  *://*|*/*|*\:* )
    echo "BACKEND_API_HOST must be a hostname only (no scheme, path, or port)." >&2
    exit 1
    ;;
esac

mkdir -p /tmp/client_temp /tmp/proxy_temp /tmp/fastcgi_temp /tmp/uwsgi_temp /tmp/scgi_temp

# Inject Entra settings when the container starts so one image can be promoted
# between environments without rebuilding the frontend bundle.
envsubst '${ENTRA_TENANT_ID} ${ENTRA_CLIENT_ID} ${API_SCOPE}' \
  < /etc/nginx/runtime-config.js.template \
  > /usr/share/nginx/html/runtime-config.js

envsubst '${BACKEND_API_HOST}' < /etc/nginx/nginx.conf.template > /tmp/nginx.conf
nginx -t -c /tmp/nginx.conf
exec nginx -c /tmp/nginx.conf -g 'daemon off;'
