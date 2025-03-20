from .__main__ import QDRANT_HOST, QDRANT_PORT, ENCODER, OLLAMA_URL
from qdrant_client import QdrantClient
import requests

class Agent():
    def __init__(self, body):
        self.input = body

    def process(self):
        return self.input