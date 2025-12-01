import pandas as pd
import re
import json
import sys
import os
from collections import defaultdict
from greek_phonology import classify_rhyme_pair, analyze_mosaic_pattern, extract_pre_rhyme_vowel



# Mapping for work codes
POET_MAPPING = {
    'ΒΡΤ': 'Aristotelis Valaoritis',
    'ΚΑΛ': 'Andreas Kalvos',
    'ΚΑΡ': 'Kostas Karyotakis',
    'ΚΒΦ': 'C.P. Cavafy',
    'ΠΑΛ': 'Kostis Palamas',
    'ΣΛΜ': 'Dionysios Solomos'
}

import html

def clean_html(raw_html):
    if not isinstance(raw_html, str):
        return ""
    # Remove HTML tags
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    # Unescape HTML entities (e.g. &nbsp; -> space)
    cleantext = html.unescape(cleantext)
    # Remove non-Greek/punctuation chars? 
    # Actually, unescape should fix &nbsp; to space, which strip() removes.
    return cleantext.strip()

def build_corpus(xlsx_path, output_path):
    print(f"Loading {xlsx_path}...")
    try:
        df = pd.read_excel(xlsx_path)
    except Exception as e:
        print(f"Error loading Excel: {e}")
        return

    corpus = {}
    
    # Group by work
    grouped = df.groupby('work')
    
    total_pairs = 0
    
    for work_code, group in grouped:
        poet_name = POET_MAPPING.get(work_code, work_code)
        print(f"Processing {poet_name} ({len(group)} lines)...")
        
        # Extract clean lines
        lines = []
        for _, row in group.iterrows():
            text = clean_html(row['html'])
            if text:
                lines.append(text)
        
        examples = []
        stats = defaultdict(int)
        
        # Iterate through lines to find rhymes
        # Window size 4 (check i against i+1, i+2, i+3)
        # To avoid duplicates (e.g. A rhymes with B, B rhymes with A), we only look forward.
        
        for i in range(len(lines)):
            line1 = lines[i]
            # Skip short lines or headers
            if len(line1) < 4: continue
            
            w1 = line1.split()[-1]
            
            for j in range(1, 4):
                if i + j >= len(lines): break
                
                line2 = lines[i+j]
                if len(line2) < 4: continue
                # Use extract_rhyme_domain to handle clitics (e.g. "kalivi mas")
                # This returns the full rhyme domain string (e.g. "kalivi mas")
                from greek_phonology import extract_rhyme_domain
                rd1 = extract_rhyme_domain(line1)
                rd2 = extract_rhyme_domain(line2)
                
                w1 = rd1['rhyme_domain']
                w2 = rd2['rhyme_domain']
                
                # Check for Rhyme
                # 1. Standard Check
                res = classify_rhyme_pair(w1, w2)
                
                is_valid = False
                classification = ""
                features = []
                phonetic = []
                
                if res['type'] != 'NONE':
                    is_valid = True
                    stress_type = res.get('subtype', 'M')
                    rhyme_type = res['type']
                    
                    # Construct classification: STRESS-TYPE (e.g. F2-PURE or F2-IMP-C-IMPERFECT)
                    if 'imperfect_type' in res:
                        imp_type = res['imperfect_type']
                        classification = f"{stress_type}-{imp_type}-{rhyme_type}"
                        features.append(imp_type)
                    else:
                        classification = f"{stress_type}-{rhyme_type}"
                    
                    features.append(stress_type)
                    features.append(rhyme_type) # PURE, RICH, IMPERFECT
                    
                    if 'details' in res:
                        features.append(res['details'])
                    
                    # Check for IDV (Pre-rhyme Identical Vowel)
                    idv1 = extract_pre_rhyme_vowel(w1)
                    idv2 = extract_pre_rhyme_vowel(w2)
                    if idv1 and idv2 and idv1 == idv2:
                        features.append("IDV")
                        classification += "-IDV"
                
                # 2. Mosaic Check (if not valid or just to be sure)
                # Only check mosaic if standard failed or if we want to be thorough
                # Mosaic check is more expensive. Let's check it if standard failed OR if it's F2/F3
                if not is_valid:
                    mosaic_res = analyze_mosaic_pattern(line1, line2)
                    if mosaic_res['mosaic_candidate']:
                        is_valid = True
                        classification = "MOSAIC"
                        features.append("MOS")
                        features.append("F2") # Usually mosaic is F2
                        # Extract phonetic from mosaic analysis
                        phonetic = [mosaic_res['line1_rhyme']['rhyme_domain_phonetic'], 
                                    mosaic_res['line2_rhyme']['rhyme_domain_phonetic']]
                        
                        # Filter out IDENTICAL rhymes (Repetition)
                        # e.g. "to Dromo" vs "to Dromo"
                        # If phonetics match perfectly AND the words are very similar/identical, skip.
                        # We want interesting rhymes, not repetition.
                        if phonetic[0] == phonetic[1]:
                             # Check if words are also identical (or close)
                             # mosaic_res['line1_rhyme']['words'] is a list of words.
                             # Normalize: remove punctuation, lowercase, strip accents
                             import unicodedata
                             def normalize(w_list):
                                 s = "".join(w_list).lower().replace("'", "").replace("’", "")
                                 # Strip accents
                                 s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                                 return s
                                 
                             w1_norm = normalize(mosaic_res['line1_rhyme']['words'])
                             w2_norm = normalize(mosaic_res['line2_rhyme']['words'])
                             
                             # Reject if one is contained in the other (e.g. "luludi" in "menaluludi")
                             # Or if they are identical
                             if w1_norm == w2_norm or w1_norm.endswith(w2_norm) or w2_norm.endswith(w1_norm):
                                 is_valid = False # Reject identical repetition
                
                if is_valid:
                    # Add to examples
                    # Limit examples per poet to avoid huge file? 
                    # Let's keep all for now, we can filter later.
                    
                    # If phonetic wasn't set by mosaic
                    if not phonetic:
                         # We need to re-extract or just use placeholders.
                         # classify_rhyme_pair doesn't return phonetics directly in the dict (it returns type).
                         # We can call extract_rhyme_domain to get phonetics.
                         from greek_phonology import extract_rhyme_domain
                         rd1 = extract_rhyme_domain(line1)
                         rd2 = extract_rhyme_domain(line2)
                         phonetic = [rd1.get('rhyme_domain_phonetic', ''), rd2.get('rhyme_domain_phonetic', '')]

                    ex = {
                        "lines": [line1, line2],
                        "line_numbers": [i+1, i+1+j], # Relative to start of processing
                        "classification": classification,
                        "phonetic": phonetic,
                        "features": features
                    }
                    examples.append(ex)
                    
                    # Update stats
                    stats['total_rhymes'] += 1
                    for f in features:
                        stats[f] += 1
        
        # Calculate percentages for stats
        final_stats = {"total_rhymes_found": stats['total_rhymes']}
        if stats['total_rhymes'] > 0:
            for k, v in stats.items():
                if k != 'total_rhymes':
                    final_stats[k] = round((v / stats['total_rhymes']) * 100, 2)
        
        corpus[work_code] = {
            "poet": poet_name,
            "poem": "Collection", # Generic
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
    import sys
    input_file = sys.argv[1] if len(sys.argv) > 1 else "GLC_Anemoskala_select_text.xlsx"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "rhyme_corpus.json"
    build_corpus(input_file, output_file)
