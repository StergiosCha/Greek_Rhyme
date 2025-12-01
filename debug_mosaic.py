from greek_phonology import analyze_mosaic_pattern

# Known valid mosaic (Solomos)
l1 = "γράψαμε τ' όνομά της"
l2 = "ωραία που φύσηξεν ο μπάτης"

print(f"Analyzing: {l1} / {l2}")
res = analyze_mosaic_pattern(l1, l2)
print(f"Mosaic Candidate: {res['mosaic_candidate']}")
if 'explanation' in res:
    print(res['explanation'])
else:
    print("No explanation (rejected early?)")
    print(f"P1: {res['line1_rhyme']['rhyme_domain_phonetic']}")
    print(f"P2: {res['line2_rhyme']['rhyme_domain_phonetic']}")
