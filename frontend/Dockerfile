FROM node:23.11.0-slim

WORKDIR /app
COPY . /app

RUN npm install
RUN npm run build

CMD ["npm", "start"]
