FROM rasa/rasa:3.5.6-spacy-en

WORKDIR /app

USER root

COPY ./data /app/data
COPY . /app

RUN rasa train

ENTRYPOINT ["rasa", "run", "-m", "models", "--enable-api", "--cors", "*", "--debug"]
