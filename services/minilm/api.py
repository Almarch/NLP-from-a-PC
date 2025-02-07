from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# 1. Load a pretrained Sentence Transformer model
# model = SentenceTransformer("all-MiniLM-L6-v2")
# model.save("/model/")

model = SentenceTransformer("/model/")

app = FastAPI()

class RequestBody(BaseModel):
    text: List = [
        "The weather is lovely today.",
        "It's so sunny outside!",
        "He drove to the stadium.",
    ]

@app.post("/embed")
async def generate(request: RequestBody):
    result = model.encode(request.text)
    return result
