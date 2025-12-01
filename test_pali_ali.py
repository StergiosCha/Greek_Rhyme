from greek_phonology import classify_rhyme_pair, extract_rhyme_domain

w1 = "πάλι"
w2 = "αλί"

print(f"Testing '{w1}' vs '{w2}'...\n")

# 1. Check Rhyme Domains & Stress
rd1 = extract_rhyme_domain(w1)
rd2 = extract_rhyme_domain(w2)
print(f"Word 1: {rd1['rhyme_domain']} ({rd1['rhyme_domain_phonetic']}) Stress: {rd1['stress_type']}")
print(f"Word 2: {rd2['rhyme_domain']} ({rd2['rhyme_domain_phonetic']}) Stress: {rd2['stress_type']}")

# 2. Classify
res = classify_rhyme_pair(w1, w2)
print(f"\nResult: {res['type']}")
if 'reason' in res:
    print(f"Reason: {res['reason']}")
