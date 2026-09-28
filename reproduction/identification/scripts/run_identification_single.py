"""
Single-model identification evaluation with checkpointing
Usage: python run_identification_single.py <model_name>
Example: python run_identification_single.py claude-sonnet-3.7
"""

import os
import asyncio
import json
import random
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import sys

from app import call_model
from prompts import get_identification_prompt
from verification_utils import parse_llm_rhyme_output

# API Keys
API_KEYS = {
    'claude': os.getenv("ANTHROPIC_API_KEY", ""),
    'openai': os.getenv("OPENAI_API_KEY", ""),
    'google': os.getenv("GOOGLE_API_KEY", ""),
    'openrouter': os.getenv("OPENROUTER_API_KEY", "")
}

# Strategies to test
STRATEGIES = ['zero_shot_structured', 'zero_shot_cot']

@dataclass
class IdentificationResult:
    """Result of a single identification test"""
    test_id: str
    model: str
    strategy: str
    use_rag: bool
    poem_text: str
    poet: str
    
    # Ground truth
    true_rhyme_type: str
    true_features: List[str]
    
    # Model prediction
    predicted_rhyme_type: Optional[str]
    predicted_features: List[str]
    
    # Accuracy
    rhyme_type_correct: bool
    features_correct: bool
    features_precision: float
    features_recall: float
    features_f1: float
    
    # Metadata
    time_taken: float
    raw_output: str

