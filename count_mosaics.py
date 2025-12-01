import json

with open("rhyme_corpus.json", "r") as f:
    corpus = json.load(f)

mosaic_count = 0
examples = []

for poet, data in corpus.items():
    for ex in data['examples']:
        if "MOS" in ex['features'] or "MOSAIC" in ex['classification']:
            mosaic_count += 1
            if len(examples) < 10:
                examples.append(ex)

print(f"Total Mosaic Rhymes found: {mosaic_count}")
print("\nSample Examples:")
for ex in examples:
    print(f"- {ex['lines'][0]} / {ex['lines'][1]}")
    print(f"  Class: {ex['classification']}")
    print(f"  Phonetic: {ex['phonetic']}")
