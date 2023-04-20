FROM rasa/rasa:3.3.1

WORKDIR /app

USER root

COPY ./models /app/models
COPY ./data /app/data
COPY . /app

RUN rasa train

ENTRYPOINT ["rasa", "run", "-m", "models", "--enable-api", "--cors", "*", "--debug"]
