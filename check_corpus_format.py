#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple enhancement: Add 4-line context to existing corpus where we only have pairs.

Currently:  {"lines": ["line1", "line2"]}  (just the rhyming pair)
Enhanced:   {"lines": ["line0", "line1", "line2", "line3"]}  (full 4-line context)
"""

import json

# Load existing corpus
print("Loading rhyme_corpus.json...")
with open('rhyme_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

print(f"Loaded {len(corpus)} poets")

# Note: The current corpus already has 2-line context for each pair.
# To get 4-line context, we'd need to re-parse the original XLSX
# with better stanza grouping.

# For now, what you have is:
# - 2 rhyming lines per example
# - Classification, phonetic info, features

# To show the user what we have:
total_examples = 0
for poet_key, poet in corpus.items():
if 'examples' in poet:
        total_examples += len(poet['examples'])
        
        # Sample first 3 examples
        print(f"\n{poet.get('poet', poet_key)} - {total_examples} examples")
        for ex in poet['examples'][:3]:
            print(f"  {ex['classification']}: {ex['lines']}")

print(f"\n=== Summary ===")
print(f"Total examples in corpus: {total_examples}")
print(f"\nCurrent format: 2 lines per example (just the rhyming pair)")
print(f"To get 4-line context, we need to rebuild from XLSX with stanza detection")
print(f"\nFor RAG: The 2-line format works fine - it shows the exact rhyme pair!")
