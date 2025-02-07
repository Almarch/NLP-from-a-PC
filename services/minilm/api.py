from sentence_transformers import SentenceTransformer
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os

model_name = "all-MiniLM-L6-v2"

if os.path.exists("/model/" + model_name):
    model = SentenceTransformer("/model/" + model_name)
else:
    model = SentenceTransformer(model_name)
    model.save("/model/" + model_name)

app = FastAPI()

class RequestBody(BaseModel):
    text: List = [
        "The weather is lovely today.",
        "It's so sunny outside!",
        "He drove to the stadium.",
    ]

@app.post("/v1/vectorize")
async def vectorize(request: RequestBody):
    result = model.encode(request.text)
    return result.tolist()

@app.get("/.well-known/ready")
async def ready():
    return {"status": "ready"}