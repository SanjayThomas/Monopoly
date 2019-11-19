FROM node:10 as react-build
WORKDIR /app
COPY . ./
WORKDIR /app/webui
RUN yarn
RUN yarn build
WORKDIR /app/game
RUN yarn
RUN yarn build
VOLUME /app
