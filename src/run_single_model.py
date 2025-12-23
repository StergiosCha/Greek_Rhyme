"""
Run evaluation for a SINGLE model with checkpoint support
Usage: python run_single_model.py <model_name>
"""

import asyncio
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evaluate_system import SystemEvaluator, DEFAULT_TEST_CASES, EvaluationResult
from dataclasses import asdict

# API Keys
# API Keys
API_KEYS = {
    'claude': os.getenv("ANTHROPIC_API_KEY", ""),
    'openai': os.getenv("OPENAI_API_KEY", ""),
    'google': os.getenv("GOOGLE_API_KEY", ""),
    'openrouter': os.getenv("OPENROUTER_API_KEY", "")
}

# 8-line test cases
TEST_CASES_8_LINES = [
    {**case, 'num_lines': 8} for case in DEFAULT_TEST_CASES
]


def get_api_key_for_model(model: str) -> str:
    """Get the appropriate API key for a model"""
    if 'claude' in model:
        return API_KEYS['claude']
    elif 'gpt' in model:
        return API_KEYS['openai']
    elif 'gemini' in model:
        return API_KEYS['google']
    else:
        return API_KEYS['openrouter']


async def llm_callback(model: str, prompt: str, api_key: str = None):
    """Callback to call LLM models"""
    from app import call_model
    if api_key is None:
        api_key = get_api_key_for_model(model)
    result, tokens = await call_model(model, prompt, api_key)
    return result, tokens


def get_checkpoint_file(model_name):
    """Get checkpoint filename for a specific model"""
    safe_name = model_name.replace(".", "_").replace("-", "_")
    return f"checkpoint_{safe_name}.json"


def get_results_file(model_name):
    """Get results filename for a specific model"""
    safe_name = model_name.replace(".", "_").replace("-", "_")
    return f"results_{safe_name}.json"


async def run_single_model(model_name):
    """Run evaluation for a single model"""
    
    checkpoint_file = get_checkpoint_file(model_name)
    results_file = get_results_file(model_name)
    
    # Load checkpoint if exists
    checkpoint = None
    if Path(checkpoint_file).exists():
        try:
            with open(checkpoint_file, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            print(f"📂 Resuming {model_name}: {checkpoint['completed_tests']} tests done")
        except:
            pass
    
    # Create evaluator
    evaluator = SystemEvaluator(models=[model_name], generate_callback=llm_callback)
    
    # Restore previous results if resuming
    start_test = 0
    if checkpoint and 'results' in checkpoint:
        for result_dict in checkpoint['results']:
            result = EvaluationResult(**result_dict)
            evaluator.results.append(result)
        start_test = len(evaluator.results)
        print(f"✅ Restored {start_test} previous results")
    
    # Create pipeline
    from agent_pipeline import AgentPipeline
    pipeline = AgentPipeline(model_name, llm_callback)
    
    # Run tests
    rag_configs = [True, False]
    total_tests = len(TEST_CASES_8_LINES) * len(rag_configs) * 2  # 2 = with/without verification
    
    print(f"\n{'='*80}")
    print(f"EVALUATING: {model_name}")
    print(f"{'='*80}")
    print(f"Test cases: {len(TEST_CASES_8_LINES)}")
    print(f"Total tests: {total_tests}")
    if start_test > 0:
        print(f"Starting from test #{start_test + 1}")
    print(f"{'='*80}\n")
    
    test_num = start_test
    
    try:
        for rag_idx, use_rag in enumerate(rag_configs):
            rag_label = "WITH RAG" if use_rag else "WITHOUT RAG"
            print(f"\n{'▓'*80}")
            print(f"{rag_label}")
            print(f"{'▓'*80}")
            
            for case_idx, test_case in enumerate(TEST_CASES_8_LINES):
                # Skip if already done
                if test_num < start_test:
                    test_num += 1
                    continue
                
                test_num += 1
                test_id = f"{model_name}_{rag_label.replace(' ', '-')}_{case_idx+1}"
                
                print(f"\n{'─'*80}")
                print(f"TEST {test_num}/{total_tests}: {test_case['rhyme_type']} + {test_case['features']}")
                print(f"Theme: {test_case['theme']}")
                print(f"{'─'*80}")
                
                # Run test
                result = await evaluator._run_single_test(
                    test_id, test_case, model_name, use_rag, pipeline
                )
                evaluator.results.append(result)
                
                # Print summary
                evaluator._print_test_summary(result)
                
                # Save checkpoint
                checkpoint_data = {
                    'model': model_name,
                    'completed_tests': len(evaluator.results),
                    'results': [asdict(r) for r in evaluator.results]
                }
                with open(checkpoint_file, 'w', encoding='utf-8') as f:
                    json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
                print(f"💾 Checkpoint saved: {len(evaluator.results)}/{total_tests}")
        
        # All tests complete
        print(f"\n{'='*80}")
        print(f"✅ {model_name} COMPLETE!")
        print(f"{'='*80}")
        
        # Save final results
        evaluator.save_results(results_file)
        print(f"📁 Results saved to: {results_file}")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrupted")
        print(f"💾 Progress saved: {len(evaluator.results)}/{total_tests} tests")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print(f"💾 Progress saved: {len(evaluator.results)}/{total_tests} tests")
        raise


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_single_model.py <model_name>")
        print("Example: python run_single_model.py llama-3.1-70b")
        sys.exit(1)
    
    model_name = sys.argv[1]
    asyncio.run(run_single_model(model_name))
