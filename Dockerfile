FROM python:3.13-alpine3.22

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN echo "**** updating packages ****" && \
  apk update && \
  apk upgrade

RUN echo "**** installing runtime packages ****" && \
    apk add bash rclone 7zip firefox

COPY . /app

RUN echo "**** fixing permission ****" && \ 
  find ./scripts/*.sh -type f -exec chmod +x {} \;

RUN echo "**** installing Python dependencies ****" && \
    python3 -m pip install -r ./requirements.txt

ENTRYPOINT ["./scripts/entry_point.sh"]

CMD ["python", "src/main.py"]