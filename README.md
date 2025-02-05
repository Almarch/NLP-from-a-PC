# hello

<p align="center"><img src="https://github.com/user-attachments/assets/b12cbef1-98a9-4b79-bca0-fa1f21cb6f0e" width="300px"/></p>

The goal of this repo is to run a light-weighted LLM on a gaming computer.

## Launch with docker

<img src="https://upload.wikimedia.org/wikipedia/commons/e/ea/Docker_%28container_engine%29_logo_%28cropped%29.png" width="120px" align="right"/>

The project is containerized.

```sh
git clone https://github.com/Almarch/hello
cd hello
docker compose build
docker compose up
```

Cuda is highly recommanded for performance. [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is needed.

## LLM

<img src="https://upload.wikimedia.org/wikipedia/commons/e/ec/DeepSeek_logo.svg" width="300px" align="right"/>

The LLM is pulled from hugging face. A [frugal deepseek model](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B) has been picked.

## Tunneling

<img src="https://github.com/user-attachments/assets/86197798-9039-484b-9874-85f529fba932" width="100px" align="right"/>

It is sometimes cheaper to pay for a virtual private server (VPS) than suscribing a fixed IP to the Internet provider. We want some services from the gaming machine, let's call it A, to be accessible from anywhere, including from machine C. In the middle, B is the VPS used as a tunnel. 

Name|A  |B  |C  |
---|---|---|---
Description|Gaming machine  |VPS  |Client  |
Role|Host the LLM  |Host the tunnel  |Plays around  | 
User|userA  |userB  | doesn't matter   | 
IP|doesn't matter  |11.22.33.44  | doesn't matter  | 

The services we need are:
- A jupyter notebook. It will be exposed at port 8888.
- An API endpoint. It will be exposed at port 7777.
- A SSH endpoint. Port 22 of the gaming machine (A) will be exposed through port 2222 of the VPS (B).

### From A) the gaming machine
The ports are pushed to the VPS:

```sh
ssh -N -R 8888:localhost:8888 -R 7777:localhost:7777 -R 2222:localhost:22 userB@11.22.33.44
```

### From B) the VPS
The appropriate ports are opened:

```sh
sudo ufw allow 2222
sudo ufw allow 7777
sudo ufw allow 8888
sudo ufw reload
```

### From C) the client
The jupyter notebook and the API ports are pulled from the VPS:

```sh
ssh -N -L 8888:localhost:8888 -L 7777:localhost:7777  userB@11.22.33.44
```

To connect to A directly with SSH:

```sh
ssh -p 2222 userA@11.22.33.44
```

Note that `userA`, not `userB`, is required for authentication.



