"""
Re-parse results using corrected parser
"""
import json
from verification_utils import parse_llm_rhyme_output

# Load checkpoint instead of results file
input_file = "identification_checkpoint_gpt_4o.json"
output_file = "identification_results_gpt_4o_PARTIAL_FIXED.json"

print(f"Loading {input_file}...")
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)
    results = data['results']

print(f"Re-parsing {len(results)} results...")

for i, r in enumerate(results):
    raw = r['raw_output']
    parsed = parse_llm_rhyme_output(raw)
    
    r['predicted_rhyme_type'] = parsed.get('rhyme_type')
    r['predicted_features'] = parsed.get('features', [])
    r['raw_code'] = parsed.get('raw_code')
    
    # Recalculate accuracy
    r['rhyme_type_correct'] = (r['predicted_rhyme_type'] == r['true_rhyme_type'])
    
    true_features_set = set(r['true_features'])
    pred_features_set = set(r['predicted_features'])
    
    if not true_features_set and not pred_features_set:
        r['features_correct'] = True
        r['features_precision'] = 1.0
        r['features_recall'] = 1.0
        r['features_f1'] = 1.0
    else:
        r['features_correct'] = (true_features_set == pred_features_set)
        
        if pred_features_set:
            r['features_precision'] = len(true_features_set & pred_features_set) / len(pred_features_set)
        else:
            r['features_precision'] = 1.0 if not true_features_set else 0.0
            
        if true_features_set:
            r['features_recall'] = len(true_features_set & pred_features_set) / len(true_features_set)
        else:
            r['features_recall'] = 1.0 if not pred_features_set else 0.0
            
        if r['features_precision'] + r['features_recall'] > 0:
            r['features_f1'] = 2 * (r['features_precision'] * r['features_recall']) / (r['features_precision'] + r['features_recall'])
        else:
            r['features_f1'] = 0.0
            
    if i % 10 == 0:
        print(f"  Processed {i}/{len(results)}")

print(f"Saving fixed results to {output_file}...")
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("Done!")
