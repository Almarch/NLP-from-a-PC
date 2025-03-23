# <img src="https://github.com/user-attachments/assets/bfe58e17-99f6-4ad7-af1a-ce25b21cbc6a" alt="PoKéDeX" width="50"/> Pokédex: AI assistant to a world of dreams and adventures

The goal of this package is to provide an AI assistant to the world of Pokémon.

It consists in a stack of services, listed in the `docker-compose.yml` file.

Basically, it encompasses an UI and an inference service. A custom agentic proxy intercepts the requests between these services, processes them, and eventually augments them from information from a vector DB.

The models have been selected with respect to their minimalism, performance and multilingualism.

The project has been set-up such as French <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Flag_of_France.svg" alt="fr" width="20"/> is the privileged language of the AI assistant.

![Picture1](https://github.com/user-attachments/assets/d3b2aea5-9b25-4bcd-9c53-92093d1b450a)

This project can also be seen as a natural language processing exercice with relatively limited resources, _i.e._ a gaming computer. The specs it has been built with are:

- a linux/amd64 platform ;
- git and docker ;
- 32 Go RAM ;
- a Nvidia GPU (12 Go VRAM) with cuda.

To make use of the later, the [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is needed.

## ⏬ Clone locally

Start by cloning the repo:

```sh
git clone https://github.com/almarch/pokedex.git
cd pokedex
```

## 🔐 Secure

The project uses [nginx](https://github.com/nginx/nginx) as a reverse proxy.

Server-client transactions are encrypted using SSL keys. For more security, use a domain name and a CA certificate.

Generate the SSL keys:

```sh
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout services/nginx/ssl/ssl.key -out services/nginx/ssl/ssl.crt -subj "/CN=localhost"
```

Also, the UI service requires a secret key:

```sh
echo "WEBUI_SECRET_KEY=$(cat /dev/urandom | tr -dc 'A-Za-z0-9' | fold -w 32 | head -n 1)" > .env
```

## 🚀 Launch

The project is containerized with [docker](https://github.com/docker).

Pull, build & launch all services with compose :

```sh
docker compose pull
docker compose build
docker compose up -d
docker ps
```

## 🦙 Pull the models

[Ollama](https://github.com/ollama/ollama) is included in the stack.

It requires 2 models:
- a LLM. By default, [Mistral-Nemo](https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407) is selected.
- an encoder. By default, [BGE-M3](https://huggingface.co/BAAI/bge-m3) is selected.

If you change the models, adjust `services/myAgent/myAgent/__main__.py` accordingly.

Pull the models from the Ollama container. If Ollama runs on container `123`:

```sh
docker exec -it 123 bash
ollama pull mistral-nemo:12b-instruct-2407-q8_0
ollama pull bge-m3:567m-fp16
```

## 🧩 Fill the Vector DB

A [Qdrant](https://github.com/qdrant/qdrant) vector DB is included in the stack.

It must be filled using the [Jupyter Notebook](https://github.com/jupyter/notebook) service, accessible at https://localhost:8888/lab/workspaces/auto-n/tree/pokemons.ipynb.

## 🎮 Access the WebUI

[Open-WebUI](https://github.com/open-webui/open-webui) is included in the stack.

Reach https://localhost:8080 and parameterize the interface. Deactivate the encoder model, and make the LLM accessible to all users. If needed, make accounts to the family & friends you would like to share the app with.

## 🔀 Adaptation to other projects

This framework can readily adapt to other agentic projects.

- The data base should be filled with relevant collections.
- The custom agentic logics is centralised in `services/agent/MyAgent/MyAgent/MyAgent.py`.

## 🕳️ Tunneling

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
The SSH ports 2222 and 8080 have to be opened.

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
