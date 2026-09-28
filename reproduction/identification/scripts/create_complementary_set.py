import json
import random
from collections import Counter

# Load corpus
with open('complete_corpus_enhanced.json') as f:
    corpus = json.load(f)

# Load golden set to avoid duplicates
with open('golden_test_set.json') as f:
    golden = json.load(f)
    golden_texts = set(p['text'] for p in golden)

print("Creating BALANCED complementary test set...")
print("="*80)

# Collect all rhyme pairs
all_pairs = []
for poet_name, poet_data in corpus.items():
    if not isinstance(poet_data, dict):
        continue
    
    pairs = []
    for key, value in poet_data.items():
        if isinstance(value, list) and len(value) > 0:
            if isinstance(value[0], dict) and 'rhyme_pair' in value[0]:
                pairs.extend(value)

    for pair in pairs:
        if isinstance(pair, dict) and 'rhyme_pair' in pair:
            text = f"{pair['rhyme_pair'][0]} / {pair['rhyme_pair'][1]}"
            if text not in golden_texts:
                pair_copy = dict(pair)
                pair_copy['poet'] = poet_name
                pair_copy['text'] = text
                all_pairs.append(pair_copy)

# Categorize by rhyme type AND features
def get_rhyme_type(classification):
    if classification.startswith('M-'):
        return 'M'
    elif classification.startswith('F2-'):
        return 'F2'
    elif classification.startswith('F3-'):
        return 'F3'
    return None

def has_feature(classification, feature):
    return feature in classification

# Build categories
m_pure = [p for p in all_pairs if get_rhyme_type(p.get('classification', '')) == 'M' and 'PURE' in p.get('classification', '')]
f3_pure = [p for p in all_pairs if get_rhyme_type(p.get('classification', '')) == 'F3' and 'PURE' in p.get('classification', '')]

mosaic_m = [p for p in all_pairs if get_rhyme_type(p.get('classification', '')) == 'M' and 'MOSAIC' in p.get('classification', '')]
mosaic_f2 = [p for p in all_pairs if get_rhyme_type(p.get('classification', '')) == 'F2' and 'MOSAIC' in p.get('classification', '')]
mosaic_f3 = [p for p in all_pairs if get_rhyme_type(p.get('classification', '')) == 'F3' and 'MOSAIC' in p.get('classification', '')]

imp_m = [p for p in all_pairs if get_rhyme_type(p.get('classification', '')) == 'M' and 'IMP' in p.get('classification', '')]
imp_f2 = [p for p in all_pairs if get_rhyme_type(p.get('classification', '')) == 'F2' and 'IMP' in p.get('classification', '')]
imp_f3 = [p for p in all_pairs if get_rhyme_type(p.get('classification', '')) == 'F3' and 'IMP' in p.get('classification', '')]

print(f"Available:")
print(f"  M-PURE: {len(m_pure)}, F3-PURE: {len(f3_pure)}")
print(f"  MOSAIC: M={len(mosaic_m)}, F2={len(mosaic_f2)}, F3={len(mosaic_f3)}")
print(f"  IMPERFECT: M={len(imp_m)}, F2={len(imp_f2)}, F3={len(imp_f3)}")

complementary = []

def add_poem(pair):
    rt = get_rhyme_type(pair.get('classification', ''))
    features = [f for f in pair.get('classification', '').split('-')[1:] if f]
    complementary.append({
        'text': pair['text'],
        'poet': pair['poet'],
        'rhyme_type': rt,
        'features': features,
        'pattern': pair.get('classification', '')
    })

# Add 2 M-PURE
if len(m_pure) >= 2:
    for p in random.sample(m_pure, 2):
        add_poem(p)
    print(f"\n✓ Added 2 M-PURE")

# Add 2 F3-PURE
if len(f3_pure) >= 2:
    for p in random.sample(f3_pure, 2):
        add_poem(p)
    print(f"✓ Added 2 F3-PURE")

# Add 6 MOSAIC - distribute across types (2 M, 2 F2, 2 F3)
if len(mosaic_m) >= 2:
    for p in random.sample(mosaic_m, 2):
        add_poem(p)
if len(mosaic_f2) >= 2:
    for p in random.sample(mosaic_f2, 2):
        add_poem(p)
if len(mosaic_f3) >= 2:
    for p in random.sample(mosaic_f3, 2):
        add_poem(p)
print(f"✓ Added 6 MOSAIC (2 M, 2 F2, 2 F3)")

# Add 4 IMPERFECT - distribute (1 M, 2 F2, 1 F3)
if len(imp_m) >= 1:
    for p in random.sample(imp_m, 1):
        add_poem(p)
if len(imp_f2) >= 2:
    for p in random.sample(imp_f2, 2):
        add_poem(p)
if len(imp_f3) >= 1:
    for p in random.sample(imp_f3, 1):
        add_poem(p)
print(f"✓ Added 4 IMPERFECT (1 M, 2 F2, 1 F3)")

print(f"\n{'='*80}")
print(f"COMPLEMENTARY TEST SET CREATED")
print(f"{'='*80}")
print(f"Total poems: {len(complementary)}")

# Save
with open('complementary_test_set.json', 'w', encoding='utf-8') as f:
    json.dump(complementary, f, ensure_ascii=False, indent=2)

print(f"\n✓ Saved to: complementary_test_set.json")

# Show summary
rt_counts = Counter(p['rhyme_type'] for p in complementary)
print(f"\nRhyme Type Breakdown:")
print(f"  M: {rt_counts.get('M', 0)}")
print(f"  F2: {rt_counts.get('F2', 0)}")
print(f"  F3: {rt_counts.get('F3', 0)}")

feature_counts = Counter()
for p in complementary:
    for f in p['features']:
        feature_counts[f] += 1
print(f"\nFeature Breakdown:")
for feat, count in sorted(feature_counts.items(), key=lambda x: -x[1]):
    print(f"  {feat}: {count}")

print(f"\nCombined with Golden Set (26 poems):")
print(f"  Total: {26 + len(complementary)} poems")
print(f"  M: {8 + rt_counts.get('M', 0)}")
print(f"  F2: {10 + rt_counts.get('F2', 0)}")
print(f"  F3: {8 + rt_counts.get('F3', 0)}")
