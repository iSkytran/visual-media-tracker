FROM node:alpine as install
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./

FROM install as build
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
