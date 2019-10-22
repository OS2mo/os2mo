FROM testcafe/testcafe:1.5.0

USER root

RUN apk --no-cache add ffmpeg
ENV NODE_PATH=:/usr/lib/node_modules:/usr/lib/node_modules/testcafe/node_modules
RUN npm install -g testcafe-vue-selectors axios

COPY .testcaferc.json .testcaferc.json

USER user
ENV FFMPEG_PATH=/usr/bin/ffmpeg
