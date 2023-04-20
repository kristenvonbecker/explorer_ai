FROM rasa/rasa-sdk:3.3.0

WORKDIR /app

COPY ./requirements-actions.txt requirements.txt
COPY . /app

USER root

RUN pip install --no-cache-dir -r requirements.txt

USER 1001

EXPOSE 5055

ENTRYPOINT ["python", "-m", "rasa_sdk", "--actions", "actions"]
