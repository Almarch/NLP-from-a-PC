# Run a LLM with RAG from a Gaming PC

The goal of this repo is to play with natural language processing with relatively limited resources. The specs it has been built with are:

- a linux/amd64 platform ;
- with git, docker and python3 ;
- a Nvidia GPU with cuda.

To make use of the later, the [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is needed.

It may work with different specs though but make sure the amount of VRAM + RAM available is soundly higher than the size of the model you intend to use. 

The cluster encompasses a [Open-WebUI](https://github.com/open-webui/open-webui) + [Ollama](https://github.com/ollama/ollama) stack, as well as a [Jupyter Notebook](https://github.com/jupyter/notebook) for experimentation.

🚧 Next step: connect WebUI database with the dedicated chromaDB service ([work in progress](https://github.com/Almarch/NLP-from-a-PC/tree/feature/1db2rule_them_all)) in order to efficiently set up the RAG pipeline

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

<img src="https://github.com/user-attachments/assets/b12cbef1-98a9-4b79-bca0-fa1f21cb6f0e" width="200px" align="right"/>

The project is containerized with docker. However, some preliminary steps are required in order to prepare the LLM on the host machine.

```sh
git clone https://github.com/Almarch/NLP-from-a-PC
cd NLP-from-a-PC
docker compose build
docker compose up -d
docker ps
```

 <img src="https://github.com/user-attachments/assets/7847f4c8-b8d7-483a-aa43-c00241c15891" width="200px" align="right"/>
 
A [frugal deepseek model](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Llama-8B) has been picked for illustration. Access the running Ollama container, say number `123`:

```sh
docker exec -it 123 bash
ollama pull deepseek-r1:8b
```

See the [Ollama collections](https://ollama.com/library/).

## Fill the Vector DB

A Chroma vector DB is included in the stack. In order to fill it from PDFs, the following pipeline is under development (`./services/jupyter/notebook/Resource.py`):

![image](https://github.com/user-attachments/assets/114170ad-4b05-4216-9de2-0f3c80e21660)

### OCR

PDFs are imported as images and read using [py](https://github.com/madmaze/pytesseract)-[tesseract](https://github.com/tesseract-ocr/tesseract).

It works for some resources, though it sometimes include typos. However it completely fails reading [this paper](https://pubmed.ncbi.nlm.nih.gov/6342763/).

### Text splitting

Text splitting is done with an arbitrary rule of 1000 words per chunk - 100 words overlap, which is the default configuration in the WebUI RAG pipeline using the [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) encoder. Using a different encoder, the chunks size should be adjusted.

Roughly half of the chunks reach the maximum number of tokens with this configuration as experimented in `./services/jupyter/notebook/fill_chroma.ipynb` :

 <p align="center"><img src="https://github.com/user-attachments/assets/260803a5-bd48-4395-a477-ed42ed6e48ec" width="600px"/></p>

### Language detection & translation

Most free encoders are language-specific as clearly stated in their documentation and further experimented in `./services/jupyter/notebook/encoding.ipynb` with [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) :

 <p align="center"><img src="https://github.com/user-attachments/assets/46b8ef39-98fe-441f-87f0-4b2ba368985d" width="600px"/></p>
 
"Les chiens sont fidèles" is an exact translations of "Dogs are loyal". I also checked [all-mpnet-base-v2](https://huggingface.co/sentence-transformers/all-mpnet-base-v2) with a similar result.

The approach I explored was to use the LLM to detect the language, then to perform the translation. Using [Mistral 7b](https://mistral.ai/en/news/announcing-mistral-7b), the translations were pretty good but the language detection was difficult to industrialize. My prompts (`./services/jupyter/notebook/prompts.py`) may very likely be improved, and they may be post-processed further as well.

Noteworthily, my limited resources make the translation step extremely long.

### Encoding

We already mentioned the importance of the encoder especially with regards to:
- its language, raising the need for translation ;
- its number of input token, that impacts the chunks size.

Let's add to the list:
- its number of output, <i>i.e.</i> the embedding vector size: longer vectors carry more informance hence allow more nuance ;
- its relevance for the topic.

Especially, for this last point, an encoder destined to a very specific topic should be considered for fine-tuning. Otherwise, only a very limited fraction of the embedding space would be actually occupied by the topic resources, making it difficult to sort and associate them efficiently. Fine-tuning the encoder is an order of magnitude easier than fine-tuning the LLM itself.

For a French RAG project, I keep that one in my back pocket:

<p align="center">
 <a href="https://huggingface.co/Lajavaness/sentence-camembert-large">
    <img src="https://www.lesfromagivores.com/img/fromages/camembertdenormandie.png" width="200px"/>
</a>

### ChromaDB

The next step will be to use the ChromaDB in a RAG pipeline from Open-WebUI.

## That's all

Onced launched with docker, the WebUI is available at http://localhost:8080 and the Jupyter Notebook at http://localhost:8000 .

Resource consumptions may be followed-up with:

```
nvtop
```

for the VRAM and GPU; and:

```
htop
```

for the RAM and CPU.

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

## Other branches

There are several branches in this repo, corresponding to exploratory steps.

- in [laptop](https://github.com/Almarch/NLP-from-a-PC/tree/laptop) I attempted to run [deepseek-llm-7b-chat](https://huggingface.co/deepseek-ai/deepseek-llm-7b-chat) from HF on a laptop. It actually "worked", with about 5 minutes / token.
- with [fastapi_everywhere](https://github.com/Almarch/NLP-from-a-PC/tree/fastapi_everywhere), I downloaded all models (LLM, OCR, encoder) into a distinct service with a fastAPI. It still used HF for the LLM.
- I switched to Ollama-WebUI framework from [from_hugging_face](https://github.com/Almarch/NLP-from-a-PC/tree/from_hugging_face). In this branch, I still download a HF model and convert it to Ollama, which was unnecessarily complicated.
