import requests
import chromadb
from .__main__ import CHROMA_HOST, CHROMA_PORT, ENCODER, OLLAMA_URL

class Agent():
    def __init__(self, body):
        self.input = body
        self.client = chromadb.HttpClient(host = CHROMA_HOST, port = CHROMA_PORT)

    def process(self):

        last_msg = self.input["messages"][-1:][0]["content"]
        
        response = requests.post(
            OLLAMA_URL + "/api/embeddings",
            json={"model": ENCODER, "prompt": last_msg}
        )

        query_vector = response.json()["embedding"]
        collection = self.client.get_collection(name="pokemon")
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=3,
        )

        rag = [results["metadatas"][0][i] for i in range(len(results["ids"][0]))]

        body = self.input

        body["messages"][-1:][0]["content"] = f"""

Tu es un assistant spécialisé
dans la description de pokémons.
L'utilisateur te poses une question,
et tu disposes d'information afin de
l'aider le mieux possible.

###

Information:

```
{rag}
```

###

Question de l'utilisateur:

{last_msg}
"""
        return body
