# Run a LLM with RAG from a Gaming PC

The goal of this repo is to play with natural language processing with relatively limited resources.

## 0. Set-up with Docker

<img src="https://github.com/user-attachments/assets/b12cbef1-98a9-4b79-bca0-fa1f21cb6f0e" width="200px" align="right"/>

The project is containerized with docker.

```sh
git clone https://github.com/Almarch/NLP-from-a-PC
cd NLP-from-a-PC
docker compose build
docker compose up
```

Cuda is highly recommanded for performance. [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is needed.

## 1. Services

The project contains several services:
- An Ollama,
- An Open-Webui,
- A Weaviate database

## 1. Large language model

<img src="https://github.com/user-attachments/assets/7847f4c8-b8d7-483a-aa43-c00241c15891" width="200px" align="right"/>

The idea is to run the LLM locally. In order to download and set up the LLM on the Ollama environment, the following steps should be done from the host machine. The host python3 requires:
- `torch`
- `transformers`
- `accelerate`

Use a `venv` if you don't want to mess with your system python. From python3:

```py
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig
import torch
import os

author = "deepseek-ai"
model_name = "DeepSeek-R1-Distill-Llama-8B"

tokenizer = AutoTokenizer.from_pretrained(
    author + "/" + model_name,
    cache_dir="./services/ollama/cache"
)
model = AutoModelForCausalLM.from_pretrained(
    author + "/" + model_name,
    cache_dir="./services/ollama/cache",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
generation_config = GenerationConfig.from_pretrained(
    author + "/" + model_name,
    cache_dir="./services/ollama/cache",
)
generation_config.pad_token_id = model.generation_config.eos_token_id

# Save to disk
os.makedirs("./services/ollama/data/models/" + model_name, exist_ok=True)
tokenizer.save_pretrained("./services/ollama/data/models/" + model_name)
model.save_pretrained("./services/ollama/data/models/" + model_name)
generation_config.save_pretrained("./services/ollama/data/models/" + model_name)
```

Then we will convert the Hugging face model to Ollama using the `llama.cpp` docker image:

```sh
docker run --rm -v "./services/ollama/data/models:/models" \
    ghcr.io/ggerganov/llama.cpp:full \
    --convert --outtype f16 "/models/DeepSeek-R1-Distill-Llama-8B"
```

Create a model file:

```sh
echo "FROM /root/.ollama/models/DeepSeek-R1-Distill-Llama-8B/DeepSeek-R1-Distill-Llama-8B-F16.gguf" > ./services/ollama/data/models/DeepSeek-R1-Distill-Llama-8B/.Modelfile
```

Once the model is converted, it must be registered to Ollama. Access the running Ollama container, say #123:

```sh
docker compose up -d
docker ps
docker exec -it 123 bash
```

And register the model:
```sh
ollama create calpaca -f /root/.ollama/models/DeepSeek-R1-Distill-Llama-8B/.Modelfile
```

A [frugal deepseek model](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B) has been picked but it may be changed for any other model.

NB:
- The `{"role": "system", "content":...}` instructions do not work well. See the [doc](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B#usage-recommendations).
- As far as I understand the `attention_mask` error message should be disregarded as explained in [this thread](https://stackoverflow.com/questions/69609401/suppress-huggingface-logging-warning-setting-pad-token-id-to-eos-token-id).

## Vector data base

A [vector data base](https://weaviate.io/blog/what-is-a-vector-database) is included in the cluster.

In order to feed the data base from raw pdf, 4 models are needed:

<p align="center"><img src="https://github.com/user-attachments/assets/4109c7b2-29b7-4c53-9b3c-753a96ec39f0" width="900px"/></p>

A python class `/services/jupyter/notebook/Resource.py` (will) encompasses all these steps and the appropriate API call to the models services in order to help integrating resources to the vector data base.

### 1.2. OCR

The OCR service is [tesseract](https://tesseract-ocr.github.io/tessdoc/). It accepts any of the following languages:

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
<br>

It has shown limitations, for instance this resource could not be processed: [this resource](https://pubmed.ncbi.nlm.nih.gov/6342763/).

### 1.3. Tokenizer

The tokenizers are the transformer models from [spaCy](https://spacy.io/models/). There are 3 models, one for each of these language (the language should therefore be thoroughly mentionned in the API call):

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
<br>

### 1.4. Encoder

The encoder model is [this one](https://huggingface.co/sentence-transformers/all-mpnet-base-v2). It takes as input up to 384 words, and yields vectors of size 768. It has been tuned using cosine similarity. It is primarily designed for English:

<div align="center">
<div style="
    display: flex;
    flex-direction: row;
    justify-content: space-around;
    margin: auto;
">
    <img src="https://upload.wikimedia.org/wikipedia/commons/8/83/Flag_of_the_United_Kingdom_%283-5%29.svg" alt="en"  width="40px">
</div>
</div>
<br>

Hence the need for a translation, in order to avoid a language bias at this pivotal step.

## 2. Tunneling

<img src="https://github.com/user-attachments/assets/86197798-9039-484b-9874-85f529fba932" width="100px" align="right"/>

It is sometimes easier to take a virtual private server (VPS) than obtaining a fixed IP from the Internet provider. We want some services from the gaming machine, let's call it A, to be accessible from anywhere, including from machine C. In the middle, B is the VPS used as a tunnel. 

Name|A  |B  |C  |
---|---|---|---
Description|Gaming machine  |VPS  |Client  |
Role|Host the models  |Host the tunnel  |Plays with NLP  | 
User|userA  |userB  | doesn't matter   | 
IP|doesn't matter  |11.22.33.44  | doesn't matter  | 

The services we need are:
- A jupyter notebook. It will be exposed at port 8888.
- Open-webui, that will be exposed at port 8080.
- Ollama, that will be exposed at port 7777.
- A SSH endpoint. Port 22 of the gaming machine (A) will be exposed through port 2222 of the VPS (B).

### From A) the gaming machine
The ports are pushed to the VPS:

```sh
ssh -N -R 8888:localhost:8888 -R 8080:localhost:8080 -R 7777:localhost:7777 -R 2222:localhost:22 userB@11.22.33.44
```

### From B) the VPS
The SSH port 2222 has to be opened.

```sh
sudo ufw allow 2222
sudo ufw reload
```

Be careful not to open 8888 or the jupyter notebook would be made public.

### From C) the client
The jupyter notebook is pulled from the VPS:

```sh
ssh -N -L 8888:localhost:8888 -L 8080:localhost:8080 -L 7777:localhost:7777  userB@11.22.33.44
```

And the VPS is a direct tunnel to the gaming machine A:

```sh
ssh -p 2222 userA@11.22.33.44
```

Note that `userA`, not `userB`, is required for authentication ; idem for the password.



