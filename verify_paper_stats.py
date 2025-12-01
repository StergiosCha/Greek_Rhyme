#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify corpus statistics against Topintzi et al. (2019) findings.
Paper benchmarks:
- Solomos: High Pure (~63%), High IDV (~25%), Low Imperfect (~0% in Hymn)
- Palamas: High Imperfect (~50%), Low Pure (~26%)
"""

import json
from collections import defaultdict

def calculate_stats(poet_data):
    examples = poet_data.get('examples', [])
    total = len(examples)
    if total == 0:
        return None
        
    stats = defaultdict(int)
    
    for ex in examples:
        feats = ex.get('features', [])
        classification = ex.get('classification', '')
        
        # Main types
        if 'PURE' in feats or 'PURE' in classification:
            stats['PURE'] += 1
        if 'RICH' in feats or 'RICH' in classification:
            stats['RICH'] += 1
        if 'IMPERFECT' in feats or 'IMPERFECT' in classification:
            stats['IMPERFECT'] += 1
        if 'MOS' in feats or 'MOSAIC' in classification:
            stats['MOSAIC'] += 1
            
        # IDV (Pre-rhyme Identical Vowel)
        if 'IDV' in feats:
            stats['IDV'] += 1
            
    # Calculate percentages
    results = {k: (v / total) * 100 for k, v in stats.items()}
    results['total_pairs'] = total
    return results

def verify_paper_stats():
    print("=== Verifying Corpus Stats against Topintzi et al. (2019) ===\n")
    
    with open('complete_corpus.json', 'r', encoding='utf-8') as f:
        corpus = json.load(f)
        
    # 1. Dionysios Solomos (ΣΛΜ)
    print("--- Dionysios Solomos (ΣΛΜ) ---")
    solomos = corpus.get('ΣΛΜ')
    if solomos:
        stats = calculate_stats(solomos)
        print(f"Total Pairs: {stats['total_pairs']}")
        print(f"PURE:      {stats.get('PURE', 0):.1f}%  (Paper: ~63% in Hymn)")
        print(f"IDV:       {stats.get('IDV', 0):.1f}%   (Paper: ~25%)")
        print(f"IMPERFECT: {stats.get('IMPERFECT', 0):.1f}% (Paper: ~0% in Hymn)")
        print(f"RICH:      {stats.get('RICH', 0):.1f}%")
    else:
        print("Solomos not found in corpus")
        
    print("\n--- Kostis Palamas (ΠΑΛ) ---")
    palamas = corpus.get('ΠΑΛ')
    if palamas:
        stats = calculate_stats(palamas)
        print(f"Total Pairs: {stats['total_pairs']}")
        print(f"PURE:      {stats.get('PURE', 0):.1f}%  (Paper: ~26% in Gypsy)")
        print(f"IMPERFECT: {stats.get('IMPERFECT', 0):.1f}% (Paper: ~50% in Gypsy)")
        print(f"IDV:       {stats.get('IDV', 0):.1f}%")
        print(f"RICH:      {stats.get('RICH', 0):.1f}%")
    else:
        print("Palamas not found in corpus")

    # Check Mavilis if available (Paper: High Rich ~57%)
    # I don't think Mavilis is in the 12 poets, but let's check keys
    print("\n--- Other Poets (Check for Mavilis) ---")
    for poet in corpus.keys():
        if "Mavilis" in poet or "Lorentzos" in poet:
            print(f"Found {poet}!")
            stats = calculate_stats(corpus[poet])
            print(f"RICH: {stats.get('RICH', 0):.1f}% (Paper: ~57%)")

if __name__ == "__main__":
    verify_paper_stats()
