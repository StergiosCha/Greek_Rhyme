from greek_phonology import analyze_mosaic_pattern, classify_rhyme_pair, extract_rhyme_domain

l1 = "Το φως της ψυχής μου για σένα καίει πιά"
l2 = "Αγάπη μου, στα χέρια σου η καρδιά"

print(f"Line 1: {l1}")
print(f"Line 2: {l2}\n")

# 1. Standard Analysis
rd1 = extract_rhyme_domain(l1)
rd2 = extract_rhyme_domain(l2)
w1 = rd1['rhyme_domain']
w2 = rd2['rhyme_domain']

print(f"Rhyme Domain 1: '{w1}' ({rd1['rhyme_domain_phonetic']}) Stress: {rd1['stress_type']}")
print(f"Rhyme Domain 2: '{w2}' ({rd2['rhyme_domain_phonetic']}) Stress: {rd2['stress_type']}")

res = classify_rhyme_pair(w1, w2)
print(f"Standard Classification: {res['type']}")

# 2. Mosaic Analysis
print("\nMosaic Analysis:")
mos = analyze_mosaic_pattern(l1, l2)
print(f"  Candidate: {mos['mosaic_candidate']}")
if 'explanation' in mos:
    print(f"  Explanation: {mos['explanation']}")
