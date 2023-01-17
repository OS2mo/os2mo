FROM cethy/alpine-supercronic:v1.0
RUN apk add --no-cache curl jq
COPY ./import_all.sh /app/
RUN chmod -R 100 "/app/"
ENTRYPOINT ["supercronic", "/etc/crontab"]
