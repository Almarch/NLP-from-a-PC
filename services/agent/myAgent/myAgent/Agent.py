import requests
from .__main__ import CHROMA_HOST, CHROMA_PORT, ENCODER, OLLAMA_URL

class Agent():
    def __init__(self, body):
        self.input = body

    def process(self):
        return self.input