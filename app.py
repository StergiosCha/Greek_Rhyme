from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal
import httpx
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = FastAPI(title="Greek Rhyme Analyzer & Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class RhymeIdentificationRequest(BaseModel):
    text: str
    model: str
    prompt_strategy: Literal["zero_shot_structured", "zero_shot_algorithm", "few_shot", "zero_shot_cot", "few_shot_cot"]
    use_rag: bool = False
    api_key: str

class RhymeGenerationRequest(BaseModel):
    theme: str
    rhyme_type: Literal["M", "F2", "F3"]
    features: list[str]
    num_lines: int = 4
    model: str
    use_rag: bool = False
    api_key: str

class RhymeResponse(BaseModel):
    result: str
    model_used: str
    prompt_used: str
    tokens_used: Optional[int] = None

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

MODEL_CONFIGS = {
    # Claude models
    "claude-sonnet-4.5": {
        "endpoint": "https://api.anthropic.com/v1/messages",
        "key": ANTHROPIC_API_KEY,
        "provider": "anthropic",
        "model_name": "claude-sonnet-4-20250514"
    },
    "claude-sonnet-3.7": {
        "endpoint": "https://api.anthropic.com/v1/messages",
        "key": ANTHROPIC_API_KEY,
        "provider": "anthropic",
        "model_name": "claude-3-7-sonnet-20250219"
    },
    
    # Current Gemini models
    "gemini-3-pro": {
        "endpoint": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro:generateContent?key={GOOGLE_API_KEY}",
        "provider": "google",
        "model_display": "Gemini 3 Pro"
    },
    "gemini-2.5-pro": {
        "endpoint": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GOOGLE_API_KEY}",
        "provider": "google",
        "model_display": "Gemini 2.5 Pro"
    },
    "gemini-2.5-flash": {
        "endpoint": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GOOGLE_API_KEY}",
        "provider": "google",
        "model_display": "Gemini 2.5 Flash"
    },
    "gemini-2.5-flash-lite": {
        "endpoint": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={GOOGLE_API_KEY}",
        "provider": "google",
        "model_display": "Gemini 2.5 Flash-Lite"
    },
    "gemini-2.0-flash": {
        "endpoint": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={GOOGLE_API_KEY}",
        "provider": "google",
        "model_display": "Gemini 2.0 Flash"
    },
    
    # OpenAI
    "gpt-4o": {
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "key": OPENAI_API_KEY,
        "provider": "openai"
    },
    
    # Open models via OpenRouter
    "llama-3.3-70b": {
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "key": OPENROUTER_API_KEY,
        "provider": "openrouter",
        "model_name": "meta-llama/llama-3.3-70b-instruct"
    },
    "llama-3.1-70b": {
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "key": OPENROUTER_API_KEY,
        "provider": "openrouter",
        "model_name": "meta-llama/llama-3.1-70b-instruct"
    },
    "qwen-2.5-72b": {
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "key": OPENROUTER_API_KEY,
        "provider": "openrouter",
        "model_name": "qwen/qwen-2.5-72b-instruct"
    },
    "mistral-large": {
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "key": OPENROUTER_API_KEY,
        "provider": "openrouter",
        "model_name": "mistralai/mistral-large"
    }
}

async def call_model(model_name: str, prompt: str, api_key: str) -> tuple[str, Optional[int]]:
    """Call specified model with prompt using provided API key"""
    if model_name not in MODEL_CONFIGS:
        raise HTTPException(400, f"Model {model_name} not supported")
    
    config = MODEL_CONFIGS[model_name]
    provider = config["provider"]
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        if provider == "anthropic":
            headers = {
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            data = {
                "model": config["model_name"],
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": prompt}]
            }
            response = await client.post(config["endpoint"], headers=headers, json=data)
            result = response.json()
            return result["content"][0]["text"], result["usage"]["output_tokens"]
        
        elif provider == "google":
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            data = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"maxOutputTokens": 4000}
            }
            response = await client.post(endpoint, json=data)
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"], None
        
        elif provider == "openai":
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000
            }
            response = await client.post(config["endpoint"], headers=headers, json=data)
            result = response.json()
            return result["choices"][0]["message"]["content"], result["usage"]["completion_tokens"]
        
        elif provider == "openrouter":
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:8052",
                "X-Title": "Greek Rhyme System"
            }
            data = {
                "model": config["model_name"],
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 4000
            }
            response = await client.post(config["endpoint"], headers=headers, json=data)
            result = response.json()
            return result["choices"][0]["message"]["content"], result.get("usage", {}).get("completion_tokens")

@app.get("/models")
async def get_models():
    """Get available models"""
    return {"models": list(MODEL_CONFIGS.keys())}

@app.post("/identify", response_model=RhymeResponse)
async def identify_rhymes(request: RhymeIdentificationRequest):
    """Identify rhymes in Greek text"""
    from prompts import get_identification_prompt
    
    # Get RAG context if requested
    rag_context = ""
    if request.use_rag:
        from rag_system import get_relevant_examples
        rag_context = await get_relevant_examples(request.text)
    
    prompt = get_identification_prompt(
        request.text,
        request.prompt_strategy,
        rag_context
    )
    
    result, tokens = await call_model(request.model, prompt, request.api_key)
    
    return RhymeResponse(
        result=result,
        model_used=request.model,
        prompt_used=prompt[:500] + "..." if len(prompt) > 500 else prompt,
        tokens_used=tokens
    )

@app.post("/generate", response_model=RhymeResponse)
async def generate_rhymes(request: RhymeGenerationRequest):
    """Generate Greek poetry with specified rhyme patterns"""
    from prompts import get_generation_prompt
    
    # Get RAG examples if requested
    rag_context = ""
    if request.use_rag:
        from rag_system import get_generation_examples
        rag_context = await get_generation_examples(
            request.rhyme_type,
            request.features,
            request.theme
        )
    
    prompt = get_generation_prompt(
        request.theme,
        request.rhyme_type,
        request.features,
        request.num_lines,
        rag_context
    )
    
    result, tokens = await call_model(request.model, prompt, request.api_key)
    
    return RhymeResponse(
        result=result,
        model_used=request.model,
        prompt_used=prompt[:500] + "..." if len(prompt) > 500 else prompt,
        tokens_used=tokens
    )

@app.get("/")
async def root():
    return {"message": "Greek Rhyme System API", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8052
    uvicorn.run(app, host="0.0.0.0", port=port)