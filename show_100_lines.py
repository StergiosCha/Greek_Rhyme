#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Show 100 lines with full rhyme annotation
"""

import sys
from detect_full_poem_scheme import detect_full_poem_rhyme_scheme

def show_100_lines(filepath: str, start_line: int = 0):
    """Analyze and show 100 lines."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if len(l.strip()) >= 10]
    
    chunk_size = 100
    start = start_line
    end = min(start + chunk_size, len(lines))
    chunk = lines[start:end]
    
    print(f"=== ANALYZING 100 LINES from {filepath} (Lines {start+1}-{end}) ===\n")
    
    result = detect_full_poem_rhyme_scheme(chunk)
    
    print(f"Scheme Length: {len(result['scheme'])}")
    print(f"Rhyming Lines: {result['rhyming_lines']}/{result['total_lines']}")
    print(f"{'='*80}\n")
    
    # Print lines with labels
    for i, line in enumerate(chunk):
        label = result['scheme'][i]
        marker = f"[{label}]" if label != 'X' else "   "
        print(f"{start+i+1:4}. {marker} {line}")
    
    print(f"\n{'='*80}")
    print("LONG DISTANCE RHYMES (>10 lines)")
    print(f"{'='*80}\n")
    
    long_dist = sorted([c for c in result['connections'] if c['distance'] > 10], 
                      key=lambda x: -x['distance'])
    
    for conn in long_dist:
        l1 = start + conn['line1'] + 1
        l2 = start + conn['line2'] + 1
        print(f"Lines {l1} ↔ {l2} (Dist: {conn['distance']}): '{conn['word1']}' ↔ '{conn['word2']}' ({conn['type']})")

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "Data/TellosAgras.txt"
    show_100_lines(filename, start_line=100)
