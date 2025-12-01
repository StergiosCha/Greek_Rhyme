from greek_phonology import classify_rhyme_pair, extract_rhyme_domain

# Check the pair the user flagged
line1 = "ανάθεμα το τυχερό,"
line2 = "οπού με πάει, νοτιάς δαρτός,"

rd1 = extract_rhyme_domain(line1)
rd2 = extract_rhyme_domain(line2)

print(f"Line 1: {line1}")
print(f"  Rhyme domain: '{rd1['rhyme_domain']}'")
print(f"\nLine 2: {line2}")
print(f"  Rhyme domain: '{rd2['rhyme_domain']}'")

result = classify_rhyme_pair(rd1['rhyme_domain'], rd2['rhyme_domain'])

print(f"\nClassification: {result['type']}")
if result['type'] != 'NONE':
    print(f"  Subtype: {result.get('subtype', 'N/A')}")
    print(f"  Details: {result.get('details', 'N/A')}")
    
print(f"\n✓ Should this be in corpus? {result['type'] != 'NONE'}")
