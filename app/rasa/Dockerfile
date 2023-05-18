FROM rasa/rasa:3.5.6-spacy-en

WORKDIR /app

USER root

COPY ./data /app/data
COPY . /app

RUN pip install -U --no-cache-dir pip setuptools wheel && \
    pip install -U spacy && \
    python -m spacy download en_core_web_md && \
    rasa train

ENTRYPOINT ["rasa", "run", "-m", "models", "--enable-api", "--cors", "*", "--debug"]
