#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build ENHANCED corpus from TXT files (with full context)

Usage:
    python build_corpus_from_txt_enhanced.py Data/poet.txt output.json
"""

import json
from pathlib import Path
from greek_phonology import classify_rhyme_pair, extract_rhyme_domain, extract_pre_rhyme_vowel


def parse_txt_file(filepath: str):
    """Parse TXT file and extract clean lines."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    clean_lines = []
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip titles/headers (all caps, short lines)
        if line.isupper() and len(line) < 50:
            continue
        
        # Skip lines starting with special characters
        if line[0] in ['#', '*', '-', '=']:
            continue
        
        # Keep if looks like poetry
        if len(line) >= 10:
            clean_lines.append(line)
    
    return clean_lines


def build_enhanced_corpus_from_txt(txt_path: str, output_path: str):
    """Build enhanced corpus with context from TXT file."""
    
    print(f"Processing {txt_path}...")
    all_lines = parse_txt_file(txt_path)
    print(f"  Extracted {len(all_lines)} lines")
    
    # Find rhyme pairs with context
    entries = []
    
    for i in range(len(all_lines)):
        line1 = all_lines[i]
        if len(line1) < 4:
            continue
        
        rd1 = extract_rhyme_domain(line1)
        w1 = rd1['rhyme_domain']
        
        # Check next 3 lines
        for j in range(1, 4):
            if i + j >= len(all_lines):
                break
            
            line2 = all_lines[i + j]
            if len(line2) < 4:
                continue
            
            rd2 = extract_rhyme_domain(line2)
            w2 = rd2['rhyme_domain']
            
            # Classify
            res = classify_rhyme_pair(w1, w2)
            
            if res['type'] == 'NONE':
                continue
            
            # Build context (surrounding lines)
            context_start = max(0, i - 1)
            context_end = min(len(all_lines), i + j + 2)
            context_lines = all_lines[context_start:context_end]
            
            # Find rhyme positions in context
            rhyme_line1_pos = i - context_start
            rhyme_line2_pos = (i + j) - context_start
            
            # Build classification
            classification = ""
            features = []
            
            stress_type = res.get('subtype', 'M')
            rhyme_type = res['type']
            
            if 'imperfect_type' in res:
                imp_type = res['imperfect_type']
                classification = f"{stress_type}-{imp_type}-{rhyme_type}"
                features.append(imp_type)
            else:
                classification = f"{stress_type}-{rhyme_type}"
            
            features.append(stress_type)
            features.append(rhyme_type)
            
            if 'details' in res:
                features.append(res['details'])
            
            # Check IDV
            idv1 = extract_pre_rhyme_vowel(w1)
            idv2 = extract_pre_rhyme_vowel(w2)
            if idv1 and idv2 and idv1 == idv2:
                features.append("IDV")
                classification += "-IDV"
            
            # Create entry
            entry = {
                "rhyme_pair": [line1, line2],
                "context": context_lines,
                "rhyme_positions": [rhyme_line1_pos, rhyme_line2_pos],
                "distance": j,
                "phonetic": [w1, w2],
                "classification": classification,
                "features": features,
                "line_indices": [i, i + j]
            }
            
            entries.append(entry)
    
    print(f"  Found {len(entries)} rhyme pairs")
    
    # Save
    poet_name = Path(txt_path).stem
    output_corpus = {
        "version": "enhanced_txt_v1",
        "poet": poet_name,
        "source": str(txt_path),
        "total_entries": len(entries),
        "entries": entries
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_corpus, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved to {output_path}")
    
    # Sample
    if entries:
        print(f"\nSample:")
        ex = entries[0]
        print(f"  {ex['classification']}")
        print(f"  Rhyme pair:")
        print(f"    '{ex['rhyme_pair'][0]}'")
        print(f"    '{ex['rhyme_pair'][1]}'")
        print(f"  Context ({len(ex['context'])} lines):")
        for idx, line in enumerate(ex['context'][:4]):
            marker = "→" if idx in ex['rhyme_positions'] else " "
            print(f"    {marker} {line[:60]}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python build_corpus_from_txt_enhanced.py input.txt [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"{Path(input_file).stem}_enhanced.json"
    
    build_enhanced_corpus_from_txt(input_file, output_file)
