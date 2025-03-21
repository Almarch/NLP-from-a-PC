# <img src="https://github.com/user-attachments/assets/bfe58e17-99f6-4ad7-af1a-ce25b21cbc6a" alt="PoKéDeX" width="50"/> Pokédex: a local LLM with RAG & UI

The goal of this repo is to play with natural language processing with relatively limited resources. The specs it has been built with are:

- a linux/amd64 platform ;
- git and docker ;
- a Nvidia GPU with cuda ;
- at least 32 Go RAM.

To make use of the later, the [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is needed.

It may work with different specs though but make sure the amount of VRAM + RAM available is higher than the size of the model you intend to use. 

![image](https://github.com/user-attachments/assets/807d20ed-1906-40a4-9bcb-11514528cc89)

## Clone locally

Start by cloning the repo:

```sh
git clone https://github.com/almarch/pokedex.git
cd pokedex
```

## Secure

Generate SSL keys in order to secure all communications:

```sh
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout services/nginx/ssl/ssl.key -out services/nginx/ssl/ssl.crt -subj "/CN=localhost"
```

Also, webUI requires a secret key:

```sh
echo "WEBUI_SECRET_KEY=$(cat /dev/urandom | tr -dc 'A-Za-z0-9' | fold -w 32 | head -n 1)" > .env
```

## Deploy

The project is containerized with [docker](https://github.com/docker). However, some preliminary steps are required in order to prepare the LLM on the host machine.

```sh
docker compose pull
docker compose build
docker compose up -d
docker ps
```

## Pull the models

[Ollama](https://github.com/ollama/ollama) is included in the stack. It requires 2 models:
- a LLM
- an encoder

If you change the models, adjust `services/myAgent/myAgent/__main__.py` accordingly.

Pull the models from the Ollama container. If Ollama runs on container `123`:

```sh
docker exec -it 123 bash
ollama pull mistral-nemo:12b-instruct-2407-q8_0
ollama pull bge-m3:567m-fp16
```

## Fill the Vector DB

A [Qdrant](https://github.com/qdrant/qdrant) vector DB is included in the stack.

It must be filled using the [Jupyter Notebook](https://github.com/jupyter/notebook) service, accessible at https://localhost:8888/lab/workspaces/auto-n/tree/pokemons.ipynb.

## Access the WebUI

[Open-WebUI](https://github.com/open-webui/open-webui) is included in the stack.

Reach https://localhost:8080 and parameterize the interface. Deactivate the encoder model, and make the LLM accessible to all users. If needed, make accounts to the family & friend you would like to share the app with.

## Tunneling

<img src="https://github.com/user-attachments/assets/86197798-9039-484b-9874-85f529fba932" width="100px" align="right"/>

Say we need to tunnel the server using a VPS. In other terms, we want some services from the GPU server, let's call it A, to be accessible from anywhere, including from machine C. In the middle, B is the VPS used as a tunnel. 

Name|A  |B  |C  |
---|---|---|---
Description|GPU server  |VPS  |Client  |
Role|Host the services  |Host the tunnel  |Use the Pokédex  | 
User|userA  |userB  | doesn't matter   | 
IP|doesn't matter  |11.22.33.44  | doesn't matter  | 

The services we need are:
- The web UI and the notebook, available at ports 8080 and 8888 respectively.
- A SSH endpoint. Port 22 of the gaming machine (A) will be exposed through port 2222 of the VPS (B).

### From A) the gaming machine
The ports are pushed to the VPS:

```sh
ssh -N -R 8080:localhost:8080 -R 8888:localhost:8888 -R 2222:localhost:22 userB@11.22.33.44
```

### From B) the VPS
The SSH ports 2222 and 443 have to be opened.

```sh
sudo ufw allow 2222
sudo ufw allow 8080
sudo ufw reload
```

### From C) the client
The jupyter notebook is pulled from the VPS:

```sh
ssh -N -L 8888:localhost:8888 userB@11.22.33.44
```

And the VPS is a direct tunnel to the gaming machine A:

```sh
ssh -p 2222 userA@11.22.33.44
```

Note that `userA`, not `userB`, is required for authentication ; idem for the password.

## License

This work is licensed under GPL-2.0.
