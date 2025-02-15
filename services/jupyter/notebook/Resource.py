import requests
import io
import os
import pdf2image
import pytesseract
from sentence_transformers import SentenceTransformer
import chromadb
import uuid
import random
from prompts import is_english,to_english

class Resource:
    def __init__(self,path):
        
        self.translated = False
        self.embedded = False
        self.stored = False
        
        self.name = os.path.splitext(path)[0]
        extension = os.path.splitext(path)[1]
        if extension == ".pdf":
            self.images = pdf2image.convert_from_path(path)
            print(str(len(self.images)) + " pages have been scanned")
            self.read()
        
    def read(self):
        assert("images" in self.__dict__)
        self.text = ""
        for image in self.images:
            self.text += pytesseract.image_to_string(image, lang='eng+fra+spa')
        print(str(len(self.text)) + " characters have been read")

    def split(
        self,
        size=1000,
        overlap=100
    ):
        assert("text" in self.__dict__)
        self.chunks = []
        start = 0
        while start < len(self.text):
            end = start + size
            self.chunks.append(
                {
                    "id": uuid.uuid4().hex + uuid.uuid4().hex,
                    "content": self.text[start:end],
                    "resource": self.name
                }
            )
            start += size - overlap
        print("Text has been split into "+ str(len(self.chunks)) + " chunks")
        return(self)
            
    def translate(
        self,
        skip = False,
        n_samples = 5,
        threshold = 4,
        ollama = "http://ollama:11434/api/generate"
    ):
        assert("chunks" in self.__dict__)
        chunks = random.choices(self.chunks, k = n_samples) # tirage avec remise

        # detect the language
        if not skip:
            chunks_are_english = []
            for chunk in chunks:
                response = requests.post(
                    ollama,
                    json = {
                        "model": "mistral:latest",
                        "prompt": is_english(chunk["content"]),
                        "stream": False
                    }
                )
                print(response.json()["response"])
                chunks_are_english.append(response.json()["response"] in ["Is English: true"," Is English: true"])
            
        # translate all chunks
        if skip or sum(chunks_are_english) >= threshold:
            for i in range(len(self.chunks)):
                self.chunks[i]["translated"] = self.chunks[i]["content"]
            print("Text is already in English")
            
        else:
            print("Translating...")
            for i in range(len(self.chunks)):
                response = requests.post(
                    ollama,
                    json = {
                        "model": "mistral:latest",
                        "prompt": to_english(self.chunks[i]["content"]),
                        "stream": False
                    }
                )
                self.chunks[i]["translated"] = response.json()["response"][len("To English: "):]
            print("All chunks have been translated to English")
        self.translated = True
        return(self)

    def embed(
        self,
        encoder = "sentence-transformers/all-MiniLM-L6-v2",
        cache = "/project/models/",
    ):
        assert(self.translated)
        model = SentenceTransformer(encoder, cache_folder = cache)
        for i in range(len(self.chunks)):
            self.chunks[i]["tokens"] = model.tokenize([self.chunks[i]["translated"]])
            self.chunks[i]["vector"] = model.encode(self.chunks[i]["translated"])
        print("All chunks have been embedded")
        self.embedded = True
        self.encoder = encoder
        return(self)

    def store(
        self,
        collection,
        host = "chroma",
        port = 8000
    ):
        assert(self.embedded)
        client = chromadb.HttpClient(host = host, port = port)
        collection = client.get_or_create_collection(name = collection)
        for i in range(len(self.chunks)):
            collection.add(
                ids = self.chunks[i]["id"],
                embeddings = self.chunks[i]["vector"],
                metadatas = {
                    "chunk": i,
                    "text": self.chunks[i]["content"],
                    "resource": self.name,
                    "translated": self.translated,
                    "ntokens": len(self.chunks[i]["tokens"]),
                    "encoder": self.encoder
                }
            )
        self.stored = True
        print("Stored in the database")


        
