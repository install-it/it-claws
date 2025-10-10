FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

RUN echo "**** updating packages ****" && \
  echo "deb http://deb.debian.org/debian trixie non-free" >> /etc/apt/sources.list.d/non-free.list && \
  apt update && \
  apt upgrade -y

RUN echo "**** installing runtime packages ****" && \
  apt install -y bash rclone p7zip-full p7zip-rar wget
    
RUN echo "**** installing firefox ****" && \
  wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | tee /etc/apt/keyrings/packages.mozilla.org.asc && \
    echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null && \
    apt update && \
    apt install -y firefox

COPY . /app

RUN echo "**** fixing permission ****" && \ 
  find ./scripts/*.sh -type f -exec chmod +x {} \;

RUN echo "**** installing Python dependencies ****" && \
  python3 -m pip install -r ./requirements.txt

ENTRYPOINT ["./scripts/entry_point.sh"]

CMD ["python", "src/main.py"]