FROM python:3.9-slim-buster

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends git openssh-client && \
    rm -rf /var/lib/apt/lists/*


COPY . /app

RUN --mount=type=ssh git submodule update --init --recursive

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python3", "-u", "main.py"]
