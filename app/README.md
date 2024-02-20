## The Explorer AI web application

The Explorer AI web application has been packaged to run in a network of Docker containers which is configured in 
`docker-compose.yml`. The app's functionality involves interrelated 4 containers/servers:

- The Rasa server, which runs the language model and handles all prediction tasks
- The action server, which runs custom chatbot actions and communicates with the Rasa server
- The web server, which is built from the official Nginx image and serves as a reverse proxy for the Rasa server
- The certbot server, which handles initializtion and automatic renewal of security certificates