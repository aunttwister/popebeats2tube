# Use node for building frontend
FROM node:18 AS build

# Set working directory
WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy all files
COPY . .

# Build the React app with the correct environment variables
ARG REACT_APP_API_BASE_URL
ARG REACT_APP_GOOGLE_CLIENT_ID
ENV REACT_APP_API_BASE_URL=http://localhost:4011/api
ENV REACT_APP_GOOGLE_CLIENT_ID=299795794182-g4po9fe003o5ducp1jkn588tdcsdbmaa.apps.googleusercontent.com

RUN npm run build

# Use Nginx to serve static files
FROM nginx:latest AS production
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
