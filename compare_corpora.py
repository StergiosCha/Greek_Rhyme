#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compare Strict Corpus vs Topintzi Variant Corpus
"""

import json
from collections import defaultdict

def load_corpus(path):
    print(f"Loading {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_pairs_set(corpus):
    """Extract set of rhyme pairs (line1, line2) for comparison."""
    pairs = set()
    pair_details = {}
    
    for poet, data in corpus.items():
        if 'examples' not in data: continue
        
        for ex in data['examples']:
            # Normalize pair for comparison (sort to handle order)
            # Actually order matters for rhyme, but let's assume consistent order
            # or just use the tuple as is.
            l1 = ex['lines'][0].strip()
            l2 = ex['lines'][1].strip()
            pair = (l1, l2)
            
            pairs.add(pair)
            pair_details[pair] = ex
            
    return pairs, pair_details

def compare_corpora():
    strict_path = "complete_corpus.json"
    topintzi_path = "complete_corpus_topintzi.json"
    
    strict = load_corpus(strict_path)
    topintzi = load_corpus(topintzi_path)
    
    print("\n=== COMPARISON REPORT ===")
    
    # 1. High Level Stats
    s_total = sum(len(p['examples']) for p in strict.values() if 'examples' in p)
    t_total = sum(len(p['examples']) for p in topintzi.values() if 'examples' in p)
    
    print(f"\nTotal Rhyme Pairs:")
    print(f"  Strict:   {s_total:,}")
    print(f"  Topintzi: {t_total:,}")
    print(f"  Diff:     +{t_total - s_total:,} pairs")
    
    # 2. Per Poet Stats
    print(f"\nBreakdown by Poet:")
    print(f"{'Poet':<25} | {'Strict':<10} | {'Topintzi':<10} | {'Diff':<10}")
    print("-" * 65)
    
    all_poets = sorted(set(strict.keys()) | set(topintzi.keys()))
    
    for poet in all_poets:
        s_count = len(strict.get(poet, {}).get('examples', []))
        t_count = len(topintzi.get(poet, {}).get('examples', []))
        diff = t_count - s_count
        print(f"{poet:<25} | {s_count:<10,} | {t_count:<10,} | +{diff:<10,}")
        
    # 3. Unique Rhymes Analysis
    print(f"\nAnalyzing Unique Rhymes in Topintzi Variant...")
    s_pairs, s_details = get_pairs_set(strict)
    t_pairs, t_details = get_pairs_set(topintzi)
    
    unique_pairs = t_pairs - s_pairs
    print(f"Found {len(unique_pairs)} unique pairs in Topintzi corpus.")
    
    # Analyze types of unique pairs
    type_counts = defaultdict(int)
    examples_by_type = defaultdict(list)
    
    for pair in unique_pairs:
        ex = t_details[pair]
        cls = ex.get('classification', 'UNKNOWN')
        
        # Extract main type (e.g. IMP-0F-TOPINTZI)
        if 'IMP-0F-TOPINTZI' in cls:
            main_type = 'IMP-0F-TOPINTZI'
        elif 'IMP-0' in cls:
            main_type = 'IMP-0'
        elif 'IMP-C' in cls:
            main_type = 'IMP-C'
        else:
            main_type = cls
            
        type_counts[main_type] += 1
        examples_by_type[main_type].append(ex)
            
    print(f"\nClassification of Unique Pairs:")
    for rtype, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  • {rtype}: {count} pairs")
        
    # Show examples
    print(f"\n=== 100 EXAMPLES OF TOPINTZI-ONLY RHYMES (IMP-0F) ===")
    print(f"(Format: Word1 vs Word2)")
    
    count = 0
    for rtype, examples in examples_by_type.items():
        if rtype != 'IMP-0F-TOPINTZI': continue
        
        for ex in examples:
            if count >= 100: break
            
            # Try to get Greek words from rhyme domain if available, else from lines
            # The 'phonetic' field currently holds the rhyme domain text (which is Greek)
            # based on how build_corpus works (w1 = rd1['rhyme_domain']).
            w1 = ex['phonetic'][0]
            w2 = ex['phonetic'][1]
            
            print(f"{count+1}. {w1} vs {w2}")
            count += 1
        if count >= 100: break

if __name__ == "__main__":
    compare_corpora()
