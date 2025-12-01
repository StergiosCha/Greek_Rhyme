import json

# Load unified corpus
with open('complete_corpus.json', 'r', encoding='utf-8') as f:
    corpus = json.load(f)

# Check Tellos Agras for the rhyme
agras = corpus.get('TellosAgras', {})
examples = agras.get('examples', [])

target_rhyme = None
for ex in examples:
    # Check if this is the pair
    # "στάσου" vs "μαλλιά σου"
    # Note: The corpus stores full lines or rhyme domains?
    # It stores rhyme domains in 'rhyme_pair_phonetic' or similar?
    # Let's check the 'rhyme_pair' field which has the lines
    
    lines = ex.get('lines', [])
    if len(lines) == 2:
        l1 = lines[0]
        l2 = lines[1]
        
        if "στάσου" in l1 and "μαλλιά σου" in l2:
            target_rhyme = ex
            break

if target_rhyme:
    print("✅ FOUND THE RHYME IN CORPUS!")
    print(json.dumps(target_rhyme, indent=2, ensure_ascii=False))
else:
    print("❌ RHYME NOT FOUND IN CORPUS")
