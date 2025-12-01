#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge TXT and XLSX ENHANCED Topintzi-variant corpora
"""

import json

print("=== Merging Complete Enhanced Corpus (Topintzi Variant: TXT + XLSX) ===\n")

# Load TXT enhanced corpus
print("Loading TXT enhanced corpus...")
with open('unified_corpus_enhanced_topintzi.json', 'r', encoding='utf-8') as f:
    txt_enhanced = json.load(f)

# Load XLSX enhanced corpus
print("Loading XLSX enhanced corpus...")
with open('rhyme_corpus_enhanced_topintzi.json', 'r', encoding='utf-8') as f:
    xlsx_enhanced = json.load(f)

# Merge entries
all_entries = []

# Add TXT entries
if 'entries' in txt_enhanced:
    for entry in txt_enhanced['entries']:
        entry['source'] = 'TXT'
        all_entries.append(entry)
    print(f"  Added {len(txt_enhanced['entries'])} TXT entries")

# Add XLSX entries
if 'entries' in xlsx_enhanced:
    for entry in xlsx_enhanced['entries']:
        entry['source'] = 'XLSX'
        if 'rhyme_pair' not in entry and 'lines' in entry:
            entry['rhyme_pair'] = entry.get('lines', [])
            entry['context'] = entry.get('lines', [])
        all_entries.append(entry)
    print(f"  Added {len(xlsx_enhanced['entries'])} XLSX entries")

# Create unified enhanced corpus
complete_enhanced = {
    "version": "complete_enhanced_topintzi_v1",
    "description": "Complete Greek rhyme corpus (Topintzi Variant) with full context",
    "total_entries": len(all_entries),
    "sources": ["TXT (6 poets)", "XLSX (6 poets)"],
    "entries": all_entries
}

# Save
with open('complete_corpus_enhanced_topintzi.json', 'w', encoding='utf-8') as f:
    json.dump(complete_enhanced, f, ensure_ascii=False, indent=2)

print(f"\n✓ Saved complete_corpus_enhanced_topintzi.json")
print(f"\n{'='*60}")
print(f"COMPLETE ENHANCED CORPUS (TOPINTZI VARIANT)")
print(f"{'='*60}")
print(f"Total entries: {len(all_entries):,}")

# Count by source
txt_count = sum(1 for e in all_entries if e.get('source') == 'TXT')
xlsx_count = sum(1 for e in all_entries if e.get('source') == 'XLSX')

print(f"\nBy source:")
print(f"  • TXT:  {txt_count:,} entries")
print(f"  • XLSX: {xlsx_count:,} entries")

# Count by poet (for TXT)
txt_poets = {}
for entry in all_entries:
    if entry.get('source') == 'TXT' and 'poet' in entry:
        poet = entry['poet']
        txt_poets[poet] = txt_poets.get(poet, 0) + 1

if txt_poets:
    print(f"\nTXT poets:")
    for poet, count in sorted(txt_poets.items(), key=lambda x: -x[1]):
        print(f"  • {poet}: {count:,}")

print(f"\n{'='*60}")
