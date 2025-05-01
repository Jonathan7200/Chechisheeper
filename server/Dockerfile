FROM node:23-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --production

COPY . .
EXPOSE 3250

CMD ["node", "server.js"]