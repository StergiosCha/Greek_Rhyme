#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge TXT and XLSX Topintzi-variant corpora into complete unified corpus
"""

import json

print("=== Merging Complete Corpus (Topintzi Variant: TXT + XLSX) ===\n")

# Load TXT corpus
print("Loading TXT corpus...")
with open('unified_corpus_topintzi.json', 'r', encoding='utf-8') as f:
    txt_corpus = json.load(f)

# Load XLSX corpus
print("Loading XLSX corpus...")
with open('rhyme_corpus_topintzi.json', 'r', encoding='utf-8') as f:
    xlsx_corpus = json.load(f)

# Merge them
complete_corpus = {}

# Add TXT poets
for poet_key, poet_data in txt_corpus.items():
    complete_corpus[poet_key] = poet_data
    complete_corpus[poet_key]['source'] = 'TXT'

# Add XLSX poets
for poet_key, poet_data in xlsx_corpus.items():
    if poet_key in complete_corpus:
        # Poet exists in both - merge examples
        print(f"  ⚠ {poet_key} exists in both corpora - merging...")
        complete_corpus[poet_key]['examples'].extend(poet_data['examples'])
        complete_corpus[poet_key]['total_rhymes'] = len(complete_corpus[poet_key]['examples'])
        complete_corpus[poet_key]['source'] = 'TXT+XLSX'
    else:
        complete_corpus[poet_key] = poet_data
        complete_corpus[poet_key]['source'] = 'XLSX'

# Save unified
with open('complete_corpus_topintzi.json', 'w', encoding='utf-8') as f:
    json.dump(complete_corpus, f, ensure_ascii=False, indent=2)

# Calculate stats
total_pairs = sum(len(p['examples']) for p in complete_corpus.values() if 'examples' in p)
total_poets = len(complete_corpus)

print(f"\n✓ Saved complete_corpus_topintzi.json")
print(f"\n{'='*60}")
print(f"COMPLETE UNIFIED CORPUS (TOPINTZI VARIANT)")
print(f"{'='*60}")
print(f"Total poets: {total_poets}")
print(f"Total rhyme pairs: {total_pairs:,}")
print(f"\nPoet breakdown:")

for poet_key in sorted(complete_corpus.keys()):
    poet = complete_corpus[poet_key]
    if 'examples' in poet:
        count = len(poet['examples'])
        source = poet.get('source', 'UNKNOWN')
        poet_name = poet.get('poet', poet_key)
        print(f"  • {poet_name}: {count:,} pairs ({source})")

print(f"\n{'='*60}")
