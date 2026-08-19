FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install --no-audit --no-fund
COPY . .
ARG VITE_ENTRA_TENANT_ID
ARG VITE_ENTRA_CLIENT_ID
ARG VITE_API_SCOPE
ARG VITE_API_BASE_URL
ENV VITE_ENTRA_TENANT_ID=$VITE_ENTRA_TENANT_ID VITE_ENTRA_CLIENT_ID=$VITE_ENTRA_CLIENT_ID VITE_API_SCOPE=$VITE_API_SCOPE VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build
FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist /usr/share/nginx/html
USER 101
EXPOSE 8080
HEALTHCHECK CMD wget -qO- http://127.0.0.1:8080/health || exit 1
