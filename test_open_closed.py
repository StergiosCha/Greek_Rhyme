from greek_phonology import classify_rhyme_pair as classify_strict
from greek_phonology_topintzi import classify_rhyme_pair_topintzi as classify_variant

pairs = [
    ("τυχερό", "δαρτό"),   # Should RHYME (Pure) in BOTH
    ("τυχερό", "δαρτός")   # Should REJECT in Strict, ACCEPT in Variant
]

print("=== Verifying Strict vs Topintzi Variant ===\n")

for w1, w2 in pairs:
    print(f"--- '{w1}' vs '{w2}' ---")
    
    # Strict
    res_strict = classify_strict(w1, w2)
    print(f"  [Strict]  : {res_strict['type']}")
    
    # Variant
    res_variant = classify_variant(w1, w2)
    print(f"  [Variant] : {res_variant['type']}", end="")
    if 'imperfect_type' in res_variant:
        print(f" ({res_variant['imperfect_type']})")
    else:
        print()
    print()
