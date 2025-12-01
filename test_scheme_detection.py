#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze rhyme schemes in real Greek poetry
"""

from analyze_rhyme_scheme import detect_rhyme_scheme
from greek_phonology import extract_rhyme_domain, classify_rhyme_pair

# Test with a real poem chunk
poem_lines = [
    "Τα καηµένα τα πουλάκια",
    "Κρύο βαρύ, χειµώνας όξω,",
    "τρέµουν οι φωτιές στα τζάκια,",
    "κι ένας άνεµος που φύσα",
    "σβήνει µέσα µου το όξω.",
    "Κι ακουµπά στο βιτρολώξω",
    "το παγωµένο του µουτράκι",
    "κι όλο κτυπάει τα φτερά του,",
]

print("=== POEM LINES ===")
for i, line in enumerate(poem_lines, 1):
    rd = extract_rhyme_domain(line)
    print(f"{i}. {line}")
    print(f"   → Rhyme domain: '{rd['rhyme_domain']}' ({rd['stress_type']})")

print("\n=== RHYME SCHEME DETECTION ===")
result = detect_rhyme_scheme(poem_lines)

print(f"Scheme: {result['scheme']}")
print(f"Pattern: {result['pattern']}")
print(f"Rhyming lines: {result['rhyming_lines']}/{result['total_lines']}")

print(f"\n=== RHYME GROUPS ===")
for label, indices in sorted(result['groups'].items()):
    print(f"\n{label} rhyme group (lines {[i+1 for i in indices]}):")
    for idx in indices:
        print(f"  {idx+1}. {poem_lines[idx]}")
        rd = extract_rhyme_domain(poem_lines[idx])
        print(f"     → {rd['rhyme_domain']}")
    
    # Show rhyme verification
    if len(indices) >= 2:
        w1 = extract_rhyme_domain(poem_lines[indices[0]])['rhyme_domain']
        w2 = extract_rhyme_domain(poem_lines[indices[1]])['rhyme_domain']
        res = classify_rhyme_pair(w1, w2)
        print(f"     ✓ Verified: {res['type']}")
