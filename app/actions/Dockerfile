FROM rasa/rasa-sdk:3.5.1

WORKDIR /app

COPY ./requirements-actions.txt requirements.txt
COPY . /app

USER root

RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt && \
    mkdir /.cache && \
    chmod -R 777 /.cache

USER 1001

EXPOSE 5055

ENTRYPOINT ["python", "-m", "rasa_sdk", "--actions", "actions"]
