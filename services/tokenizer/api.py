from fastapi import FastAPI
from pydantic import BaseModel
import spacy

# API
app = FastAPI()

class RequestBody(BaseModel):
    text: str
    lang: str = "en"

@app.post("/split/")
async def tokenize(request: RequestBody):

    assert(request.lang in ["en","fr","es"])
    model = {
        "en": "en_core_web_trf",
        "fr": "fr_dep_news_trf",
        "es": "es_dep_news_trf",
    }[request.lang]
    nlp = spacy.load(model)

    # tokenize
    doc = nlp(request.text)
    sentences = [sent.text for sent in doc.sents]
    return {"sentences": sentences}
