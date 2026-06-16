FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
RUN echo "**** updating packages ****" && \
  echo "deb http://deb.debian.org/debian trixie non-free" >> /etc/apt/sources.list.d/non-free.list && \
  apt update && \
  apt upgrade -y

RUN echo "**** installing runtime packages ****" && \
  apt install -y bash rclone p7zip-full p7zip-rar wget

RUN echo "**** installing chromium and dependencies ****" && \
  apt install -y chromium

COPY . /app

RUN echo "**** fixing permissions ****" && \
  find ./scripts/*.sh -type f -exec chmod +x {} \;

RUN echo "**** installing Python dependencies ****" && \
  pip install .

ENTRYPOINT ["./scripts/entry_point.sh"]

CMD ["it-claws"]