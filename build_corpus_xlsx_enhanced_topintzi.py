import json
import openpyxl
from bs4 import BeautifulSoup
from greek_phonology import extract_rhyme_domain, extract_pre_rhyme_vowel
from greek_phonology_topintzi import classify_rhyme_pair_topintzi

def build_corpus_with_context_topintzi(xlsx_path: str, output_path: str):
    """Build enhanced corpus with full context (Topintzi Variant)."""
    
    print(f"Loading {xlsx_path} (Topintzi Enhanced)...")
    wb = openpyxl.load_workbook(xlsx_path)
    ws = wb.active
    
    all_lines = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or len(row) < 5 or not row[4]: continue
        cell_value = str(row[4])
        if '<' in cell_value:
            soup = BeautifulSoup(cell_value, 'html.parser')
            cell_value = soup.get_text()
        cell_value = cell_value.strip()
        if len(cell_value) >= 4 and not cell_value.isdigit():
            all_lines.append(cell_value)
    
    print(f"Extracted {len(all_lines)} lines")
    
    corpus_entries = []
    
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
            if 'details' in res: features.append(res['details'])
            
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
            
            corpus_entries.append(entry)
    
    output_corpus = {
        "version": "enhanced_xlsx_topintzi_v1",
        "total_entries": len(corpus_entries),
        "source": xlsx_path,
        "description": "Rhyme pairs with full surrounding context (Topintzi Variant)",
        "entries": corpus_entries
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_corpus, f, ensure_ascii=False, indent=2)
    
    print(f"✓ Saved {len(corpus_entries)} entries to {output_path}")

if __name__ == "__main__":
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "GLC_Anemoskala_select_text.xlsx"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "rhyme_corpus_enhanced_topintzi.json"
    build_corpus_with_context_topintzi(input_file, output_file)
