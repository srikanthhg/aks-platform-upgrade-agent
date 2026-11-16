FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
RUN apk add --no-cache gettext
COPY nginx.conf.template /etc/nginx/nginx.conf.template
COPY runtime-config.js.template /etc/nginx/runtime-config.js.template
COPY docker-entrypoint.sh /usr/local/bin/frontend-entrypoint
COPY --from=build /app/dist /usr/share/nginx/html
RUN chmod 0555 /usr/local/bin/frontend-entrypoint
USER 101
EXPOSE 8080
ENTRYPOINT ["/usr/local/bin/frontend-entrypoint"]
HEALTHCHECK CMD wget -qO- http://127.0.0.1:8080/health || exit 1
