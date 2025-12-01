import pandas as pd
import re
import json
import sys
import os
from collections import defaultdict
from greek_phonology import analyze_mosaic_pattern, extract_pre_rhyme_vowel, extract_rhyme_domain
from greek_phonology_topintzi import classify_rhyme_pair_topintzi
import html
import unicodedata

# Mapping for work codes
POET_MAPPING = {
    'ΒΡΤ': 'Aristotelis Valaoritis',
    'ΚΑΛ': 'Andreas Kalvos',
    'ΚΑΡ': 'Kostas Karyotakis',
    'ΚΒΦ': 'C.P. Cavafy',
    'ΠΑΛ': 'Kostis Palamas',
    'ΣΛΜ': 'Dionysios Solomos'
}

def clean_html(raw_html):
    if not isinstance(raw_html, str):
        return ""
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    cleantext = html.unescape(cleantext)
    return cleantext.strip()

def build_corpus_topintzi(xlsx_path, output_path):
    print(f"Loading {xlsx_path} (Topintzi Variant)...")
    try:
        df = pd.read_excel(xlsx_path)
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return

    corpus = {}
    grouped = df.groupby('work')
    total_pairs = 0
    
    for work_code, group in grouped:
        poet_name = POET_MAPPING.get(work_code, work_code)
        print(f"Processing {poet_name} ({len(group)} lines)...")
        
        lines = []
        for _, row in group.iterrows():
            text = clean_html(row['html'])
            if text:
                lines.append(text)
        
        examples = []
        stats = defaultdict(int)
        
        for i in range(len(lines)):
            line1 = lines[i]
            if len(line1) < 4: continue
            
            for j in range(1, 4):
                if i + j >= len(lines): break
                
                line2 = lines[i+j]
                if len(line2) < 4: continue
                
                rd1 = extract_rhyme_domain(line1)
                rd2 = extract_rhyme_domain(line2)
                w1 = rd1['rhyme_domain']
                w2 = rd2['rhyme_domain']
                
                # Use Topintzi Classifier
                res = classify_rhyme_pair_topintzi(w1, w2)
                
                is_valid = False
                classification = ""
                features = []
                phonetic = []
                
                if res['type'] != 'NONE':
                    is_valid = True
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
                
                if not is_valid:
                    mosaic_res = analyze_mosaic_pattern(line1, line2)
                    if mosaic_res['mosaic_candidate']:
                        is_valid = True
                        classification = "MOSAIC"
                        features.append("MOS")
                        features.append("F2")
                        phonetic = [mosaic_res['line1_rhyme']['rhyme_domain_phonetic'], 
                                    mosaic_res['line2_rhyme']['rhyme_domain_phonetic']]
                        
                        if phonetic[0] == phonetic[1]:
                             def normalize(w_list):
                                 s = "".join(w_list).lower().replace("'", "").replace("’", "")
                                 s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                                 return s
                             w1_norm = normalize(mosaic_res['line1_rhyme']['words'])
                             w2_norm = normalize(mosaic_res['line2_rhyme']['words'])
                             if w1_norm == w2_norm or w1_norm.endswith(w2_norm) or w2_norm.endswith(w1_norm):
                                 is_valid = False
                
                if is_valid:
                    if not phonetic:
                         phonetic = [rd1.get('rhyme_domain_phonetic', ''), rd2.get('rhyme_domain_phonetic', '')]

                    ex = {
                        "lines": [line1, line2],
                        "line_numbers": [i+1, i+1+j],
                        "classification": classification,
                        "phonetic": phonetic,
                        "features": features
                    }
                    examples.append(ex)
                    stats['total_rhymes'] += 1
                    for f in features: stats[f] += 1
        
        final_stats = {"total_rhymes_found": stats['total_rhymes']}
        if stats['total_rhymes'] > 0:
            for k, v in stats.items():
                if k != 'total_rhymes':
                    final_stats[k] = round((v / stats['total_rhymes']) * 100, 2)
        
        corpus[work_code] = {
            "poet": poet_name,
            "poem": "Collection",
            "variant": "Topintzi (IMP-0F allowed)",
            "stats": final_stats,
            "examples": examples
        }
        
        print(f"  Found {len(examples)} rhyme pairs.")
        total_pairs += len(examples)

    print(f"Saving corpus with {total_pairs} total pairs to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)
    print("Done.")

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "GLC_Anemoskala_select_text.xlsx"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "rhyme_corpus_topintzi.json"
    build_corpus_topintzi(input_file, output_file)
