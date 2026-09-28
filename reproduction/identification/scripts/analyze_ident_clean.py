"""
Analyze identification evaluation results with CLEANED data (removing UNKNOWN/noisy labels)
"""

import json
import statistics
import sys
from collections import defaultdict

def analyze_results_cleaned(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"\n{'='*80}")
    print(f"CLEANED ANALYSIS: {filename}")
    print(f"{'='*80}")
    print(f"Total raw tests: {len(results)}")
    
    # FILTER: Remove tests where 'UNKNOWN' is in true features
    cleaned_results = []
    skipped_count = 0
    
    for r in results:
        # Check features for 'UNKNOWN'
        if 'UNKNOWN' in r['true_features']:
            skipped_count += 1
            continue
            
        # Also strictly require a valid rhyme type (M, F2, F3) in truth
        if r['true_rhyme_type'] not in ['M', 'F2', 'F3']:
            skipped_count += 1
            continue
            
        cleaned_results.append(r)
        
    print(f"Skipped {skipped_count} noisy/unknown tests.")
    print(f"Valid tests for analysis: {len(cleaned_results)}")
    
    if not cleaned_results:
        print("No valid results remaining!")
        return

    results = cleaned_results
    
    # Overall Accuracy
    rt_acc = sum(r['rhyme_type_correct'] for r in results) / len(results) * 100
    feat_acc = sum(r['features_correct'] for r in results) / len(results) * 100
    avg_f1 = statistics.mean(r['features_f1'] for r in results)
    
    print(f"\n📊 OVERALL ACCURACY (Verified Samples Only):")
    print(f"  Rhyme Type Accuracy: {rt_acc:.1f}%")
    print(f"  Features Exact Match: {feat_acc:.1f}%")
    print(f"  Features F1 Score:    {avg_f1:.3f}")
    
    # By Strategy
    print(f"\n🧠 BY STRATEGY:")
    strategies = set(r['strategy'] for r in results)
    for strat in sorted(strategies):
        strat_res = [r for r in results if r['strategy'] == strat]
        if not strat_res: continue
        s_rt_acc = sum(r['rhyme_type_correct'] for r in strat_res) / len(strat_res) * 100
        s_feat_acc = sum(r['features_correct'] for r in strat_res) / len(strat_res) * 100
        print(f"  {strat:<25}: RT={s_rt_acc:.1f}% | Feat={s_feat_acc:.1f}%")
        
    # By RAG
    print(f"\n📚 BY RAG:")
    with_rag = [r for r in results if r['use_rag']]
    
    if with_rag:
        r_rt = sum(r['rhyme_type_correct'] for r in with_rag) / len(with_rag) * 100
        print(f"  WITH RAG    (n={len(with_rag)}): RT={r_rt:.1f}%")
        
    no_rag = [r for r in results if not r['use_rag']]
    if no_rag:
        n_rt = sum(r['rhyme_type_correct'] for r in no_rag) / len(no_rag) * 100
        print(f"  WITHOUT RAG (n={len(no_rag)}): RT={n_rt:.1f}%")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_results_cleaned(sys.argv[1])
    else:
        print("Usage: python analyze_ident_clean.py <results_file>")
