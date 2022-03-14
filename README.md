# Flask-Redis HyperChat

## What
A primitive chat app using Flask and Redis pub-sub.

## Task Definition:
We will make a chat application but in a more sophisticated way.
In this application, each server is a chat participant and they communicate with each other through a messaging server( Redis ).
Each server is a flask/django/barebone application written in python.
We can make as many servers as we want using docker.
To test, each server opens a web service through which we can see a list of servers and chat with them.
So, a server may be at localhost:8000, another at localhost: 8001.
There is no direct connection between them. They all know about the messaging server only.


## Running
Run the follow command (you need Docker installed):

`chmod +x run.sh`
then
`./run.sh`

Go to `http://localhost:<port_num>`




License: (LICENSE)
