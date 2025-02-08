import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

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

class RequestBody(BaseModel):
    text: List = [
        {
            "role": "user",
            "content": "Hello"
        }
    ]
    ntokens: int = 100
    temperature: float = .6

@app.post("/info")
async def device_info(request):
    return model.hf_device_map

@app.post("/hey")
async def generate(request: RequestBody):
    input_tensor = tokenizer.apply_chat_template(
        request.text,
        add_generation_prompt=True,
        return_tensors="pt"
    )
    outputs = model.generate(
        input_tensor.to(model.device),
        max_new_tokens=request.ntokens,
        temperature=request.temperature
    )
    result = tokenizer.decode(
        outputs[0][input_tensor.shape[1]:],
        skip_special_tokens=True
    )
    return result
