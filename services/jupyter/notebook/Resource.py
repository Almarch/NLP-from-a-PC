import requests
import io
import os
import pdf2image
import chromadb
import base64

models = {
    "vision": "llama3.2-vision:11b-instruct-q4_K_M",
    "llm": "mistral-nemo:12b-instruct-2407-q4_0",
    "encoder": "snowflake-arctic-embed2:568m-l-fp16",
}

class Resource:
    def __init__(
        self,
        path,
        ollama = "http://ollama:11434/api"
    ):
        self.ollama = ollama
        self.embedded = False
        self.stored = False
        self.name = path
        
        self.name = os.path.splitext(path)[0]
        extension = os.path.splitext(path)[1]
        if extension == ".pdf":
            self.images = pdf2image.convert_from_path(path)
            print(str(len(self.images)) + " pages have been scanned")

        self.extract_content()
        self.synthetize()
        self.store()

    def generate_text(
        self,
        prompt,
        model = models["llm"]
    ):
        response = requests.post(
            self.ollama + "/generate",
            json = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
        )
        return(response.json()["response"])

    def image_analysis(
        self,
        image,
        prompt = "what's in this image?",
        model = models["vision"]
    ):
        tmp = io.BytesIO()
        image.save(tmp, format="JPEG")
        tmp.seek(0)
        tmp = base64.b64encode(tmp.read()).decode("utf-8")
        response = requests.post(
            self.ollama + "/chat",
            json = {
                "model": model,
                "messages": [
                    {
                      "role": "user",
                      "content": prompt,
                      "images": [str(tmp)],
                    }
                  ],
                "stream": False
            }
        )
        return(response.json()["message"]["content"])

    def extract_content(self):
        self.full_text = ""
        for image in self.images:
            self.full_text += self.image_analysis(
                image = image,
                prompt = """
Extrait l'ensemble du texte de ces images.
Ne rajoute pas de commentaire ni de caractère spéciaux.
Ne traduis pas le texte.
"""
            )

    def describe_content(self):
        self.full_description = ""
        for i, image in enumerate(self.images):
            self.full_description += "\n#Page " + str(i) + "\n" + self.image_analysis(
                image = image,
                prompt = """
Synthétise le contenu de cette image en Français.
"""
            )

    def synthetize(
        self,
        max_words = 2000
    ):
        self.describe_content()
        self.synthese = self.generate_text(
            prompt = """
Tu es un assistant spécialisé dans la synthèse de texte.
Un texte t'es confié et tu en réalises la synthèse.
La synthèse doit être en français.
La synthèse doit mentionner l'intention de l'auteur ainsi que les éléments les plus répétitifs.
La synthèse doit faire maximum """ + str(max_words) + """ caractères.

###

Voici le texte:
""" + self.full_description
        )

    def embed(
        self,
        prompt,
        model = models["encoder"]
    ):
        response = requests.post(
            self.ollama + "/embeddings",
            json = {
                "model": "snowflake-arctic-embed2:568m-l-fp16",
                "prompt": prompt,
            }
        )
        return response.json()["embedding"]

    def embed_whole(
        self
    ):
        json = {
            "resource": self.name,
            "text": self.full_text,
            "synthese": self.synthese,
        }
        vector = self.embed(self.synthese)
        return json, vector

    def store(
        self,
        collection = "rag",
        host = "chroma",
        port = 8000
    ):
        json, vector = self.embed_whole()
        
        client = chromadb.HttpClient(host = host, port = port)
        collection = client.get_or_create_collection(name = collection)
        collection.add(
            ids = self.name,
            embeddings = vector,
            metadatas = json
        )
        print("Stored in the database")
