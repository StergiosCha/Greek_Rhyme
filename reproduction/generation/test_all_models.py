"""
Test all 11 models to verify API keys are working
"""

import os
import asyncio
from app import call_model

# API Keys
API_KEYS = {
    'claude': os.getenv("ANTHROPIC_API_KEY", ""),
    'openai': os.getenv("OPENAI_API_KEY", ""),
    'google': os.getenv("GOOGLE_API_KEY", ""),
    'openrouter': os.getenv("OPENROUTER_API_KEY", "")
}

# All 10 models
ALL_MODELS = [
    ("claude-sonnet-4.5", "claude"),
    ("claude-sonnet-3.7", "claude"),
    ("gemini-3-pro-preview", "google"),
    ("gemini-2.5-pro", "google"),
    ("gemini-2.5-flash", "google"),
    ("gpt-4o", "openai"),
    ("llama-3.3-70b", "openrouter"),
    ("llama-3.1-70b", "openrouter"),
    ("qwen-2.5-72b", "openrouter"),
    ("mistral-large", "openrouter")
]

TEST_PROMPT = "Say 'OK' if you can read this."

async def test_model(model_name: str, provider: str):
    """Test a single model"""
    try:
        api_key = API_KEYS[provider]
        result, tokens = await call_model(model_name, TEST_PROMPT, api_key)
        
        # Check if we got a response
        if result and len(result) > 0:
            return True, f"✓ OK (tokens: {tokens})"
        else:
            return False, "✗ Empty response"
    except Exception as e:
        return False, f"✗ Error: {str(e)[:100]}"


async def main():
    print("="*80)
    print("TESTING ALL MODELS")
    print("="*80)
    print(f"Total models to test: {len(ALL_MODELS)}")
    print()
    
    results = []
    
    for i, (model_name, provider) in enumerate(ALL_MODELS, 1):
        print(f"[{i}/{len(ALL_MODELS)}] Testing {model_name}...", end=" ", flush=True)
        
        success, message = await test_model(model_name, provider)
        results.append((model_name, success, message))
        
        print(message)
        
        # Small delay between tests
        await asyncio.sleep(0.5)
    
    # Summary
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    
    working = [r for r in results if r[1]]
    failing = [r for r in results if not r[1]]
    
    print(f"✓ Working: {len(working)}/{len(ALL_MODELS)}")
    print(f"✗ Failing: {len(failing)}/{len(ALL_MODELS)}")
    print()
    
    if failing:
        print("Failed models:")
        for model, _, message in failing:
            print(f"  - {model}: {message}")
        print()
    
    if len(working) == len(ALL_MODELS):
        print("🎉 ALL MODELS WORKING! Ready to run evaluation.")
    else:
        print("⚠️  Some models failed. Fix API keys before running evaluation.")
    
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
