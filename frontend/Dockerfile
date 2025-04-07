FROM node:20-alpine AS build
WORKDIR /app

COPY . .

RUN cp .env.staging .env
RUN echo "Using .env:" && cat .env

RUN npm install

ENV GENERATE_SOURCEMAP=false
ENV DISABLE_ESLINT_PLUGIN=true

RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
