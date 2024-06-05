# simpleWebServer

This is a simple web server written in Python using the http.server module.

## What does it do?

The server is capable of parsing client requests, and servicing them by rendering HTML to the screen. Should the client provide the address of a directory, an index.html file will be rendered. Should this index.html file not exist, the directory contents are rendered to the screen.

## Want to try it?

You can try out and work on the server by:

1. Cloning the repository
2. Running `python server.py `
3. Making a specific url request @ http://localhost:8080
