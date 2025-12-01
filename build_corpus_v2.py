#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Corpus Builder V2 with Rhyme Scheme Detection

New Features:
- Detects rhyme schemes (AABB, ABAB, ABBA, etc.)
- Supports both XLSX and TXT input files
- Labels each pair with its scheme context
- Outputs to rhyme_corpus_v2.json (preserves original)

Usage:
    python build_corpus_v2.py input.xlsx output_v2.json
    python build_corpus_v2.py input.txt output_v2.json
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from greek_phonology import classify_rhyme_pair, extract_rhyme_domain, analyze_mosaic_pattern, extract_pre_rhyme_vowel


def detect_rhyme_scheme(lines: List[str], max_stanza_size: int = 8) -> List[Dict]:
    """
    Detect rhyme scheme for lines using windowed approach.
    
    Returns list of dicts with rhyme pair info including scheme labels.
    """
    if not lines:
        return []
    
    # Build rhyme matrix for this stanza
    rhyme_map = {}  # line_idx -> rhyme_label (A, B, C, ...)
    next_label = ord('A')
    
    rhyme_pairs = []
    
    for i in range(len(lines)):
        line1 = lines[i]
        if len(line1) < 4:
            continue
        
        rd1 = extract_rhyme_domain(line1)
        w1 = rd1['rhyme_domain']
        
        # Check against next 3 lines (window size 4)
        for j in range(1, 4):
            if i + j >= len(lines):
                break
            
            line2 = lines[i + j]
            if len(line2) < 4:
                continue
            
            rd2 = extract_rhyme_domain(line2)
            w2 = rd2['rhyme_domain']
            
            # Classify rhyme
            res = classify_rhyme_pair(w1, w2)
            
            if res['type'] == 'NONE':
                continue
            
            # Valid rhyme found!
            # Assign rhyme labels (A, B, C, ...)
            if i not in rhyme_map:
                if i + j in rhyme_map:
                    # Line i+j already has a label, use same
                    rhyme_map[i] = rhyme_map[i + j]
                else:
                    # New rhyme pair, assign new label
                    rhyme_map[i] = chr(next_label)
                    rhyme_map[i + j] = chr(next_label)
                    next_label += 1
            else:
                # Line i already has label, assign to i+j
                rhyme_map[i + j] = rhyme_map[i]
            
            # Build classification string
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
            
            # Check for IDV
            idv1 = extract_pre_rhyme_vowel(w1)
            idv2 = extract_pre_rhyme_vowel(w2)
            if idv1 and idv2 and idv1 == idv2:
                features.append("IDV")
                classification += "-IDV"
            
            # Determine scheme pattern
            distance = j
            scheme_pattern = ""
            if distance == 1:
                scheme_pattern = "COUPLET(AA)"
            elif distance == 2:
                scheme_pattern = "ALTERNATE(ABA)"
            elif distance == 3:
                # Could be ABBA or ABCA
                scheme_pattern = "ENCLOSED(ABBA?)"
            
            # Store pair info
            pair_info = {
                "word1": w1,
                "word2": w2,
                "line1": line1.strip(),
                "line2": line2.strip(),
                "distance": distance,
                "classification": classification,
                "features": features,
                "scheme_pattern": scheme_pattern,
                "rhyme_labels": f"{rhyme_map.get(i, '?')}{rhyme_map.get(i+j, '?')}"
            }
            
            rhyme_pairs.append(pair_info)
    
    # Infer full scheme for this stanza
    scheme_str = ""
    for i in range(min(len(lines), max_stanza_size)):
        scheme_str += rhyme_map.get(i, 'X')
    
    # Add scheme context to all pairs
    for pair in rhyme_pairs:
        pair["stanza_scheme"] = scheme_str
    
    return rhyme_pairs


def parse_txt_file(filepath: str) -> List[Dict]:
    """
    Parse TXT file into poems/stanzas.
    Assumes blank lines separate stanzas.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines (stanzas)
    stanzas = []
    current_stanza = []
    
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip empty lines between stanzas
        if not line:
            if current_stanza:
                stanzas.append(current_stanza)
                current_stanza = []
            continue
        
        # Skip titles (lines starting with # or all caps)
        if line.startswith('#') or (line.isupper() and len(line) < 50):
            continue
        
        current_stanza.append(line)
    
    # Add last stanza
    if current_stanza:
        stanzas.append(current_stanza)
    
    return stanzas


def parse_xlsx_file(filepath: str) -> List[Dict]:
    """Parse XLSX file (existing logic from build_corpus_from_xlsx.py)"""
    import openpyxl
    from bs4 import BeautifulSoup
    
    wb = openpyxl.load_workbook(filepath)
    ws = wb.active
    
    stanzas = []
    current_poem = []
    
    for row in ws.iter_rows(values_only=True):
        if not row or not row[0]:
            continue
        
        cell_value = str(row[0])
        
        # Clean HTML if present
        if '<' in cell_value:
            soup = BeautifulSoup(cell_value, 'html.parser')
            cell_value = soup.get_text()
        
        cell_value = cell_value.strip()
        
        if not cell_value or len(cell_value) < 4:
            # Empty line, end of stanza
            if current_poem:
                stanzas.append(current_poem)
                current_poem = []
            continue
        
        current_poem.append(cell_value)
    
    if current_poem:
        stanzas.append(current_poem)
    
    return stanzas


def build_corpus_v2(input_path: str, output_path: str):
    """
    Build enhanced corpus with rhyme scheme detection.
    """
    input_path = Path(input_path)
    
    print(f"Building corpus from: {input_path}")
    
    # Parse input based on file type
    if input_path.suffix.lower() == '.txt':
        stanzas = parse_txt_file(str(input_path))
        print(f"Parsed {len(stanzas)} stanzas from TXT")
    elif input_path.suffix.lower() in ['.xlsx', '.xls']:
        stanzas = parse_xlsx_file(str(input_path))
        print(f"Parsed {len(stanzas)} stanzas from XLSX")
    else:
        raise ValueError(f"Unsupported file type: {input_path.suffix}")
    
    # Process all stanzas
    all_pairs = []
    
    for stanza_idx, lines in enumerate(stanzas):
        if len(lines) < 2:
            continue
        
        # Detect rhymes and schemes
        pairs = detect_rhyme_scheme(lines)
        
        # Add metadata
        for pair in pairs:
            pair["stanza_id"] = stanza_idx
            pair["source_file"] = input_path.name
        
        all_pairs.extend(pairs)
    
    # Save to JSON
    corpus = {
        "version": "2.0",
        "source": str(input_path),
        "total_pairs": len(all_pairs),
        "features": [
            "rhyme_scheme_detection",
            "distance_labels",
            "stanza_context",
            "full_line_preservation"
        ],
        "pairs": all_pairs
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved {len(all_pairs)} rhyme pairs to {output_path}")
    
    # Print statistics
    schemes = {}
    for pair in all_pairs:
        scheme = pair.get('stanza_scheme', 'UNKNOWN')
        schemes[scheme] = schemes.get(scheme, 0) + 1
    
    print(f"\n=== Rhyme Scheme Statistics ===")
    for scheme, count in sorted(schemes.items(), key=lambda x: -x[1])[:10]:
        print(f"  {scheme}: {count} pairs")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python build_corpus_v2.py input_file [output_file]")
        print("  input_file: .txt or .xlsx file")
        print("  output_file: defaults to rhyme_corpus_v2.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "rhyme_corpus_v2.json"
    
    build_corpus_v2(input_file, output_file)
