FROM node:4-slim as builder

MAINTAINER cmoesgaard

WORKDIR /app

ADD . /app

RUN npm install

RUN npm run grunt

FROM python:3.6-slim

WORKDIR /app

COPY --from=builder /app .

EXPOSE 5000

CMD ["./manage.py", "run", "--host=0.0.0.0"]
