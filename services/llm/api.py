import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import time
import uuid

### load the model
model_name = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    cache_dir="/model/"
)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    cache_dir="/model/",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
model.generation_config = GenerationConfig.from_pretrained(model_name)
model.generation_config.pad_token_id = model.generation_config.eos_token_id

### API
app = FastAPI()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str = model_name
    messages: List[ChatMessage] = [
        {
            "role": "user",
            "content": "Hello"
        },
        {
            "role": "assistant",
            "content": "Hello, how can I assist you today ?"
        },
        {
            "role": "user",
            "content": "I have a question, ..."
        },
    ]
    max_tokens: int = 100
    temperature: float = 0.6

@app.post("/api/chat/completions")
async def chat_completions(request: ChatRequest):
    try:
        input_text = tokenizer.apply_chat_template(
            [{"role": msg.role, "content": msg.content} for msg in request.messages],
            add_generation_prompt=True,
            return_tensors="pt"
        )
        outputs = model.generate(
            input_text.to(model.device),
            max_new_tokens=request.max_tokens,
            temperature=request.temperature
        )
        result = tokenizer.decode(
            outputs[0][input_text.shape[1]:],
            skip_special_tokens=True
        )
        return {
            "id": "chatcmpl-" + str(uuid.uuid4()),
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_name,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": result},
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": input_text.shape[1],
                "completion_tokens": len(outputs[0]) - input_text.shape[1],
                "total_tokens": len(outputs[0])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/models")
async def list_models():
    return {
        "object": "list",
        "data": [
            {
                "id": model_name,
                "object": "model",
                "owned_by": "self"
            }
        ]
    }

@app.get("/api/version")
async def api_version():
    return {"version": "1.0.0"}

@app.get("/api/tags")
async def api_tags():
    return {"object": "list", "data": []}

@app.get("/api/device_map")
async def device_info():
    return model.hf_device_map
