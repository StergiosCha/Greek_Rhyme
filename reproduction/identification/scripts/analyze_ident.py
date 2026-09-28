"""
Analyze identification evaluation results
"""

import json
import statistics
from collections import defaultdict
import sys

def analyze_results(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    print(f"\n{'='*80}")
    print(f"ANALYSIS: {filename}")
    print(f"{'='*80}")
    print(f"Total tests: {len(results)}")
    
    # Overall Accuracy
    rt_acc = sum(r['rhyme_type_correct'] for r in results) / len(results) * 100
    feat_acc = sum(r['features_correct'] for r in results) / len(results) * 100
    avg_f1 = statistics.mean(r['features_f1'] for r in results)
    
    print(f"\n📊 OVERALL:")
    print(f"  Rhyme Type Accuracy: {rt_acc:.1f}%")
    print(f"  Features Exact Match: {feat_acc:.1f}%")
    print(f"  Features F1 Score:    {avg_f1:.3f}")
    
    # By Strategy
    print(f"\n🧠 BY STRATEGY:")
    strategies = set(r['strategy'] for r in results)
    for strat in sorted(strategies):
        strat_res = [r for r in results if r['strategy'] == strat]
        s_rt_acc = sum(r['rhyme_type_correct'] for r in strat_res) / len(strat_res) * 100
        s_feat_acc = sum(r['features_correct'] for r in strat_res) / len(strat_res) * 100
        s_f1 = statistics.mean(r['features_f1'] for r in strat_res)
        print(f"  {strat:<25}: RT={s_rt_acc:.1f}% | Feat={s_feat_acc:.1f}% | F1={s_f1:.3f}")
        
    # By RAG
    print(f"\n📚 BY RAG:")
    with_rag = [r for r in results if r['use_rag']]
    no_rag = [r for r in results if not r['use_rag']]
    
    if with_rag:
        r_rt = sum(r['rhyme_type_correct'] for r in with_rag) / len(with_rag) * 100
        r_f1 = statistics.mean(r['features_f1'] for r in with_rag)
        print(f"  WITH RAG    (n={len(with_rag)}): RT={r_rt:.1f}% | F1={r_f1:.3f}")
        
    if no_rag:
        n_rt = sum(r['rhyme_type_correct'] for r in no_rag) / len(no_rag) * 100
        n_f1 = statistics.mean(r['features_f1'] for r in no_rag)
        print(f"  WITHOUT RAG (n={len(no_rag)}): RT={n_rt:.1f}% | F1={n_f1:.3f}")
        
    # By Rhyme Type
    print(f"\n📝 BY RHYME TYPE:")
    types = set(r['true_rhyme_type'] for r in results)
    for rt in sorted(types):
        rt_res = [r for r in results if r['true_rhyme_type'] == rt]
        acc = sum(r['rhyme_type_correct'] for r in rt_res) / len(rt_res) * 100
        print(f"  {rt:<5} (n={len(rt_res)}): Accuracy={acc:.1f}%")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_results(sys.argv[1])
    else:
        print("Usage: python analyze_ident.py <results_file>")
