#!/bin/sh
set -eu

: "${ENTRA_TENANT_ID:?ENTRA_TENANT_ID must be set in the Container App environment}"
: "${ENTRA_CLIENT_ID:?ENTRA_CLIENT_ID must be set in the Container App environment}"
: "${API_SCOPE:?API_SCOPE must be set in the Container App environment}"

mkdir -p /tmp/client_temp /tmp/proxy_temp /tmp/fastcgi_temp /tmp/uwsgi_temp /tmp/scgi_temp

# Inject Entra settings when the container starts so one image can be promoted
# between environments without rebuilding the frontend bundle.
envsubst '${ENTRA_TENANT_ID} ${ENTRA_CLIENT_ID} ${API_SCOPE}' \
  < /etc/nginx/runtime-config.js.template \
  > /tmp/runtime-config.js

if [ -n "${BACKEND_API_HOST:-}" ]; then
  case "$BACKEND_API_HOST" in
    *://*|*/*|*\:* )
      echo "BACKEND_API_HOST must be a hostname only (no scheme, path, or port)." >&2
      exit 1
      ;;
  esac

  envsubst '${BACKEND_API_HOST}' < /etc/nginx/nginx.conf.template > /tmp/nginx.conf
else
  # Allow the frontend UI to start without a backend proxy. API requests will
  # not be available until BACKEND_API_HOST is configured.
  sed '/^[[:space:]]*location \/api\/[[:space:]]*{/,/^[[:space:]]*}/d' \
    /etc/nginx/nginx.conf.template > /tmp/nginx.conf
  echo "BACKEND_API_HOST is not set; starting frontend without the /api proxy."
fi

nginx -t -c /tmp/nginx.conf
exec nginx -c /tmp/nginx.conf -g 'daemon off;'
