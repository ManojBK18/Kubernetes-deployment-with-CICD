FROM node:20-alpine as BUILD
WORKDIR /app
COPY package.json .
RUN npm install 
COPY . .
RUN npm run build

FROM nginx:latest 
WORKDIR /app
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=BUILD /app/dist /app
EXPOSE 80