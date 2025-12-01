from greek_phonology import classify_rhyme_pair, extract_rhyme_domain

line165 = "Το παινεμένο αγιόκλημα να σε τυλίγω στάσου,"
line166 = "με τα χλωμά μου δάχτυλα να πλέχω τα μαλλιά σου,"

print(f"Line 165: {line165}")
rd1 = extract_rhyme_domain(line165)
print(f"  Rhyme domain: '{rd1['rhyme_domain']}'")
print(f"  Stress type: {rd1['stress_type']}")
print(f"  Phonetic: {rd1['rhyme_domain_phonetic']}")

print(f"\nLine 166: {line166}")
rd2 = extract_rhyme_domain(line166)
print(f"  Rhyme domain: '{rd2['rhyme_domain']}'")
print(f"  Stress type: {rd2['stress_type']}")
print(f"  Phonetic: {rd2['rhyme_domain_phonetic']}")

result = classify_rhyme_pair(rd1['rhyme_domain'], rd2['rhyme_domain'])
print(f"\nClassification: {result['type']}")
