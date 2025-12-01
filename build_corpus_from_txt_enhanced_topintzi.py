#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build ENHANCED corpus from TXT files (Topintzi Variant)
Captures IMP-0F (Open vs Closed) rhymes.
"""

import json
from pathlib import Path
from greek_phonology import extract_rhyme_domain, extract_pre_rhyme_vowel
from greek_phonology_topintzi import classify_rhyme_pair_topintzi


def parse_txt_file(filepath: str):
    """Parse TXT file and extract clean lines."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='utf-16') as f:
            lines = f.readlines()
    
    clean_lines = []
    for line in lines:
        line = line.strip()
        if not line: continue
        if line.isupper() and len(line) < 50: continue
        if line[0] in ['#', '*', '-', '=']: continue
        if len(line) >= 10:
            clean_lines.append(line)
    return clean_lines


def build_enhanced_corpus_from_txt_topintzi(txt_path: str, output_path: str):
    """Build enhanced corpus with context from TXT file (Topintzi Variant)."""
    
    print(f"Processing {txt_path} (Topintzi Enhanced)...")
    all_lines = parse_txt_file(txt_path)
    print(f"  Extracted {len(all_lines)} lines")
    
    entries = []
    
    for i in range(len(all_lines)):
        line1 = all_lines[i]
        if len(line1) < 4: continue
        
        rd1 = extract_rhyme_domain(line1)
        w1 = rd1['rhyme_domain']
        
        for j in range(1, 4):
            if i + j >= len(all_lines): break
            
            line2 = all_lines[i + j]
            if len(line2) < 4: continue
            
            rd2 = extract_rhyme_domain(line2)
            w2 = rd2['rhyme_domain']
            
            # Use Topintzi Classifier
            res = classify_rhyme_pair_topintzi(w1, w2)
            
            if res['type'] == 'NONE':
                continue
            
            # Build context
            context_start = max(0, i - 1)
            context_end = min(len(all_lines), i + j + 2)
            context_lines = all_lines[context_start:context_end]
            
            rhyme_line1_pos = i - context_start
            rhyme_line2_pos = (i + j) - context_start
            
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
            
            idv1 = extract_pre_rhyme_vowel(w1)
            idv2 = extract_pre_rhyme_vowel(w2)
            if idv1 and idv2 and idv1 == idv2:
                features.append("IDV")
                classification += "-IDV"
            
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
    
    poet_name = Path(txt_path).stem
    output_corpus = {
        "version": "enhanced_txt_topintzi_v1",
        "poet": poet_name,
        "source": str(txt_path),
        "variant": "Topintzi (IMP-0F allowed)",
        "total_entries": len(entries),
        "entries": entries
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_corpus, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved to {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python build_corpus_from_txt_enhanced_topintzi.py input.txt [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"{Path(input_file).stem}_enhanced_topintzi.json"
    
    build_enhanced_corpus_from_txt_topintzi(input_file, output_file)
