from greek_phonology import classify_rhyme_pair, extract_rhyme_domain, g2p_greek

# Deep dive into why this is being classified as rhyming
line1 = "τυχερό"
line2 = "δαρτός"

print("=== PHONETIC ANALYSIS ===\n")
print(f"Word 1: {line1}")
p1 = g2p_greek(line1)
print(f"  Phonetic: {p1}")
print(f"  Rhyme domain: {extract_rhyme_domain(line1)}")

print(f"\nWord 2: {line2}")
p2 = g2p_greek(line2)
print(f"  Phonetic: {p2}")
print(f"  Rhyme domain: {extract_rhyme_domain(line2)}")

result = classify_rhyme_pair(line1, line2)
print(f"\n=== CLASSIFICATION (BUG?) ===")
print(f"Type: {result['type']}")
print(f"Subtype: {result.get('subtype', 'N/A')}")
print(f"Details: {result.get('details', 'N/A')}")

print(f"\n=== SHOULD RHYME? ===")
print(f"User says: NO")
print(f"System says: {result['type']}")
print(f"\n❌ BUG: System is too lenient on IMPERFECT rhymes!")
