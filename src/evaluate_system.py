"""
Evaluation Script for Greek Rhyme System
=========================================

This script evaluates the system by comparing:
1. Generation WITHOUT verification (fast, single-shot)
2. Symbolic rule validation (using greek_phonology.py)
3. Generation WITH verification (feedback loop)

Tests all parameter combinations: M, F2, F3, PURE, RICH, IMPERFECT, MOSAIC, IDV

Usage:
    python evaluate_system.py --model gpt-4o --num-samples 5
"""

import asyncio
import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse

# Import our modules
from agent_pipeline import AgentPipeline
from greek_phonology import classify_rhyme_pair, extract_rhyme_domain, detect_stress_position, analyze_mosaic_pattern
from verification_utils import find_all_rhymes_in_poem


@dataclass
class EvaluationResult:
    """Results for a single test case"""
    test_id: str
    model: str
    use_rag: bool
    theme: str
    rhyme_type: str  # M, F2, F3
    features: List[str]  # PURE, RICH, IMPERFECT, MOSAIC, IDV
    
    # Without verification
    no_verify_poem: str
    no_verify_time: float
    no_verify_valid: bool
    no_verify_errors: List[str]
    no_verify_correct_pairs: int
    no_verify_total_pairs: int
    
    # With verification
    with_verify_poem: str
    with_verify_time: float
    with_verify_attempts: int
    with_verify_valid: bool
    with_verify_errors: List[str]
    with_verify_correct_pairs: int
    with_verify_total_pairs: int
    
    # Comparison
    improvement: float  # Percentage improvement in accuracy


