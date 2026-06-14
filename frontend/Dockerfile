FROM node:20-alpine AS build
WORKDIR /app
COPY package.json .
RUN npm install 
COPY . .
RUN npm run build

FROM nginx:latest 
WORKDIR /app
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /app
EXPOSE 80