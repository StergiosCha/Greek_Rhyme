#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rhyme Scheme Analyzer - Detects patterns across entire poems

Detects schemes like:
- AABB (couplets)
- ABAB (alternate rhyme)
- ABBA (enclosed rhyme)
- AAAA (monorhyme)
- Complex patterns (ABABCDCD, etc.)
"""

from typing import List, Dict, Tuple
from greek_phonology import classify_rhyme_pair, extract_rhyme_domain


def detect_rhyme_scheme(lines: List[str], max_distance: int = 8) -> Dict:
    """
    Detect rhyme scheme across a poem.
    
    Args:
        lines: List of poetry lines
        max_distance: Maximum distance to check for rhymes (prevents false positives in long poems)
    
    Returns:
        Dict with scheme labels, pattern name, and rhyme groups
    """
    
    if len(lines) < 2:
        return {"scheme": "", "pattern": "NONE", "groups": {}}
    
    # Build rhyme matrix: which lines rhyme with which
    rhyme_matrix = {}  # {i: [j, k, ...]} - line i rhymes with lines j, k
    
    for i in range(len(lines)):
        if len(lines[i]) < 4:
            continue
        
        rd1 = extract_rhyme_domain(lines[i])
        w1 = rd1['rhyme_domain']
        
        rhyme_matrix[i] = []
        
        # Check against later lines within max_distance
        for j in range(i + 1, min(len(lines), i + max_distance + 1)):
            if len(lines[j]) < 4:
                continue
            
            rd2 = extract_rhyme_domain(lines[j])
            w2 = rd2['rhyme_domain']
            
            # Check if they rhyme
            result = classify_rhyme_pair(w1, w2)
            
            if result['type'] != 'NONE':
                rhyme_matrix[i].append(j)
                if j not in rhyme_matrix:
                    rhyme_matrix[j] = []
                rhyme_matrix[j].append(i)
    
    # Assign rhyme labels (A, B, C, ...)
    label_map = {}  # {line_index: 'A', 'B', etc.}
    next_label = ord('A')
    
    for i in range(len(lines)):
        if i in label_map:
            continue
        
        # Check if this line rhymes with any previously labeled lines
        found_label = None
        if i in rhyme_matrix:
            for rhyme_partner in rhyme_matrix[i]:
                if rhyme_partner in label_map:
                    found_label = label_map[rhyme_partner]
                    break
        
        if found_label:
            label_map[i] = found_label
        else:
            # New rhyme group
            label_map[i] = chr(next_label)
            next_label += 1
    
    # Build scheme string
    scheme_str = ""
    for i in range(len(lines)):
        if i in label_map:
            scheme_str += label_map[i]
        else:
            scheme_str += "X"  # Non-rhyming line
    
    # Identify pattern name
    pattern_name = identify_pattern(scheme_str)
    
    # Group lines by rhyme
    rhyme_groups = {}
    for idx, label in label_map.items():
        if label not in rhyme_groups:
            rhyme_groups[label] = []
        rhyme_groups[label].append(idx)
    
    return {
        "scheme": scheme_str,
        "pattern": pattern_name,
        "groups": rhyme_groups,
        "total_lines": len(lines),
        "rhyming_lines": len(label_map)
    }


def identify_pattern(scheme: str) -> str:
    """Identify common rhyme pattern names."""
    
    # Remove X's (non-rhyming) for pattern detection
    clean_scheme = scheme.replace('X', '')
    
    if not clean_scheme:
        return "UNRHYMED"
    
    # Check for common patterns
    patterns = {
        # 4-line patterns
        "AABB": "COUPLETS",
        "ABAB": "ALTERNATE",
        "ABBA": "ENCLOSED",
        "AAAA": "MONORHYME",
        
        # 6-line patterns
        "ABABCC": "QUATRAIN + COUPLET",
        "AABBCC": "TRIPLE COUPLETS",
        
        # 8-line patterns
        "ABABABCC": "OCTAVE (Sicilian)",
        "ABBAABBA": "OCTAVE (Petrarchan)",
        "ABABCDCD": "DOUBLE ALTERNATE",
        
        # 14-line patterns (sonnets)
        "ABBAABBACDECDE": "SONNET (Petrarchan)",
        "ABBAABBACDCDCD": "SONNET (Italian variant)",
        "ABABCDCDEFEFGG": "SONNET (Shakespearean)",
    }
    
    # Exact match
    if scheme in patterns:
        return patterns[scheme]
    
    # Pattern-based detection
    if len(scheme) >= 4:
        # Check first 4 lines
        first_4 = scheme[:4]
        if first_4 == "AABB":
            return f"COUPLETS (starts {scheme})"
        elif first_4 == "ABAB":
            return f"ALTERNATE (starts {scheme})"
        elif first_4 == "ABBA":
            return f"ENCLOSED (starts {scheme})"
        elif first_4 == "AAAA":
            return f"MONORHYME (starts {scheme})"
    
    # Check for repeating patterns
    if len(scheme) >= 8:
        # Check if it's ABAB repeated
        if scheme[:4] == "ABAB" and all(scheme[i:i+4] == "ABAB" for i in range(0, len(scheme)-3, 4)):
            return "REPEATED ALTERNATE"
    
    # Generic description
    unique_letters = len(set(scheme))
    if unique_letters == 1:
        return f"MONORHYME ({len(scheme)} lines)"
    elif unique_letters == 2:
        return f"TWO-RHYME SCHEME ({scheme})"
    else:
        return f"COMPLEX ({scheme})"


def analyze_poem_file(filepath: str):
    """Analyze rhyme scheme of a poem from a file."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if len(l.strip()) >= 10]
    
    # Split into stanzas (by blank lines in original - here we'll use all lines as one poem)
    # For demonstration, let's analyze in chunks of 20 lines
    
    results = []
    chunk_size = 20
    
    for start in range(0, len(lines), chunk_size):
        chunk = lines[start:start + chunk_size]
        
        if len(chunk) < 4:
            continue
        
        scheme_info = detect_rhyme_scheme(chunk)
        
        if scheme_info['scheme']:
            results.append({
                'start_line': start + 1,
                'end_line': start + len(chunk),
                'scheme': scheme_info['scheme'],
                'pattern': scheme_info['pattern'],
                'lines_preview': chunk[:4]
            })
    
    return results


