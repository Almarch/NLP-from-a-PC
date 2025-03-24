from .__main__ import QDRANT_HOST, QDRANT_PORT, ENCODER, OLLAMA, LLM, ENCODER_WINDOW
from qdrant_client import QdrantClient
import requests

class Agent():
    def __init__(self, body):
        self.body = body
        self.client = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)

    def set_instructions(self, instructions):
        system_message = {
            "role": "system",
            "content": instructions
        }
        self.body["messages"].insert(0, system_message)

    def embed(
        self,
        prompt,
    ):
        response = requests.post(
            OLLAMA + "/api/embeddings",
            json = {
                "model": ENCODER,
                "prompt": prompt,
            }
        )
        return response.json()["embedding"]
    
    def generate(
        self,
        prompt,
        temperature = 0,
    ):
        response = requests.post(
            OLLAMA + "/api/generate",
            json = {
                "model": LLM,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
            }
        )
        return(response.json()["response"])
    
    def summarize(
            self,
            conversation,
            nmax = ENCODER_WINDOW,
    ):
        prompt = f"""
### INSTRUCTIONS

You are an assistant specialized in summarizing conversations.
You receive a conversation as input, and summarize it with
respect to its original language.

The summary must make a special emphasize on the last message.
The goal of the rest of the conversation is to add as much
context as needed to well interpret the last message.

The summary must be at maximum {ENCODER_WINDOW} tokens long.

### CONVERSATION

{conversation}

### SUMMARY

        """

        return self.generate(prompt)


    
