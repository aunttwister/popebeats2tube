# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY . .
RUN npm install && npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
