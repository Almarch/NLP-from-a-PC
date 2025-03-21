# Pokédex: a local LLM with RAG & UI

The goal of this repo is to play with natural language processing with relatively limited resources. The specs it has been built with are:

- a linux/amd64 platform ;
- with git, docker and python3 ;
- a Nvidia GPU with cuda.

To make use of the later, the [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is needed.

It may work with different specs though but make sure the amount of VRAM + RAM available is soundly higher than the size of the model you intend to use. 

The cluster encompasses a [Open-WebUI](https://github.com/open-webui/open-webui) + [Ollama](https://github.com/ollama/ollama) stack, as well as a [Jupyter Notebook](https://github.com/jupyter/notebook) for experimentation.

## Secure

Generate SSL keys in order to secure all communications:

```sh
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nlp-from-a-pc/services/nginx/ssl/ssl.key -out nlp-from-a-pc/services/nginx/ssl/ssl.crt -subj "/CN=localhost"
```

Also, webUI requires a secret key:

```sh
echo "WEBUI_SECRET_KEY=$(cat /dev/urandom | tr -dc 'A-Za-z0-9' | fold -w 32 | head -n 1)" > nlp-from-a-pc/.env
```

## Deploy

The project is containerized with docker. However, some preliminary steps are required in order to prepare the LLM on the host machine.

```sh
git clone https://github.com/almarch/pokedex
cd NLP-from-a-PC
docker compose build
docker compose up -d
docker ps
```

Pull all required models. The required models are:

- a LLM
- an encoder

If you change the model, adjust `services/myAgent/myAgent/__main__.py` accordingly.

If ollama runs on container `123`:

```sh
docker exec -it 123 bash
ollama pull mistral-nemo:12b-instruct-2407-q8_0
ollama pull bge-m3:567m-fp16
```

## Fill the Vector DB

A Qdrant vector DB is included in the stack. It has been filled as detailed in the `services/jupyter/notebook/pokemons.py`, also accessible from https://localhost:8888/lab/workspaces/auto-n/tree/pokemons.ipynb.

## Tunneling

<img src="https://github.com/user-attachments/assets/86197798-9039-484b-9874-85f529fba932" width="100px" align="right"/>

It is sometimes easier to take a virtual private server (VPS) than obtaining a fixed IP from the Internet provider. We want some services from the gaming machine, let's call it A, to be accessible from anywhere, including from machine C. In the middle, B is the VPS used as a tunnel. 

Name|A  |B  |C  |
---|---|---|---
Description|Gaming machine  |VPS  |Client  |
Role|Host the models  |Host the tunnel  |Plays with NLP  | 
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