def load_corpus(corpus_file: str = "complete_corpus_enhanced.json") -> Dict:
    """Load the rhyme corpus"""
    with open(corpus_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_rag_context(corpus: Dict, exclude_poem_text: str) -> str:
    """Get RAG context, EXCLUDING the test poem"""
    examples = []
    
    for poet_name, poet_data in corpus.items():
        for entry in poet_data.get('entries', [])[:50]:  # Take first 50 from each
            rhyme_pair = entry.get('rhyme_pair', [])
            if not rhyme_pair or len(rhyme_pair) < 2:
                continue
            
            # Skip if this matches test poem
            poem_text = ' / '.join(rhyme_pair)
            if poem_text == exclude_poem_text:
                continue
            
            classification = entry.get('classification', '')
            phonetic = entry.get('phonetic', [])
            
            if classification:
                examples.append(f"Lines: {poem_text}\nPattern: {classification}\nPhonetic: {' / '.join(phonetic)}")
    
    # Randomly sample
    if len(examples) > 15:
        examples = random.sample(examples, 15)
    
    if not examples:
        return ""
    
    context = "--- EXAMPLE RHYMES FROM CORPUS ---\n\n"
    for i, ex in enumerate(examples, 1):
        context += f"Example {i}:\n{ex}\n\n"
    context += "--- END OF EXAMPLES ---\n\n"
    
    return context

def sample_test_poems(corpus: Dict, num_samples: int = 26) -> List[Dict]:
    """Sample test poems from corpus"""
    all_poems = []
    
    for poet_name, poet_data in corpus.items():
        for entry in poet_data.get('entries', []):
            rhyme_pair = entry.get('rhyme_pair', [])
            if not rhyme_pair or len(rhyme_pair) < 2:
                continue
            
            classification = entry.get('classification', '')
            if not classification:
                continue
            
            # Parse classification
            parts = classification.split('-')
            if not parts:
                continue
            
            rhyme_type = parts[0]
            features = parts[1:] if len(parts) > 1 else []
            
            all_poems.append({
                'text': ' / '.join(rhyme_pair),
                'poet': poet_name,
                'rhyme_type': rhyme_type,
                'features': features,
                'pattern': classification,
            })
    
    # Sample diverse coverage
    if len(all_poems) <= num_samples:
        return all_poems
    
    # Balance across rhyme types
    samples_by_type = {'M': [], 'F2': [], 'F3': []}
    for poem in all_poems:
        rt = poem['rhyme_type']
        if rt in samples_by_type:
            samples_by_type[rt].append(poem)
    
    samples_per_type = num_samples // 3
    sampled = []
    for rt, poems in samples_by_type.items():
        if poems:
            sampled.extend(random.sample(poems, min(samples_per_type, len(poems))))
    
    # Fill remaining
    if len(sampled) < num_samples:
        remaining = [p for p in all_poems if p not in sampled]
        sampled.extend(random.sample(remaining, min(num_samples - len(sampled), len(remaining))))
    
    return sampled[:num_samples]

async def run_single_test(test_id: str, poem: Dict, model: str, strategy: str, use_rag: bool, corpus: Dict) -> IdentificationResult:
    """Run a single identification test"""
    import time
    
    print(f"\n{'─'*80}")
    print(f"TEST: {test_id}")
    print(f"Model: {model}, Strategy: {strategy}, RAG: {use_rag}")
    print(f"Poem: {poem['text'][:50]}...")
    print(f"True: {poem['rhyme_type']}-{'+'.join(poem['features']) if poem['features'] else 'BASIC'}")
    
    # Get RAG context
    rag_context = get_rag_context(corpus, poem['text']) if use_rag else ""
    
    # Get prompt
    prompt = get_identification_prompt(
        text=poem['text'],
        strategy=strategy,
        rag_context=rag_context
    )
    
    # Get API key
    if 'claude' in model:
        api_key = API_KEYS['claude']
    elif 'gpt' in model or 'o1' in model:
        api_key = API_KEYS['openai']
    elif 'gemini' in model:
        api_key = API_KEYS['google']
    else:
        api_key = API_KEYS['openrouter']
    
    # Call model
    start_time = time.time()
    try:
        result, _ = await call_model(model, prompt, api_key)
        time_taken = time.time() - start_time
    except Exception as e:
        print(f"❌ Error: {e}")
        return IdentificationResult(
            test_id=test_id, model=model, strategy=strategy, use_rag=use_rag,
            poem_text=poem['text'], poet=poem['poet'],
            true_rhyme_type=poem['rhyme_type'], true_features=poem['features'],
            predicted_rhyme_type=None, predicted_features=[],
            rhyme_type_correct=False, features_correct=False,
            features_precision=0.0, features_recall=0.0, features_f1=0.0,
            time_taken=0.0, raw_output=str(e)
        )
    
    # Parse output
    try:
        parsed = parse_llm_rhyme_output(result)
        predicted_rhyme_type = parsed.get('rhyme_type')
        predicted_features = parsed.get('features', [])
    except:
        predicted_rhyme_type = None
        predicted_features = []
    
    # Calculate accuracy
    rhyme_type_correct = (predicted_rhyme_type == poem['rhyme_type'])
    
    true_features_set = set(poem['features'])
    pred_features_set = set(predicted_features)
    
    if not true_features_set and not pred_features_set:
        features_correct = True
        features_precision = 1.0
        features_recall = 1.0
        features_f1 = 1.0
    else:
        features_correct = (true_features_set == pred_features_set)
        
        if pred_features_set:
            features_precision = len(true_features_set & pred_features_set) / len(pred_features_set)
        else:
            features_precision = 1.0 if not true_features_set else 0.0
        
        if true_features_set:
            features_recall = len(true_features_set & pred_features_set) / len(true_features_set)
        else:
            features_recall = 1.0 if not pred_features_set else 0.0
        
        if features_precision + features_recall > 0:
            features_f1 = 2 * (features_precision * features_recall) / (features_precision + features_recall)
        else:
            features_f1 = 0.0
    
    print(f"Predicted: {predicted_rhyme_type}-{'+'.join(predicted_features) if predicted_features else 'BASIC'}")
    print(f"Rhyme type: {'✓' if rhyme_type_correct else '✗'}")
    print(f"Features: {'✓' if features_correct else '✗'} (F1={features_f1:.2f})")
    print(f"Time: {time_taken:.2f}s")
    
    return IdentificationResult(
        test_id=test_id, model=model, strategy=strategy, use_rag=use_rag,
        poem_text=poem['text'], poet=poem['poet'],
        true_rhyme_type=poem['rhyme_type'], true_features=poem['features'],
        predicted_rhyme_type=predicted_rhyme_type, predicted_features=predicted_features,
        rhyme_type_correct=rhyme_type_correct, features_correct=features_correct,
        features_precision=features_precision, features_recall=features_recall,
        features_f1=features_f1, time_taken=time_taken, raw_output=result
    )

async def run_identification_single(model_name: str):
    """Run identification evaluation for a single model with checkpointing"""
    
    # Setup files
    checkpoint_file = f"identification_checkpoint_{model_name.replace('-', '_')}.json"
    results_file = f"identification_results_{model_name.replace('-', '_')}.json"
    
    # Load checkpoint if exists
    start_test = 0
    results = []
    test_poems = None
    
    if Path(checkpoint_file).exists():
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
        start_test = checkpoint.get('completed_tests', 0)
        results = checkpoint.get('results', [])
        test_poems = checkpoint.get('test_poems', None)
        print(f"🔄 Resuming from checkpoint: {start_test} tests completed")
    
    # Load corpus (always needed for RAG context)
    corpus = load_corpus()
    
    # Sample test poems (use saved ones if resuming)
    if test_poems is None:
        # Check for Golden Set first
        golden_file = Path("golden_test_set.json")
        if golden_file.exists():
            print(f"🌟 Loading Golden Test Set from {golden_file}...")
            with open(golden_file, 'r', encoding='utf-8') as f:
                test_poems = json.load(f)
            print(f"✓ Loaded {len(test_poems)} valid poems.")
        else:
            print("⚠️ No Golden Set found, sampling randomly...")
            test_poems = sample_test_poems(corpus, num_samples=26)
            print(f"✓ Sampled {len(test_poems)} test poems")
    else:
        print(f"✓ Using {len(test_poems)} test poems from checkpoint")
    
    # Run tests
    rag_configs = [True, False]
    total_tests = len(STRATEGIES) * len(rag_configs) * len(test_poems)
    test_num = start_test
    
    print(f"\n{'='*80}")
    print(f"IDENTIFICATION EVALUATION: {model_name}")
    print(f"{'='*80}")
    print(f"Strategies: {', '.join(STRATEGIES)}")
    print(f"Total tests: {total_tests}")
    if start_test > 0:
        print(f"Starting from test #{start_test + 1}")
    print(f"{'='*80}\n")
    
    try:
        for strategy in STRATEGIES:
            for use_rag in rag_configs:
                rag_label = "WITH RAG" if use_rag else "WITHOUT RAG"
                
                for i, poem in enumerate(test_poems):
                    # Skip if already done
                    if test_num < start_test:
                        test_num += 1
                        continue
                    
                    test_num += 1
                    test_id = f"{model_name}_{strategy}_{rag_label.replace(' ', '-')}_{i+1}"
                    
                    print(f"\n[{test_num}/{total_tests}] {strategy} - {rag_label}")
                    
                    result = await run_single_test(test_id, poem, model_name, strategy, use_rag, corpus)
                    results.append(asdict(result))
                    
                    # Save checkpoint
                    checkpoint_data = {
                        'model': model_name,
                        'completed_tests': len(results),
                        'test_poems': test_poems,
                        'results': results
                    }
                    with open(checkpoint_file, 'w', encoding='utf-8') as f:
                        json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)
                    print(f"💾 Checkpoint saved: {len(results)}/{total_tests}")
        
        # All tests complete
        print(f"\n{'='*80}")
        print(f"✅ {model_name} COMPLETE!")
        print(f"{'='*80}")
        
        # Save final results
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"📁 Results saved to: {results_file}")
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Interrupted")
        print(f"💾 Progress saved: {len(results)}/{total_tests} tests")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print(f"💾 Progress saved: {len(results)}/{total_tests} tests")
        raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_identification_single.py <model_name>")
        print("Example: python run_identification_single.py claude-sonnet-3.7")
        sys.exit(1)
    
    model_name = sys.argv[1]
    asyncio.run(run_identification_single(model_name))
