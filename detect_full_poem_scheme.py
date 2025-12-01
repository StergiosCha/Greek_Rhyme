#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Rhyme Scheme Analyzer - Checks ALL line pairs in a poem/stanza

Detects complex patterns like:
- ABCABC (repeating triplets)
- ABABCDCD (double alternate)
- Cross-stanza rhyming
"""

from typing import List, Dict
from greek_phonology import classify_rhyme_pair, extract_rhyme_domain


def detect_full_poem_rhyme_scheme(lines: List[str], min_rhyme_quality: str = "PURE") -> Dict:
    """
    Detect rhyme scheme by checking ALL pairs of lines.
    
    Args:
        lines: List of poetry lines
        min_rhyme_quality: Minimum rhyme type to accept ("PURE", "RICH", "IMPERFECT")
    
    Returns:
        Dict with scheme labels, pattern name, and all rhyme connections
    """
    
    if len(lines) < 2:
        return {"scheme": "", "pattern": "NONE", "groups": {}, "connections": []}
    
    # Extract rhyme domains for all lines
    rhyme_data = []
    for i, line in enumerate(lines):
        if len(line.strip()) < 4:
            rhyme_data.append(None)
            continue
        
        rd = extract_rhyme_domain(line)
        rhyme_data.append({
            'index': i,
            'line': line,
            'domain': rd['rhyme_domain'],
            'stress': rd['stress_type']
        })
    
    # Build complete rhyme matrix - check ALL pairs
    rhyme_connections = []
    
    for i in range(len(rhyme_data)):
        if not rhyme_data[i]:
            continue
        
        for j in range(i + 1, len(rhyme_data)):
            if not rhyme_data[j]:
                continue
            
            # Same stress type required
            if rhyme_data[i]['stress'] != rhyme_data[j]['stress']:
                continue
            
            # Check if they rhyme
            w1 = rhyme_data[i]['domain']
            w2 = rhyme_data[j]['domain']
            
            result = classify_rhyme_pair(w1, w2)
            
            # Accept based on quality threshold
            accepted_types = []
            if min_rhyme_quality == "IMPERFECT":
                accepted_types = ["PURE", "RICH", "IMPERFECT"]
            elif min_rhyme_quality == "RICH":
                accepted_types = ["PURE", "RICH"]
            else:  # PURE
                accepted_types = ["PURE", "RICH"]
            
            if result['type'] in accepted_types:
                rhyme_connections.append({
                    'line1': i,
                    'line2': j,
                    'word1': w1,
                    'word2': w2,
                    'type': result['type'],
                    'distance': j - i
                })
    
    # Build rhyme groups using graph coloring
    # Lines that rhyme together get the same label
    label_map = {}
    next_label = ord('A')
    
    for conn in rhyme_connections:
        i, j = conn['line1'], conn['line2']
        
        # Check if either line already has a label
        label_i = label_map.get(i)
        label_j = label_map.get(j)
        
        if label_i and label_j:
            # Both have labels - they should be the same (merge groups)
            if label_i != label_j:
                # Merge: change all label_j to label_i
                for k, v in list(label_map.items()):
                    if v == label_j:
                        label_map[k] = label_i
        elif label_i:
            # i has label, j doesn't
            label_map[j] = label_i
        elif label_j:
            # j has label, i doesn't
            label_map[i] = label_j
        else:
            # Neither has label - create new group
            new_label = chr(next_label)
            next_label += 1
            label_map[i] = new_label
            label_map[j] = new_label
    
    # Build scheme string
    scheme_str = ""
    for i in range(len(lines)):
        if i in label_map:
            scheme_str += label_map[i]
        else:
            scheme_str += "X"  # Non-rhyming line
    
    # Group lines by rhyme label
    rhyme_groups = {}
    for idx, label in label_map.items():
        if label not in rhyme_groups:
            rhyme_groups[label] = []
        rhyme_groups[label].append(idx)
    
    # Identify pattern
    pattern_name = identify_pattern_enhanced(scheme_str, rhyme_groups)
    
    return {
        "scheme": scheme_str,
        "pattern": pattern_name,
        "groups": rhyme_groups,
        "connections": rhyme_connections,
        "total_lines": len(lines),
        "rhyming_lines": len(label_map)
    }


def identify_pattern_enhanced(scheme: str, groups: Dict) -> str:
    """Enhanced pattern detection with more schemes."""
    
    if not scheme or 'X' == scheme.replace('X', ''):
        return "UNRHYMED"
    
    # Common exact patterns
    patterns = {
        "AABB": "COUPLETS",
        "ABAB": "ALTERNATE",
        "ABBA": "ENCLOSED",
        "AAAA": "MONORHYME",
        "ABCABC": "TRIPLET REPEAT",
        "ABABCDCD": "DOUBLE ALTERNATE",
        "ABBACDDC": "DOUBLE ENCLOSED",
        "AABCCB": "TAIL RHYME",
    }
    
    if scheme in patterns:
        return patterns[scheme]
    
    # Check for repeating patterns
    if len(scheme) >= 6:
        # Check for ABABAB... (all alternate)
        if all(scheme[i] == scheme[i % 2] for i in range(len(scheme))):
            return "CONTINUOUS ALTERNATE"
        
        # Check for AABBCC... (all couplets)
        is_couplets = True
        for i in range(0, len(scheme) - 1, 2):
            if i + 1 < len(scheme) and scheme[i] != scheme[i + 1]:
                is_couplets = False
                break
        if is_couplets:
            return "CONTINUOUS COUPLETS"
    
    # Check for complex cross-rhyming
    max_group_size = max(len(g) for g in groups.values()) if groups else 0
    if max_group_size >= 3:
        return f"COMPLEX CROSS-RHYME (max {max_group_size} lines)"
    
    return f"CUSTOM ({scheme})"


if __name__ == "__main__":
    # Test with the Lapathiotis poem
    test_poem = [
        "Τα καηµένα τα πουλάκια",       # A
        "Κρύο βαρύ, χειµώνας όξω,",     # B  
        "τρέµουν οι φωτιές στα τζάκια,", # A
        "κι ένας άνεµος που φύσα",       # C
        "σβήνει µέσα µου το όξω.",       # B
        "Κι ακουµπά στο βιτρολώξω",      # B
        "το παγωµένο του µουτράκι",      # D
        "κι όλο κτυπάει τα φτερά του,",  # E
    ]
    
    print("=== ENHANCED FULL-POEM RHYME SCHEME ===\n")
    
    result = detect_full_poem_rhyme_scheme(test_poem)
    
    print(f"Scheme: {result['scheme']}")
    print(f"Pattern: {result['pattern']}")
    print(f"Rhyming lines: {result['rhyming_lines']}/{result['total_lines']}")
    
    print(f"\n=== RHYME GROUPS ===")
    for label in sorted(result['groups'].keys()):
        indices = result['groups'][label]
        print(f"\n{label} → Lines {[i+1 for i in indices]}:")
        for idx in indices:
            print(f"  {idx+1}. {test_poem[idx]}")
    
    print(f"\n=== ALL RHYME CONNECTIONS ===")
    for conn in result['connections']:
        print(f"Lines {conn['line1']+1}-{conn['line2']+1}: '{conn['word1']}' ↔ '{conn['word2']}' ({conn['type']}, distance={conn['distance']})")
