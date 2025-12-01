from greek_phonology import extract_rhyme_domain, classify_rhyme_pair

l1 = "σαν ψυχομάχημα· θα πάω να ιδώ."
l2 = "Στο χώμα κοίτεται ένα κορμί."

rd1 = extract_rhyme_domain(l1)
rd2 = extract_rhyme_domain(l2)

w1 = rd1['rhyme_domain']
w2 = rd2['rhyme_domain']

print(f"Line 1 Domain: '{w1}'")
print(f"Line 2 Domain: '{w2}'")

res = classify_rhyme_pair(w1, w2)
print(f"Result: {res}")
