from .__main__ import QDRANT_HOST, QDRANT_PORT, ENCODER, OLLAMA, LLM
from qdrant_client import QdrantClient
import requests

class Agent():
    def __init__(self, body):
        self.body = body
        self.last_message = body["messages"][-1]["content"]
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
    
