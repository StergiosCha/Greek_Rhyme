#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build enhanced corpus with full 4-line context for each rhyme pair.

Output format:
{
  "rhyme_pair": [line_i, line_j],  // The 2 rhyming lines
  "context": [line_i-1, line_i, line_j, line_j+1],  // Surrounding context
  "pair_positions": [i, j],  // Which lines in context are the rhyming pair
  "classification": "F2-PURE",
  ...
}
"""

import json
import openpyxl
from bs4 import BeautifulSoup
from greek_phonology import classify_rhyme_pair, extract_rhyme_domain, extract_pre_rhyme_vowel


def build_corpus_with_context(xlsx_path: str, output_path: str):
    """Build corpus with full context for each rhyme pair."""
    
    print(f"Loading {xlsx_path}...")
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    
    # Extract all lines from COLUMN 5 (html)
    all_lines = []
    for row in ws.iter_rows(min_row=2, values_only=True):  # Skip header
        if not row or len(row) < 5 or not row[4]:  # Column 5 is index 4
            continue
        
        cell_value = str(row[4])  # Column 5: html
        
        # Clean HTML
        if '<' in cell_value:
            soup = BeautifulSoup(cell_value, 'html.parser')
            cell_value = soup.get_text()
        
        cell_value = cell_value.strip()
        
        # Skip empty, short lines, or metadata
        if len(cell_value) >= 4 and not cell_value.isdigit():
            all_lines.append(cell_value)
    
    print(f"Extracted {len(all_lines)} lines")
    
    # Find rhyme pairs with context
    corpus_entries = []
    
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
            
            # Classify rhyme
            res = classify_rhyme_pair(w1, w2)
            
            if res['type'] == 'NONE':
                continue
            
            # Valid rhyme! Build context
            # Get surrounding lines (window of 4-6 lines depending on distance)
            context_start = max(0, i - 1)
            context_end = min(len(all_lines), i + j + 2)
            
            context_lines = all_lines[context_start:context_end]
            
            # Find positions of rhyming lines in context
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
            
            corpus_entries.append(entry)
    
    # Save
    output_corpus = {
        "version": "enhanced_v1",
        "total_entries": len(corpus_entries),
        "source": xlsx_path,
        "description": "Rhyme pairs with full surrounding context",
        "entries": corpus_entries
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_corpus, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved {len(corpus_entries)} entries to {output_path}")
    
    # Sample
    if corpus_entries:
        print(f"\n=== Sample Entry ===")
        sample = corpus_entries[100]
        print(f"Classification: {sample['classification']}")
        print(f"Rhyme pair:")
        print(f"  '{sample['rhyme_pair'][0]}'")
        print(f"  '{sample['rhyme_pair'][1]}'")
        print(f"Context ({len(sample['context'])} lines):")
        for idx, line in enumerate(sample['context']):
            marker = "→" if idx in sample['rhyme_positions'] else " "
            print(f"  {marker} {line[:60]}")


if __name__ == "__main__":
    import sys
    
    input_file = sys.argv[1] if len(sys.argv) > 1 else "GLC_Anemoskala_select_text.xlsx"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "rhyme_corpus_enhanced.json"
    
    build_corpus_with_context(input_file, output_file)
