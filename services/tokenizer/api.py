from fastapi import FastAPI
from pydantic import BaseModel
import spacy
import os

# API
app = FastAPI()

class TextRequest(BaseModel):
    text: str
    lang: str = "fr"

@app.post("/tokenize/")
async def tokenize(request: TextRequest):

    assert(request.lang in ["en","fr","es"])

    # load the model
    model_family = "_core_web_sm"
    model_name = request.lang + model_family
    model_path = "/model/" + model_name

    if not os.path.exists(model_path):
        nlp = spacy.load(model_name)
        nlp.to_disk(model_path)
    else:
        nlp = spacy.load(model_path)

    # tokenize
    doc = nlp(request.text)
    sentences = [sent.text for sent in doc.sents]
    return {"sentences": sentences}
