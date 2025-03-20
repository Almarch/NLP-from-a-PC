from .__main__ import QDRANT_HOST, QDRANT_PORT, ENCODER, OLLAMA, LLM
from qdrant_client import QdrantClient
import requests

class Agent():
    def __init__(self, body):
        self.input = body
        self.client = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)

    def process(self):
        return self.input
    
    def embed(
        self,
        prompt,
    ):
        response = requests.post(
            OLLAMA + "/embeddings",
            json = {
                "model": ENCODER,
                "prompt": prompt,
            }
        )
        return response.json()["embedding"]
    
    def generate_text(
        self,
        prompt,
        temperature = 0,
    ):
        response = requests.post(
            OLLAMA + "/generate",
            json = {
                "model": LLM,
                "prompt": prompt,
                "stream": False,
                "temperature": temperature,
            }
        )
        return(response.json()["response"])