if __name__ == "__main__":
    import sys
    
    # Test with example
    test_poem = [
        "Της καρδιάς μου το φτερούγισμα αψηφά το τέλος πια",  # A
        "Στη ματιά σου ονειρεύομαι, σαν το φως στη σκιά",      # A
        "Το άγγιγμα στην άκρη των χειλιών μας δυνατά",         # A
        "Σαν ποτάμι που χύνεται στη θάλασσα μακριά",          # A
        "Με του έρωτα τα κύματα να με πνίγουν ξανά",           # A
        "Στης ψυχής μου τα μυστικά βρίσκω εσένα παντού πιά",   # A
    ]
    
    print("=== Rhyme Scheme Analyzer ===\n")
    
    result = detect_rhyme_scheme(test_poem)
    
    print(f"Scheme: {result['scheme']}")
    print(f"Pattern: {result['pattern']}")
    print(f"Rhyming lines: {result['rhyming_lines']}/{result['total_lines']}")
    print(f"\nRhyme groups:")
    for label, line_indices in sorted(result['groups'].items()):
        print(f"  {label}: lines {[i+1 for i in line_indices]}")
        for idx in line_indices[:2]:  # Show first 2 of each group
            print(f"     {idx+1}. {test_poem[idx][:60]}...")
    
    # Test file if provided
    if len(sys.argv) > 1:
        print(f"\n\n=== Analyzing {sys.argv[1]} ===\n")
        results = analyze_poem_file(sys.argv[1])
        
        for r in results[:5]:  # Show first 5 chunks
            print(f"Lines {r['start_line']}-{r['end_line']}: {r['scheme']} ({r['pattern']})")