class SymbolicValidator:
    """
    Validates poems using symbolic phonological rules
    This is the GROUND TRUTH - no LLM involved
    """
    
    def validate_poem(self, poem_text: str, expected_rhyme_type: str, expected_features: List[str]) -> Dict[str, Any]:
        """
        Validate a poem against expected constraints using symbolic rules
        
        Args:
            poem_text: The generated poem
            expected_rhyme_type: M, F2, or F3
            expected_features: List of features like PURE, RICH, IMPERFECT, MOSAIC, IDV
            
        Returns:
            Dict with validation results
        """
        lines = [l.strip() for l in poem_text.split('\n') if l.strip()]
        
        # Clean lines (remove metadata, numbers, etc.)
        clean_lines = self._clean_lines(lines)
        
        if len(clean_lines) < 2:
            return {
                'valid': False,
                'errors': [f'Too few lines: {len(clean_lines)}'],
                'correct_pairs': 0,
                'total_pairs': 0,
                'details': []
            }
        
        # Check consecutive pairs (assuming couplet structure)
        errors = []
        details = []
        correct_pairs = 0
        total_pairs = 0
        
        for i in range(0, len(clean_lines) - 1, 2):
            if i + 1 >= len(clean_lines):
                break
            
            total_pairs += 1
            line1 = clean_lines[i]
            line2 = clean_lines[i + 1]
            
            # Extract rhyme domains
            rd1 = extract_rhyme_domain(line1)
            rd2 = extract_rhyme_domain(line2)
            
            w1 = rd1['rhyme_domain'].strip('*·.').strip()
            w2 = rd2['rhyme_domain'].strip('*·.').strip()
            
            # Validate this pair
            pair_result = self._validate_pair(
                w1, w2, line1, line2,
                expected_rhyme_type, expected_features
            )
            
            details.append({
                'line_nums': (i + 1, i + 2),
                'words': (w1, w2),
                'result': pair_result
            })
            
            if pair_result['valid']:
                correct_pairs += 1
            else:
                errors.extend(pair_result['errors'])
        
        overall_valid = len(errors) == 0
        
        return {
            'valid': overall_valid,
            'errors': errors,
            'correct_pairs': correct_pairs,
            'total_pairs': total_pairs,
            'details': details,
            'accuracy': (correct_pairs / total_pairs * 100) if total_pairs > 0 else 0
        }
    
    def _clean_lines(self, lines: List[str]) -> List[str]:
        """Clean lines to extract only Greek poetry"""
        import re
        
        clean = []
        for line in lines:
            # Strip leading numbers
            line = re.sub(r'^\d+\.?\s*', '', line)
            # Strip markdown
            line = line.replace('**', '').replace('*', '')
            # Strip annotations
            line = re.sub(r'\s*[\(\[].*?[\)\]]\s*$', '', line)
            line = line.strip()
            
            # Skip if too short
            if len(line) < 5:
                continue
            # Skip if no Greek
            if not re.search(r'[\u0370-\u03FF\u1F00-\u1FFF]', line):
                continue
            # Skip headers
            if line.startswith('#'):
                continue
            # Skip if has parentheses/brackets
            if '(' in line or '[' in line:
                continue
            
            clean.append(line)
        
        return clean
    
    def _validate_pair(self, w1: str, w2: str, line1: str, line2: str,
                      expected_rhyme_type: str, expected_features: List[str]) -> Dict[str, Any]:
        """Validate a single rhyme pair"""
        errors = []
        
        # 1. Check if they rhyme at all
        rhyme_result = classify_rhyme_pair(w1, w2)
        
        if rhyme_result['type'] == 'NONE':
            errors.append(f"No rhyme: '{w1}' / '{w2}'")
            return {'valid': False, 'errors': errors, 'rhyme_type': 'NONE'}
        
        # 2. Check stress position (M/F2/F3)
        requested_stress = expected_rhyme_type
        if requested_stress:
            s1 = detect_stress_position(w1)
            s2 = detect_stress_position(w2)
            
            def matches_stress(stress_info, req):
                for _, code in stress_info:
                    if code == req:
                        return True
                    if req == "M" and code == "F1":
                        return True
                    if req == "F1" and code == "M":
                        return True
                return False
            
            if not (matches_stress(s1, requested_stress) and matches_stress(s2, requested_stress)):
                errors.append(f"Stress mismatch: Expected {requested_stress}, found {s1}/{s2} for '{w1}' / '{w2}'")
        
        # 3. Check rhyme quality (PURE, RICH, IMPERFECT)
        if "PURE" in expected_features:
            if rhyme_result['type'] != 'PURE':
                errors.append(f"PURE requested but '{w1}' / '{w2}' is {rhyme_result['type']}")
        
        if "RICH" in expected_features:
            if rhyme_result['type'] != 'RICH':
                errors.append(f"RICH requested but '{w1}' / '{w2}' is {rhyme_result['type']}")
        
        if "IMPERFECT" in expected_features or "IMP" in expected_features:
            if rhyme_result['type'] != 'IMPERFECT':
                errors.append(f"IMPERFECT requested but '{w1}' / '{w2}' is {rhyme_result['type']}")
        
        # 4. Check MOSAIC
        if "MOSAIC" in expected_features or "MOS" in expected_features:
            mosaic_check = analyze_mosaic_pattern(line1, line2)
            if not mosaic_check['mosaic_candidate']:
                errors.append(f"MOSAIC requested but '{w1}' / '{w2}' is not mosaic")
        
        # 5. Check IDV (Pre-rhyme Identical Vowel)
        if "IDV" in expected_features:
            from greek_phonology import extract_pre_rhyme_vowel
            v1 = extract_pre_rhyme_vowel(w1)
            v2 = extract_pre_rhyme_vowel(w2)
            
            # Phonetic normalization
            phonetic_map = {
                'α': 'a', 'ά': 'a',
                'ε': 'e', 'έ': 'e',
                'η': 'i', 'ή': 'i', 'ι': 'i', 'ί': 'i', 'υ': 'i', 'ύ': 'i',
                'ο': 'o', 'ό': 'o', 'ω': 'o', 'ώ': 'o',
            }
            
            def normalize_vowel(v):
                return phonetic_map.get(v, v)
            
            if v1 and v2:
                if normalize_vowel(v1) != normalize_vowel(v2):
                    errors.append(f"IDV requested but pre-stress vowels differ: '{v1}' vs '{v2}' in '{w1}' / '{w2}'")
        
        # 6. Check for identical words (COPY)
        is_copy = w1.lower() == w2.lower()
        if is_copy and "COPY" not in expected_features:
            errors.append(f"Identical words '{w1}' / '{w2}' (COPY) not allowed")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'rhyme_type': rhyme_result['type'],
            'rhyme_subtype': rhyme_result.get('subtype', '')
        }


