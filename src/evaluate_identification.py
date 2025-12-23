"""
Evaluation script for rhyme identification task
Tests how well LLMs can identify rhyme types and features in existing poems
"""

import asyncio
import json
import random
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import sys

from app import call_model
from prompts import get_identification_prompt
from verification_utils import verify_identification_output, parse_llm_rhyme_output

# API Keys
import os

# API Keys
API_KEYS = {
    'claude': os.getenv("ANTHROPIC_API_KEY", ""),
    'openai': os.getenv("OPENAI_API_KEY", ""),
    'google': os.getenv("GOOGLE_API_KEY", ""),
    'openrouter': os.getenv("OPENROUTER_API_KEY", "")
}

# Models to evaluate
MODELS = [
    'claude-sonnet-4.5',
    'claude-sonnet-3.7',
    'gemini-2.0-flash',
    'gpt-4o',
    'mistral-large',
]

@dataclass
class IdentificationResult:
    """Result of a single identification test"""
    test_id: str
    model: str
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

class IdentificationEvaluator:
    """Evaluates models on rhyme identification task"""
    
    def __init__(self, models: List[str], corpus_file: str = None):
        self.models = models
        if corpus_file is None:
            # Default to data directory relative to this script
            self.corpus_file = str(Path(__file__).parent.parent / "data" / "complete_corpus_enhanced.json")
        else:
            self.corpus_file = corpus_file
        self.corpus = self._load_corpus()
        self.results: List[IdentificationResult] = []
    
    def _load_corpus(self) -> Dict:
        """Load the rhyme corpus"""
        with open(self.corpus_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_rag_context(self, exclude_poem_text: str) -> str:
        """
        Get RAG context, EXCLUDING the test poem to avoid giving away the answer
        """
        examples = []
        
        for poet_name, poet_data in self.corpus.items():
            for example in poet_data.get('examples', []):
                # Skip if this is the test poem
                if example['lines'] == exclude_poem_text:
                    continue
                
                pattern = example.get('pattern', '')
                lines = example['lines']
                phonetic = example.get('phonetic_structure', '')
                
                examples.append(f"Lines: {lines}\nPattern: {pattern}\nPhonetic structure: {phonetic}")
        
        # Randomly sample examples to keep context manageable
        if len(examples) > 15:
            examples = random.sample(examples, 15)
        
        if not examples:
            return ""
        
        context = "--- EXAMPLE RHYMES FROM CORPUS ---\n\n"
        for i, ex in enumerate(examples, 1):
            context += f"Example {i}:\n{ex}\n\n"
        context += "--- END OF EXAMPLES ---\n\n"
        
        return context
    
    def _sample_test_poems(self, num_samples: int = 26) -> List[Dict]:
        """
        Sample test poems from corpus
        Ensure diverse coverage of rhyme types and features
        """
        all_poems = []
        
        for poet_name, poet_data in self.corpus.items():
            for example in poet_data.get('examples', []):
                pattern = example.get('pattern', '')
                if not pattern:
                    continue
                
                # Parse pattern to get rhyme type and features
                parts = pattern.split('-')
                if not parts:
                    continue
                
                rhyme_type = parts[0]  # M, F2, or F3
                features = parts[1:] if len(parts) > 1 else []
                
                all_poems.append({
                    'text': example['lines'],
                    'poet': poet_name,
                    'rhyme_type': rhyme_type,
                    'features': features,
                    'pattern': pattern,
                })
        
        # Sample to get diverse coverage
        if len(all_poems) <= num_samples:
            return all_poems
        
        # Try to get balanced sample across rhyme types
        samples_by_type = {'M': [], 'F2': [], 'F3': []}
        for poem in all_poems:
            rt = poem['rhyme_type']
            if rt in samples_by_type:
                samples_by_type[rt].append(poem)
        
        # Sample equally from each type
        samples_per_type = num_samples // 3
        sampled = []
        for rt, poems in samples_by_type.items():
            if poems:
                sampled.extend(random.sample(poems, min(samples_per_type, len(poems))))
        
        # Fill remaining with random samples
        if len(sampled) < num_samples:
            remaining = [p for p in all_poems if p not in sampled]
            sampled.extend(random.sample(remaining, min(num_samples - len(sampled), len(remaining))))
        
        return sampled[:num_samples]
    
    async def _run_single_test(self, test_id: str, poem: Dict, model: str, use_rag: bool) -> IdentificationResult:
        """Run a single identification test"""
        import time
        
        print(f"\n{'─'*80}")
        print(f"TEST: {test_id}")
        print(f"Model: {model}, RAG: {use_rag}")
        print(f"Poem: {poem['text'][:50]}...")
        print(f"True: {poem['rhyme_type']}-{'+'.join(poem['features']) if poem['features'] else 'BASIC'}")
        
        # Get RAG context (excluding this poem)
        rag_context = self._get_rag_context(poem['text']) if use_rag else ""
        
        # Get prompt
        prompt = get_identification_prompt(
            text=poem['text'],
            strategy="comprehensive",
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
                test_id=test_id,
                model=model,
                use_rag=use_rag,
                poem_text=poem['text'],
                poet=poem['poet'],
                true_rhyme_type=poem['rhyme_type'],
                true_features=poem['features'],
                predicted_rhyme_type=None,
                predicted_features=[],
                rhyme_type_correct=False,
                features_correct=False,
                features_precision=0.0,
                features_recall=0.0,
                features_f1=0.0,
                time_taken=0.0,
                raw_output=str(e)
            )
        
        # Parse model output
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
        print(f"Features: {'✓' if features_correct else '✗'} (P={features_precision:.2f}, R={features_recall:.2f}, F1={features_f1:.2f})")
        print(f"Time: {time_taken:.2f}s")
        
        return IdentificationResult(
            test_id=test_id,
            model=model,
            use_rag=use_rag,
            poem_text=poem['text'],
            poet=poem['poet'],
            true_rhyme_type=poem['rhyme_type'],
            true_features=poem['features'],
            predicted_rhyme_type=predicted_rhyme_type,
            predicted_features=predicted_features,
            rhyme_type_correct=rhyme_type_correct,
            features_correct=features_correct,
            features_precision=features_precision,
            features_recall=features_recall,
            features_f1=features_f1,
            time_taken=time_taken,
            raw_output=result
        )
    
    async def run_evaluation(self, num_samples: int = 26):
        """Run full identification evaluation"""
        print(f"\n{'='*80}")
        print("RHYME IDENTIFICATION EVALUATION")
        print(f"{'='*80}")
        print(f"Models: {', '.join(self.models)}")
        print(f"Samples: {num_samples}")
        print(f"{'='*80}\n")
        
        # Sample test poems
        test_poems = self._sample_test_poems(num_samples)
        print(f"✓ Sampled {len(test_poems)} test poems")
        
        # Run tests
        rag_configs = [True, False]
        total_tests = len(self.models) * len(test_poems) * len(rag_configs)
        test_num = 0
        
        for model in self.models:
            print(f"\n{'▓'*80}")
            print(f"MODEL: {model}")
            print(f"{'▓'*80}")
            
            for use_rag in rag_configs:
                rag_label = "WITH RAG" if use_rag else "WITHOUT RAG"
                print(f"\n{rag_label}")
                
                for i, poem in enumerate(test_poems):
                    test_num += 1
                    test_id = f"{model}_{rag_label.replace(' ', '-')}_{i+1}"
                    
                    print(f"\n[{test_num}/{total_tests}]")
                    
                    result = await self._run_single_test(test_id, poem, model, use_rag)
                    self.results.append(result)
        
        print(f"\n{'='*80}")
        print("EVALUATION COMPLETE")
        print(f"{'='*80}")
    
    def save_results(self, filename: str = "identification_results.json"):
        """Save results to JSON file"""
        results_dict = [asdict(r) for r in self.results]
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results_dict, f, ensure_ascii=False, indent=2)
        print(f"\n📁 Results saved to: {filename}")
    
    def print_summary(self):
        """Print evaluation summary"""
        print(f"\n{'='*80}")
        print("SUMMARY")
        print(f"{'='*80}\n")
        
        for model in self.models:
            model_results = [r for r in self.results if r.model == model]
            if not model_results:
                continue
            
            print(f"\n{model}:")
            
            # Overall accuracy
            rhyme_type_acc = sum(r.rhyme_type_correct for r in model_results) / len(model_results) * 100
            features_acc = sum(r.features_correct for r in model_results) / len(model_results) * 100
            avg_f1 = sum(r.features_f1 for r in model_results) / len(model_results)
            
            print(f"  Rhyme type accuracy: {rhyme_type_acc:.1f}%")
            print(f"  Features exact match: {features_acc:.1f}%")
            print(f"  Features F1: {avg_f1:.3f}")
            
            # By RAG
            with_rag = [r for r in model_results if r.use_rag]
            without_rag = [r for r in model_results if not r.use_rag]
            
            if with_rag:
                rag_rt_acc = sum(r.rhyme_type_correct for r in with_rag) / len(with_rag) * 100
                print(f"  With RAG rhyme type: {rag_rt_acc:.1f}%")
            
            if without_rag:
                no_rag_rt_acc = sum(r.rhyme_type_correct for r in without_rag) / len(without_rag) * 100
                print(f"  Without RAG rhyme type: {no_rag_rt_acc:.1f}%")

async def main():
    evaluator = IdentificationEvaluator(models=MODELS)
    await evaluator.run_evaluation(num_samples=26)
    evaluator.print_summary()
    evaluator.save_results()

if __name__ == "__main__":
    asyncio.run(main())
