# Build stage
FROM node:20-alpine AS build
WORKDIR /app

# Copy everything
COPY . .

# Use .env.staging explicitly for React
RUN cp .env.staging .env

# Optional: log contents of env file
RUN echo "Using .env:" && cat .env

RUN npm install

ENV GENERATE_SOURCEMAP=false
ENV DISABLE_ESLINT_PLUGIN=true

RUN npm run build

# Serve stage
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
