#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge all individual Topintzi-variant poet corpora into unified files
"""

import json
from pathlib import Path

# List of poets
poets = [
    "FotosGiofyllis",
    "KostasOuranis",
    "MitsosPapanikolaou",
    "NapoleonLapathiotis",
    "RomosFiliras",
    "TellosAgras"
]

# === MERGE REGULAR CORPORA ===
print("=== Merging Regular Corpora (Topintzi Variant) ===")
unified_regular = {}

for poet in poets:
    corpus_file = f"corpus_{poet}_topintzi.json"
    if not Path(corpus_file).exists():
        print(f"  ⚠ Skipping {poet} - file not found")
        continue
    
    with open(corpus_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Merge into unified structure
    unified_regular.update(data)
    
    # Count examples
    if poet in data and 'examples' in data[poet]:
        count = len(data[poet]['examples'])
        print(f"  ✓ {poet}: {count} pairs")

# Save unified regular corpus
with open('unified_corpus_topintzi.json', 'w', encoding='utf-8') as f:
    json.dump(unified_regular, f, ensure_ascii=False, indent=2)

total_regular = sum(len(v['examples']) for v in unified_regular.values() if 'examples' in v)
print(f"\n✓ Saved unified_corpus_topintzi.json with {total_regular} total pairs from {len(unified_regular)} poets")

# === MERGE ENHANCED CORPORA ===
print("\n=== Merging Enhanced Corpora (Topintzi Variant) ===")
all_enhanced_entries = []
poet_stats = {}

for poet in poets:
    corpus_file = f"corpus_{poet}_enhanced_topintzi.json"
    if not Path(corpus_file).exists():
        print(f"  ⚠ Skipping {poet} - file not found")
        continue
    
    with open(corpus_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if 'entries' in data:
        # Add poet metadata to each entry
        for entry in data['entries']:
            entry['poet'] = poet
        
        all_enhanced_entries.extend(data['entries'])
        poet_stats[poet] = len(data['entries'])
        print(f"  ✓ {poet}: {len(data['entries'])} pairs")

# Save unified enhanced corpus
unified_enhanced = {
    "version": "unified_enhanced_topintzi_v1",
    "description": "Unified enhanced corpus (Topintzi Variant) from 6 Greek poets with full context",
    "total_poets": len(poet_stats),
    "total_entries": len(all_enhanced_entries),
    "poet_stats": poet_stats,
    "entries": all_enhanced_entries
}

with open('unified_corpus_enhanced_topintzi.json', 'w', encoding='utf-8') as f:
    json.dump(unified_enhanced, f, ensure_ascii=False, indent=2)

print(f"\n✓ Saved unified_corpus_enhanced_topintzi.json with {len(all_enhanced_entries)} total pairs from {len(poet_stats)} poets")

# === SUMMARY ===
print("\n" + "="*50)
print("UNIFIED TOPINTZI CORPUS FILES CREATED")
print("="*50)
print(f"📄 unified_corpus_topintzi.json: {total_regular:,} rhyme pairs")
print(f"📄 unified_corpus_enhanced_topintzi.json: {len(all_enhanced_entries):,} rhyme pairs")
print("\nPoet breakdown:")
for poet in sorted(poet_stats.keys()):
    print(f"  • {poet}: {poet_stats[poet]:,} pairs")
