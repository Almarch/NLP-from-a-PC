# Run a LLM with RAG from a Gaming PC

The goal of this repo is to play with natural language processing with relatively limited resources.

## 0. Launch with Docker

<img src="https://github.com/user-attachments/assets/b12cbef1-98a9-4b79-bca0-fa1f21cb6f0e" width="200px" align="right"/>

The project is containerized with docker.

```sh
git clone https://github.com/Almarch/hello
cd hello
docker compose build
docker compose up
```

Cuda is highly recommanded for performance. [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is needed.

## 1. Services

The project contains several services and models, and strictly follows the philosophy: 1 model = 1 service. Some services aren't models though.

A vector data base is available in order to extract relevant context from specific fields.

A Jupyter Notebook is also here for development purposes.

## 2. LLM

<img src="https://github.com/user-attachments/assets/7847f4c8-b8d7-483a-aa43-c00241c15891" width="200px" align="right"/>

The LLM is pulled from hugging face. A [frugal deepseek model](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B) has been picked.

NB:
- The {"system": ...} instructions do not work well. See the [doc](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B#usage-recommendations).
- The attention mask error message should be disregarded, as explained in [this thread](https://stackoverflow.com/questions/69609401/suppress-huggingface-logging-warning-setting-pad-token-id-to-eos-token-id).

## 3. Vector data base

A [vector data base](https://weaviate.io/blog/what-is-a-vector-database) is included in the cluster.

In order to feed the data base from raw pdf, 3 models are needed:

<p align="center"><img src="https://github.com/user-attachments/assets/ff1ba80f-fb1d-44e3-a95c-abd6074b4845" width="900px"/></p>

A python class `/services/jupyter/notebook/Resource.py` encompasses all these steps and the appropriate API call to the models services in order to help integrating resources to the vector data base. The OCR and the tokenizer have been picked for the following languages:

<div align="center">
<div style="
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    margin: auto;
">
    <img src="https://upload.wikimedia.org/wikipedia/commons/8/83/Flag_of_the_United_Kingdom_%283-5%29.svg" alt="en"  width="40px">
    <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Flag_of_France.svg" alt="fr"  width="40px">
    <img src="https://upload.wikimedia.org/wikipedia/commons/9/9a/Flag_of_Spain.svg" alt="es"  width="40px">
</div>
</div>

## 4. OCR

The OCR service is [tesseract](https://tesseract-ocr.github.io/tessdoc/).

## 4. Tokenizer

The tokenizers are the transformer models from [spaCy](https://spacy.io/models/).

## 5. Encoder

The encoder model is [this one](https://huggingface.co/sentence-transformers/all-mpnet-base-v2). It takes as input up to 384 words, and yields vectors of size 768.

## 6. Tunneling

<img src="https://github.com/user-attachments/assets/86197798-9039-484b-9874-85f529fba932" width="100px" align="right"/>

It is sometimes easier to take a virtual private server (VPS) than obtaining a fixed IP from the Internet provider. We want some services from the gaming machine, let's call it A, to be accessible from anywhere, including from machine C. In the middle, B is the VPS used as a tunnel. 

Name|A  |B  |C  |
---|---|---|---
Description|Gaming machine  |VPS  |Client  |
Role|Host the LLM  |Host the tunnel  |Plays around  | 
User|userA  |userB  | doesn't matter   | 
IP|doesn't matter  |11.22.33.44  | 55.66.77.88  | 

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
The SSH port 2222 has to be opened. Say we want the API to be reachable from a specific IP.

```sh
sudo ufw allow 2222
sudo ufw allow from 55.66.77.88 to any port 7777
sudo ufw reload
```

Be careful not to open 8888 or the jupyter notebook would be made public.

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



