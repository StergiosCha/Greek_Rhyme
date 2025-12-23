from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Literal
import httpx
import os
from dotenv import load_dotenv

# Load .env file
# Load .env file
load_dotenv()

# Add src to path for imports
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

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
    prompt_strategy: Literal["zero_shot_structured", "zero_shot_algorithm", "few_shot", "zero_shot_cot", "few_shot_cot", "mosaic_enhanced"]
    use_rag: bool = False
    api_key: str

class RhymeGenerationRequest(BaseModel):
    theme: str
    rhyme_type: Literal["M", "F2", "F3"]
    features: list[str]
    num_lines: int = 4
    model: str
    use_rag: bool = False
    use_verification: bool = True  # Enable/disable verification feedback loop
    poet: Optional[str] = ""  # Optional poet style
    api_key: str

class RhymeResponse(BaseModel):
    result: str
    generation_model: str
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
    "gemini-3-pro-preview": {
        "endpoint": f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent?key={GOOGLE_API_KEY}",
        "provider": "google",
        "model_display": "Gemini 3 Pro Preview"
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
    "gpt-5": {
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
    "llama-3.1-8b": {
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "key": OPENROUTER_API_KEY,
        "provider": "openrouter",
        "model_name": "meta-llama/llama-3.1-8b-instruct"
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
    
    async with httpx.AsyncClient(timeout=600.0) as client:  # 10 minutes for verification loops
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
                "generationConfig": {"maxOutputTokens": 8000}  # Increased for long RAG prompts
            }
            response = await client.post(endpoint, json=data)
            result = response.json()
            # Safe access with error handling
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    return candidate["content"]["parts"][0]["text"], None
            # If response structure is unexpected, raise with details
            raise ValueError(f"Unexpected Google API response: {result}")
        
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
            if "choices" in result:
                return result["choices"][0]["message"]["content"], result["usage"]["completion_tokens"]
            else:
                raise ValueError(f"Unexpected OpenAI API response: {result}")
        
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
            
            # Handle API errors
            if "error" in result:
                raise ValueError(f"OpenRouter API error: {result['error']}")
            if "choices" not in result:
                raise ValueError(f"Unexpected OpenRouter response format: {result}")
                
            return result["choices"][0]["message"]["content"], result.get("usage", {}).get("completion_tokens")

@app.get("/models")
async def get_models():
    """Get available models"""
    return {"models": list(MODEL_CONFIGS.keys())}

@app.post("/identify", response_model=RhymeResponse)
async def identify_rhymes(request: RhymeIdentificationRequest):
    """Identify rhymes in Greek text"""
    from prompts import get_identification_prompt
    from greek_phonology import extract_rhyme_domain, analyze_mosaic_pattern, format_for_llm_prompt
    
    # Get RAG context if requested
    rag_context = ""
    if request.use_rag:
        from rag_system import get_relevant_examples
        rag_context = await get_relevant_examples(request.text)
    
    # PHONETIC PREPROCESSING for mosaic_enhanced strategy
    phonetic_analysis = ""
    if request.prompt_strategy == "mosaic_enhanced":
        lines = [l.strip() for l in request.text.split('\n') if l.strip()]
        
        analyses = []
        for i in range(len(lines)-1):
            analysis = analyze_mosaic_pattern(lines[i], lines[i+1])
            analyses.append(format_for_llm_prompt(analysis))
        
        phonetic_analysis = "\n\n".join(analyses)
    
    prompt = get_identification_prompt(
        request.text,
        request.prompt_strategy,
        rag_context,
        phonetic_analysis
    )
    
    result, tokens = await call_model(request.model, prompt, request.api_key)
    
    return RhymeResponse(
        result=result,
        generation_model=request.model,
        prompt_used=prompt[:500] + "..." if len(prompt) > 500 else prompt,
        tokens_used=tokens
    )

# Insert this after the /identify endpoint (after line 236)

@app.post("/identify/verified")
async def identify_rhymes_verified(request: RhymeIdentificationRequest):
    """
    Identify rhymes in Greek text WITH PHONOLOGICAL VERIFICATION.
    This endpoint adds post-processing verification to check LLM output.
    """
    from prompts import get_identification_prompt
    from greek_phonology import extract_rhyme_domain, analyze_mosaic_pattern, format_for_llm_prompt
    from verification_utils import verify_identification_output
    
    # Get RAG context if requested
    rag_context = ""
    if request.use_rag:
        from rag_system import get_relevant_examples
        rag_context = await get_relevant_examples(request.text)
    
    # PHONETIC PREPROCESSING for mosaic_enhanced strategy
    phonetic_analysis = ""
    if request.prompt_strategy == "mosaic_enhanced":
        lines = [l.strip() for l in request.text.split('\n') if l.strip()]
        
        analyses = []
        for i in range(len(lines)-1):
            analysis = analyze_mosaic_pattern(lines[i], lines[i+1])
            analyses.append(format_for_llm_prompt(analysis))
        
        phonetic_analysis = "\n\n".join(analyses)
    
    prompt = get_identification_prompt(
        request.text,
        request.prompt_strategy,
        rag_context,
        phonetic_analysis
    )
    
    # Get LLM result
    llm_result, tokens = await call_model(request.model, prompt, request.api_key)
    
    # STEP 1: Get LLM's initial identification
    llm_result, tokens = await call_model(request.model, prompt, request.api_key)
    
    # STEP 2: VERIFICATION - Analyze poem to find ground truth
    verification = verify_identification_output(llm_result, request.text)
    
    # STEP 3: Send verification results back to LLM for reflection
    feedback_prompt = f"""You previously analyzed this Greek poem for rhymes:

{request.text}

Your analysis was:
{llm_result}

PHONOLOGICAL VERIFICATION RESULTS:
{verification['verification_summary']}

Please review the verification results and provide a corrected analysis that:
1. Acknowledges which rhymes you correctly identified
2. Explains any rhymes you missed
3. Corrects any false rhymes you claimed
4. Provides the final corrected rhyme scheme

Be concise and focus on the corrections."""

    # Get LLM's reflection
    llm_reflection, tokens2 = await call_model(request.model, feedback_prompt, request.api_key)
    
    # Format combined output
    combined_result = f"""=== INITIAL LLM ANALYSIS ===
{llm_result}

=== PHONOLOGICAL VERIFICATION ===
{verification['verification_summary']}

=== LLM REFLECTION & CORRECTION ===
{llm_reflection}
"""
    
    return {
        "result": combined_result,
        "llm_output": llm_result,
        "llm_reflection": llm_reflection,
        "verification": verification,
        "generation_model": request.model,
        "prompt_used": prompt[:500] + "..." if len(prompt) > 500 else prompt,
        "tokens_used": tokens + tokens2
    }

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
            request.theme,
            poet=request.poet if request.poet else None
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
        generation_model=request.model,
        prompt_used=prompt[:500] + "..." if len(prompt) > 500 else prompt,
        tokens_used=tokens
    )

class EvaluationRequest(BaseModel):
    test_cases: Optional[list[dict]] = None  # If None, use default test cases
    num_samples: int = 1
    model: str
    api_key: str

@app.post("/evaluate")
async def evaluate_system(request: EvaluationRequest):
    """
    Evaluate the rhyme generation system by comparing:
    1. Generation WITHOUT verification (fast, single-shot)
    2. Symbolic rule validation
    3. Generation WITH verification (feedback loop)
    
    Returns detailed comparison metrics for all parameter combinations.
    """
    from evaluate_system import SystemEvaluator, DEFAULT_TEST_CASES
    from dataclasses import asdict
    
    # Define callback to bridge Evaluator -> App -> LLM
    async def llm_callback(model, prompt):
        return await call_model(model, prompt, request.api_key)
    
    # Use provided test cases or defaults
    test_cases = request.test_cases if request.test_cases else DEFAULT_TEST_CASES
    
    # Initialize evaluator
    evaluator = SystemEvaluator(
        model_name=request.model,
        generate_callback=llm_callback
    )
    
    # Run evaluation
    await evaluator.run_evaluation(test_cases, num_samples=request.num_samples)
    
    # Calculate summary statistics
    total_tests = len(evaluator.results)
    
    no_verify_valid_count = sum(1 for r in evaluator.results if r.no_verify_valid)
    with_verify_valid_count = sum(1 for r in evaluator.results if r.with_verify_valid)
    
    avg_no_verify_time = sum(r.no_verify_time for r in evaluator.results) / total_tests if total_tests > 0 else 0
    avg_with_verify_time = sum(r.with_verify_time for r in evaluator.results) / total_tests if total_tests > 0 else 0
    avg_attempts = sum(r.with_verify_attempts for r in evaluator.results) / total_tests if total_tests > 0 else 0
    
    no_verify_total_pairs = sum(r.no_verify_total_pairs for r in evaluator.results)
    no_verify_correct_pairs = sum(r.no_verify_correct_pairs for r in evaluator.results)
    with_verify_total_pairs = sum(r.with_verify_total_pairs for r in evaluator.results)
    with_verify_correct_pairs = sum(r.with_verify_correct_pairs for r in evaluator.results)
    
    no_verify_accuracy = (no_verify_correct_pairs / no_verify_total_pairs * 100) if no_verify_total_pairs > 0 else 0
    with_verify_accuracy = (with_verify_correct_pairs / with_verify_total_pairs * 100) if with_verify_total_pairs > 0 else 0
    
    return {
        "summary": {
            "total_tests": total_tests,
            "model": request.model,
            "without_verification": {
                "valid_poems": no_verify_valid_count,
                "valid_percentage": (no_verify_valid_count / total_tests * 100) if total_tests > 0 else 0,
                "avg_time": avg_no_verify_time,
                "overall_accuracy": no_verify_accuracy,
                "correct_pairs": no_verify_correct_pairs,
                "total_pairs": no_verify_total_pairs
            },
            "with_verification": {
                "valid_poems": with_verify_valid_count,
                "valid_percentage": (with_verify_valid_count / total_tests * 100) if total_tests > 0 else 0,
                "avg_time": avg_with_verify_time,
                "avg_attempts": avg_attempts,
                "overall_accuracy": with_verify_accuracy,
                "correct_pairs": with_verify_correct_pairs,
                "total_pairs": with_verify_total_pairs
            },
            "improvement": {
                "accuracy_gain": with_verify_accuracy - no_verify_accuracy,
                "valid_poem_gain": with_verify_valid_count - no_verify_valid_count,
                "time_multiplier": avg_with_verify_time / avg_no_verify_time if avg_no_verify_time > 0 else 0
            }
        },
        "detailed_results": [asdict(r) for r in evaluator.results]
    }

@app.post("/agent/generate")
async def agent_generate_rhymes(request: RhymeGenerationRequest):
    """
    Generate Greek poetry using the Agentic Pipeline (Generation + Verification Loop)
    """
    from agent_pipeline import AgentPipeline
    
    # Define callback to bridge Agent -> App -> LLM
    async def llm_callback(model, prompt):
        return await call_model(model, prompt, request.api_key)
    
    # Initialize Pipeline with real LLM
    pipeline = AgentPipeline(model_name=request.model, generate_callback=llm_callback)
    
    # Run Pipeline
    result = await pipeline.generate_poem(
        theme=request.theme,
        rhyme_type=request.rhyme_type,
        features=request.features,
        num_lines=request.num_lines,
        poet=request.poet if request.poet else None,
        use_rag=request.use_rag,
        use_verification=request.use_verification
    )
    
    # If there is an error (e.g. failed after 3 attempts), we STILL return the result
    # so the user can see the failed draft and feedback.
    # The 'verification' field will contain the failure details.
    
    return {
        "poem": result["poem"],
        "verification": result["verification"],
        "generation_model": request.model,
        "error": result.get("error") # Optional: pass error message if present
    }

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    import uvicorn
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8052
    uvicorn.run(app, host="0.0.0.0", port=port)