class SystemEvaluator:
    """Main evaluation orchestrator"""
    
    def __init__(self, models: List[str] = None, generate_callback=None):
        self.models = models if models else ["gpt-4o"]
        self.generate_callback = generate_callback
        self.validator = SymbolicValidator()
        self.results: List[EvaluationResult] = []
    
    async def run_evaluation(self, test_cases: List[Dict[str, Any]], num_samples: int = 1, 
                           test_rag: bool = True, test_no_rag: bool = True):
        """
        Run evaluation on all test cases across all models and RAG configurations
        
        Args:
            test_cases: List of test case configurations
            num_samples: Number of times to run each test case
            test_rag: Whether to test with RAG enabled
            test_no_rag: Whether to test with RAG disabled
        """
        # Calculate total tests
        rag_configs = []
        if test_rag:
            rag_configs.append(True)
        if test_no_rag:
            rag_configs.append(False)
        
        total_tests = len(self.models) * len(test_cases) * len(rag_configs) * num_samples
        
        print(f"\n{'='*80}")
        print(f"GREEK RHYME SYSTEM EVALUATION")
        print(f"{'='*80}")
        print(f"Models: {', '.join(self.models)}")
        print(f"Test cases: {len(test_cases)}")
        print(f"RAG configurations: {len(rag_configs)} ({'RAG+NoRAG' if len(rag_configs)==2 else 'RAG' if test_rag else 'NoRAG'})")
        print(f"Samples per configuration: {num_samples}")
        print(f"Total tests: {total_tests}")
        print(f"{'='*80}\n")
        
        test_num = 0
        for model in self.models:
            print(f"\n{'█'*80}")
            print(f"MODEL: {model}")
            print(f"{'█'*80}")
            
            # Create pipeline for this model
            pipeline = AgentPipeline(model, self.generate_callback)
            
            for use_rag in rag_configs:
                rag_label = "WITH RAG" if use_rag else "WITHOUT RAG"
                print(f"\n{'▓'*80}")
                print(f"{rag_label}")
                print(f"{'▓'*80}")
                
                for idx, test_case in enumerate(test_cases, 1):
                    for sample in range(num_samples):
                        test_num += 1
                        test_id = f"{model}_{rag_label.replace(' ', '-')}_{idx}_{sample+1}"
                        
                        print(f"\n{'─'*80}")
                        print(f"TEST {test_num}/{total_tests}: {test_case['rhyme_type']} + {test_case['features']}")
                        print(f"Theme: {test_case['theme']}")
                        print(f"Model: {model} | RAG: {use_rag}")
                        print(f"{'─'*80}")
                        
                        result = await self._run_single_test(test_id, test_case, model, use_rag, pipeline)
                        self.results.append(result)
                        
                        # Print summary
                        self._print_test_summary(result)
        
        # Print overall summary
        self._print_overall_summary()
    
    async def _run_single_test(self, test_id: str, test_case: Dict[str, Any], 
                              model: str, use_rag: bool, pipeline: AgentPipeline) -> EvaluationResult:
        """Run a single test case"""
        theme = test_case['theme']
        rhyme_type = test_case['rhyme_type']
        features = test_case['features']
        num_lines = test_case.get('num_lines', 4)  # Default to 4 if not specified
        
        # 1. Generate WITHOUT verification
        print(f"\n[1/2] Generating WITHOUT verification (RAG={use_rag})...")
        start_time = time.time()
        
        no_verify_result = await pipeline.generate_poem(
            theme=theme,
            rhyme_type=rhyme_type,
            features=features,
            num_lines=num_lines,
            use_rag=use_rag,  # KEY: Test with/without RAG
            use_verification=False  # KEY: No verification loop
        )
        
        no_verify_time = time.time() - start_time
        no_verify_poem = no_verify_result.get('poem', '')
        
        # Validate with symbolic rules
        no_verify_validation = self.validator.validate_poem(
            no_verify_poem, rhyme_type, features
        )
        
        print(f"  Time: {no_verify_time:.2f}s")
        print(f"  Valid: {no_verify_validation['valid']}")
        no_verify_accuracy = no_verify_validation.get('accuracy', 
            (no_verify_validation['correct_pairs'] / no_verify_validation['total_pairs'] * 100) if no_verify_validation['total_pairs'] > 0 else 0)
        print(f"  Accuracy: {no_verify_accuracy:.1f}% ({no_verify_validation['correct_pairs']}/{no_verify_validation['total_pairs']})")
        
        # 2. Generate WITH verification
        print(f"\n[2/2] Generating WITH verification (RAG={use_rag})...")
        start_time = time.time()
        
        with_verify_result = await pipeline.generate_poem(
            theme=theme,
            rhyme_type=rhyme_type,
            features=features,
            num_lines=num_lines,
            use_rag=use_rag,  # KEY: Test with/without RAG
            use_verification=True  # Verification loop enabled
        )
        
        with_verify_time = time.time() - start_time
        with_verify_poem = with_verify_result.get('poem', '')
        with_verify_attempts = with_verify_result.get('attempts', 0)
        
        # Validate with symbolic rules
        with_verify_validation = self.validator.validate_poem(
            with_verify_poem, rhyme_type, features
        )
        
        print(f"  Time: {with_verify_time:.2f}s")
        print(f"  Attempts: {with_verify_attempts}")
        print(f"  Valid: {with_verify_validation['valid']}")
        with_verify_accuracy = with_verify_validation.get('accuracy',
            (with_verify_validation['correct_pairs'] / with_verify_validation['total_pairs'] * 100) if with_verify_validation['total_pairs'] > 0 else 0)
        print(f"  Accuracy: {with_verify_accuracy:.1f}% ({with_verify_validation['correct_pairs']}/{with_verify_validation['total_pairs']})")
        
        # Calculate improvement
        improvement = with_verify_accuracy - no_verify_accuracy
        
        return EvaluationResult(
            test_id=test_id,
            model=model,
            use_rag=use_rag,
            theme=theme,
            rhyme_type=rhyme_type,
            features=features,
            
            no_verify_poem=no_verify_poem,
            no_verify_time=no_verify_time,
            no_verify_valid=no_verify_validation['valid'],
            no_verify_errors=no_verify_validation['errors'],
            no_verify_correct_pairs=no_verify_validation['correct_pairs'],
            no_verify_total_pairs=no_verify_validation['total_pairs'],
            
            with_verify_poem=with_verify_poem,
            with_verify_time=with_verify_time,
            with_verify_attempts=with_verify_attempts,
            with_verify_valid=with_verify_validation['valid'],
            with_verify_errors=with_verify_validation['errors'],
            with_verify_correct_pairs=with_verify_validation['correct_pairs'],
            with_verify_total_pairs=with_verify_validation['total_pairs'],
            
            improvement=improvement
        )
    
    def _print_test_summary(self, result: EvaluationResult):
        """Print summary for a single test"""
        print(f"\n┌─ SUMMARY ─────────────────────────────────────────────────────────┐")
        print(f"│ Test ID: {result.test_id:<57} │")
        print(f"│ Model: {result.model:<59} │")
        print(f"│ RAG: {str(result.use_rag):<61} │")
        print(f"│ Config: {result.rhyme_type} + {', '.join(result.features):<50} │")
        print(f"├───────────────────────────────────────────────────────────────────┤")
        print(f"│ WITHOUT Verification:                                             │")
        print(f"│   Time: {result.no_verify_time:>6.2f}s                                                  │")
        print(f"│   Accuracy: {result.no_verify_correct_pairs}/{result.no_verify_total_pairs} pairs ({result.no_verify_correct_pairs/result.no_verify_total_pairs*100 if result.no_verify_total_pairs > 0 else 0:>5.1f}%)                                    │")
        print(f"│   Valid: {str(result.no_verify_valid):<56} │")
        print(f"├───────────────────────────────────────────────────────────────────┤")
        print(f"│ WITH Verification:                                                │")
        print(f"│   Time: {result.with_verify_time:>6.2f}s                                                  │")
        print(f"│   Attempts: {result.with_verify_attempts:<52} │")
        print(f"│   Accuracy: {result.with_verify_correct_pairs}/{result.with_verify_total_pairs} pairs ({result.with_verify_correct_pairs/result.with_verify_total_pairs*100 if result.with_verify_total_pairs > 0 else 0:>5.1f}%)                                    │")
        print(f"│   Valid: {str(result.with_verify_valid):<56} │")
        print(f"├───────────────────────────────────────────────────────────────────┤")
        print(f"│ Improvement: {result.improvement:>+6.1f}%                                            │")
        print(f"└───────────────────────────────────────────────────────────────────┘")
    
    def _print_overall_summary(self):
        """Print overall evaluation summary"""
        if not self.results:
            print("\nNo results to summarize.")
            return
        
        # Calculate aggregate statistics
        total_tests = len(self.results)
        
        no_verify_valid_count = sum(1 for r in self.results if r.no_verify_valid)
        with_verify_valid_count = sum(1 for r in self.results if r.with_verify_valid)
        
        avg_no_verify_time = sum(r.no_verify_time for r in self.results) / total_tests
        avg_with_verify_time = sum(r.with_verify_time for r in self.results) / total_tests
        avg_attempts = sum(r.with_verify_attempts for r in self.results) / total_tests
        
        # Calculate accuracy
        no_verify_total_pairs = sum(r.no_verify_total_pairs for r in self.results)
        no_verify_correct_pairs = sum(r.no_verify_correct_pairs for r in self.results)
        with_verify_total_pairs = sum(r.with_verify_total_pairs for r in self.results)
        with_verify_correct_pairs = sum(r.with_verify_correct_pairs for r in self.results)
        
        no_verify_accuracy = (no_verify_correct_pairs / no_verify_total_pairs * 100) if no_verify_total_pairs > 0 else 0
        with_verify_accuracy = (with_verify_correct_pairs / with_verify_total_pairs * 100) if with_verify_total_pairs > 0 else 0
        
        avg_improvement = with_verify_accuracy - no_verify_accuracy
        
        print(f"\n{'='*80}")
        print(f"OVERALL EVALUATION SUMMARY")
        print(f"{'='*80}")
        print(f"Total Tests: {total_tests}")
        print(f"\nWITHOUT Verification:")
        print(f"  Valid poems: {no_verify_valid_count}/{total_tests} ({no_verify_valid_count/total_tests*100:.1f}%)")
        print(f"  Avg time: {avg_no_verify_time:.2f}s")
        print(f"  Overall accuracy: {no_verify_accuracy:.1f}% ({no_verify_correct_pairs}/{no_verify_total_pairs} pairs)")
        print(f"\nWITH Verification:")
        print(f"  Valid poems: {with_verify_valid_count}/{total_tests} ({with_verify_valid_count/total_tests*100:.1f}%)")
        print(f"  Avg time: {avg_with_verify_time:.2f}s")
        print(f"  Avg attempts: {avg_attempts:.1f}")
        print(f"  Overall accuracy: {with_verify_accuracy:.1f}% ({with_verify_correct_pairs}/{with_verify_total_pairs} pairs)")
        print(f"\nIMPROVEMENT:")
        print(f"  Accuracy gain: {avg_improvement:+.1f}%")
        print(f"  Time cost: {avg_with_verify_time/avg_no_verify_time:.1f}x slower")
        print(f"  Valid poem gain: {with_verify_valid_count - no_verify_valid_count:+d} ({(with_verify_valid_count - no_verify_valid_count)/total_tests*100:+.1f}%)")
        print(f"{'='*80}\n")
    
    def save_results(self, output_file: str):
        """Save results to JSON file"""
        data = {
            'metadata': {
                'model': self.model_name,
                'timestamp': datetime.now().isoformat(),
                'total_tests': len(self.results)
            },
            'results': [asdict(r) for r in self.results]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Results saved to: {output_file}")


# Test case configurations
DEFAULT_TEST_CASES = [
    # Basic stress types
    {'theme': 'αγάπη', 'rhyme_type': 'M', 'features': []},
    {'theme': 'θάλασσα', 'rhyme_type': 'F2', 'features': []},
    {'theme': 'ουρανός', 'rhyme_type': 'F3', 'features': []},
    
    # Rhyme quality types
    {'theme': 'φως', 'rhyme_type': 'M', 'features': ['PURE']},
    {'theme': 'νύχτα', 'rhyme_type': 'F2', 'features': ['RICH']},
    {'theme': 'ελπίδα', 'rhyme_type': 'F3', 'features': ['IMPERFECT']},
    
    # Combined features
    {'theme': 'καρδιά', 'rhyme_type': 'M', 'features': ['PURE', 'IDV']},
    {'theme': 'όνειρο', 'rhyme_type': 'F2', 'features': ['RICH', 'IDV']},
    {'theme': 'μνήμη', 'rhyme_type': 'F3', 'features': ['IMPERFECT', 'IDV']},
    
    # Mosaic rhymes
    {'theme': 'φεγγάρι', 'rhyme_type': 'M', 'features': ['MOSAIC']},
    {'theme': 'άνεμος', 'rhyme_type': 'F2', 'features': ['MOSAIC']},
    
    # Complex combinations
    {'theme': 'χρόνος', 'rhyme_type': 'M', 'features': ['RICH', 'MOSAIC']},
    {'theme': 'ψυχή', 'rhyme_type': 'F2', 'features': ['PURE', 'IDV', 'MOSAIC']},
]


async def main():
    parser = argparse.ArgumentParser(description='Evaluate Greek Rhyme System')
    parser.add_argument('--models', type=str, nargs='+', default=['gpt-4o'], 
                       help='Model names (space-separated) or "all" for all models')
    parser.add_argument('--num-samples', type=int, default=1, help='Number of samples per test case')
    parser.add_argument('--output', type=str, default='evaluation_results.json', help='Output file')
    parser.add_argument('--test-cases', type=str, default=None, help='JSON file with custom test cases')
    parser.add_argument('--no-rag', action='store_true', help='Skip RAG testing (only test without RAG)')
    parser.add_argument('--rag-only', action='store_true', help='Only test with RAG (skip no-RAG)')
    
    args = parser.parse_args()
    
    # Handle "all" models
    ALL_MODELS = [
        "claude-sonnet-4.5", "claude-sonnet-3.7",
        "gemini-3-pro", "gemini-2.5-pro", "gemini-2.5-flash",
        "gpt-4o", "gpt-5",
        "llama-3.3-70b", "llama-3.1-70b", "qwen-2.5-72b", "mistral-large"
    ]
    
    if args.models == ['all']:
        models = ALL_MODELS
    else:
        models = args.models
    
    # Load test cases
    if args.test_cases:
        with open(args.test_cases, 'r', encoding='utf-8') as f:
            test_cases = json.load(f)
    else:
        test_cases = DEFAULT_TEST_CASES
    
    # Determine RAG testing configuration
    test_rag = not args.no_rag
    test_no_rag = not args.rag_only
    
    # Note: In real usage, you'd pass a generate_callback that calls your LLM
    # For now, we'll use the mock
    evaluator = SystemEvaluator(models=models, generate_callback=None)
    
    await evaluator.run_evaluation(
        test_cases, 
        num_samples=args.num_samples,
        test_rag=test_rag,
        test_no_rag=test_no_rag
    )
    
    evaluator.save_results(args.output)


if __name__ == '__main__':
    asyncio.run(main())
