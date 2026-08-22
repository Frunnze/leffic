FROM node:20-alpine AS builder

WORKDIR /build

COPY package.json tsconfig.json ./
RUN npm install

COPY src ./src
RUN npm run build

FROM nginxinc/nginx-unprivileged:alpine

USER root
RUN apk add --no-cache nginx-module-njs

COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=builder /build/dist/jwt.js /etc/nginx/njs/jwt.js

USER nginx
EXPOSE 8080

CMD ["nginx", "-g", "daemon off;"]
