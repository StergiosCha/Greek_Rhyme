#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Show FULL lines from interesting rhyme schemes
"""

from detect_full_poem_scheme import detect_full_poem_rhyme_scheme

def analyze_with_full_lines(filepath: str, max_stanzas: int = 3):
    """Analyze and show complete lines."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if len(l.strip()) >= 10]
    
    print(f"=== {filepath} ===\n")
    
    # Analyze in chunks
    chunk_size = 12
    
    for stanza_num in range(max_stanzas):
        start = stanza_num * chunk_size
        if start >= len(lines):
            break
            
        chunk = lines[start:start + chunk_size]
        
        if len(chunk) < 4:
            continue
        
        result = detect_full_poem_rhyme_scheme(chunk)
        
        # Only show if interesting
        if result['rhyming_lines'] < 3:
            continue
        
        print(f"{'='*70}")
        print(f"STANZA {stanza_num + 1} - Lines {start+1} to {start+len(chunk)}")
        print(f"Scheme: {result['scheme']} ({result['pattern']})")
        print(f"{'='*70}\n")
        
        # Print all lines with their labels
        for i, line in enumerate(chunk):
            label = result['scheme'][i] if i < len(result['scheme']) else 'X'
            marker = f"[{label}]" if label != 'X' else "   "
            print(f"{i+1:2}. {marker} {line}")
        
        print(f"\n{'─'*70}")
        print("RHYME ANALYSIS:")
        print(f"{'─'*70}\n")
        
        # Show rhyme groups with full lines
        for label in sorted(result['groups'].keys()):
            indices = result['groups'][label]
            print(f"** {label} Rhyme Group ({len(indices)} lines) **")
            for idx in indices:
                print(f"  Line {idx+1}: {chunk[idx]}")
            print()
        
        # Show connections
        if result['connections']:
            print("** All Rhyme Connections **")
            for conn in result['connections']:
                dist_marker = "🔗" if conn['distance'] > 3 else "→"
                print(f"  {dist_marker} Lines {conn['line1']+1}↔{conn['line2']+1} (distance {conn['distance']}): {conn['type']}")
                print(f"     '{conn['word1']}' / '{conn['word2']}'")
            print()
        
        print()


if __name__ == "__main__":
    import sys
    filename = sys.argv[1] if len(sys.argv) > 1 else "Data/NapoleonLapathiotis.txt"
    analyze_with_full_lines(filename, max_stanzas=5)
