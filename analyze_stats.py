import json
from collections import Counter

with open("rhyme_corpus.json", "r") as f:
    corpus = json.load(f)

print(f"Corpus Keys: {list(corpus.keys())}")

palamas_stats = Counter()
total_palamas = 0
imp0_examples = []
idv_examples = []
pisti_xario_found = False

for poet, data in corpus.items():
    if "ΠΑΛ" in poet:
        for ex in data['examples']:
            total_palamas += 1
            cls = ex['classification']
            feats = ex['features']
            
            if "IMPERFECT" in cls:
                palamas_stats['IMPERFECT'] += 1
                if "IMP-C" in feats: palamas_stats['IMP-C'] += 1
                if "IMP-0" in feats: palamas_stats['IMP-0'] += 1
                if "IMP-V" in feats: palamas_stats['IMP-V'] += 1
            elif "MOSAIC" in cls:
                palamas_stats['MOSAIC'] += 1
            else:
                palamas_stats['PURE/RICH'] += 1
            
            if "IDV" in feats:
                palamas_stats['IDV'] += 1
                if len(idv_examples) < 5: idv_examples.append(ex['lines'])

            if "IMP-0" in feats:
                if len(imp0_examples) < 5: imp0_examples.append(ex)
            
            # Check specific false positives
            l1 = ex['lines'][0]
            l2 = ex['lines'][1]
            
            if "κλέφτης" in l1 and "μένει" in l2:
                print(f"FAILURE: Found kleftis/meni! Class: {cls}")
            if "ιδώ" in l1 and "κορμί" in l2:
                print(f"FAILURE: Found iDo/kormi! Class: {cls}")
                print(f"  Phonetic: {ex['phonetic']}")
                print(f"  Features: {ex['features']}")
                print(f"  Lines: {ex['lines']}")
            if "φτερά" in l1 and "καλύβι μας" in l2:
                print(f"FAILURE: Found ftera/kalivi mas! Class: {cls}")
            
            # Check classification format
            if "IMPERFECT" in cls and not ("M-" in cls or "F2-" in cls or "F3-" in cls):
                 print(f"WARNING: Missing stress type in {cls}")

print(f"Total Palamas Pairs: {total_palamas}")
print("Stats:")
for k, v in palamas_stats.items():
    print(f"  {k}: {v} ({v/total_palamas*100:.1f}%)")

print("\nSample IMP-0:")
for ex in imp0_examples:
    print(f"  {ex['lines'][0]} / {ex['lines'][1]} ({ex['classification']})")

print("\nSample IDV:")
for lines in idv_examples:
    print(f"  {lines[0]} / {lines[1]}")
