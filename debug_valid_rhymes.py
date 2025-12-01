from greek_phonology import classify_rhyme_pair as classify_strict
from greek_phonology_topintzi import classify_rhyme_pair_topintzi as classify_variant
from greek_phonology import extract_rhyme_domain

pairs = [
    ("τυχερή·", "βρεί"),
    ("κορμί·", "κλαδί"),
    ("κοιτάει", "κυλάει·")
]

print("=== Debugging 'Valid' Rhymes Rejected by Strict Mode ===\n")

for w1, w2 in pairs:
    print(f"--- '{w1}' vs '{w2}' ---")
    
    # 1. Check Rhyme Domains
    rd1 = extract_rhyme_domain(w1)
    rd2 = extract_rhyme_domain(w2)
    print(f"  RD1: '{rd1['rhyme_domain']}' ({rd1['rhyme_domain_phonetic']}) Stress: {rd1['stress_type']}")
    print(f"  RD2: '{rd2['rhyme_domain']}' ({rd2['rhyme_domain_phonetic']}) Stress: {rd2['stress_type']}")
    
    # 2. Strict Classification
    res_strict = classify_strict(w1, w2)
    print(f"  [Strict]  : {res_strict['type']}")
    if 'reason' in res_strict:
        print(f"    Reason: {res_strict['reason']}")
    
    # 3. Variant Classification
    res_variant = classify_variant(w1, w2)
    print(f"  [Variant] : {res_variant['type']}", end="")
    if 'imperfect_type' in res_variant:
        print(f" ({res_variant['imperfect_type']})")
    print("\n")
