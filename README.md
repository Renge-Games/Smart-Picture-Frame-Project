# smart-picture-frame-project

## Install

First, clone the repo.

```sh
pip3 install virtualenv
python3 -m virtualenv venv
source venv/bin/activate
pip3 install -r requirements-pi.txt
```

Also, for the Alexa integration you probably want to set up ngrok.

```sh
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok
ngrok config add-authtoken <token>
```

You get your token from your [account's dashboard](https://dashboard.ngrok.com).

## Usage

```sh
flask run
ngrok http 5000 # or whatever port is used
```