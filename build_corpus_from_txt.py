#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build regular corpus from TXT files (similar to build_corpus_from_xlsx.py)

Usage:
    python build_corpus_from_txt.py Data/poet.txt output.json
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


def build_corpus_from_txt(txt_path: str, output_path: str):
    """Build corpus from TXT file."""
    
    print(f"Processing {txt_path}...")
    lines = parse_txt_file(txt_path)
    print(f"  Extracted {len(lines)} lines")
    
    # Find rhyme pairs (same algorithm as XLSX version)
    examples = []
    
    for i in range(len(lines)):
        line1 = lines[i]
        if len(line1) < 4:
            continue
        
        rd1 = extract_rhyme_domain(line1)
        w1 = rd1['rhyme_domain']
        
        # Check next 3 lines
        for j in range(1, 4):
            if i + j >= len(lines):
                break
            
            line2 = lines[i + j]
            if len(line2) < 4:
                continue
            
            rd2 = extract_rhyme_domain(line2)
            w2 = rd2['rhyme_domain']
            
            # Classify
            res = classify_rhyme_pair(w1, w2)
            
            if res['type'] == 'NONE':
                continue
            
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
            
            # Store example
            examples.append({
                "lines": [line1, line2],
                "line_numbers": [i + 1, i + j + 1],
                "classification": classification,
                "phonetic": [w1, w2],
                "features": features
            })
    
    print(f"  Found {len(examples)} rhyme pairs")
    
    # Save
    poet_name = Path(txt_path).stem
    corpus = {
        poet_name: {
            "poet": poet_name,
            "source": str(txt_path),
            "total_rhymes": len(examples),
            "examples": examples
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved to {output_path}")
    
    # Sample
    if examples:
        print(f"\nSample:")
        ex = examples[0]
        print(f"  {ex['classification']}")
        print(f"  '{ex['lines'][0]}'")
        print(f"  '{ex['lines'][1]}'")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python build_corpus_from_txt.py input.txt [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"{Path(input_file).stem}_corpus.json"
    
    build_corpus_from_txt(input_file, output_file)
