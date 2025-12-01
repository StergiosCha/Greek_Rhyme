#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scan entire poet files for EXTREME long-distance rhymes (>15 lines)
Uses a sliding window approach to find rhymes that span across stanzas.
"""

import sys
from detect_full_poem_scheme import detect_full_poem_rhyme_scheme

def scan_file_for_long_distance(filepath: str, window_size: int = 60, min_distance: int = 15):
    """
    Scan file with sliding window to find long distance rhymes.
    """
    print(f"=== Scanning {filepath} for rhymes > {min_distance} lines apart ===\n")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if len(l.strip()) >= 10]
    
    print(f"Total lines: {len(lines)}")
    print(f"Window size: {window_size} lines")
    print(f"Overlap: {window_size // 2} lines\n")
    
    found_rhymes = []
    seen_pairs = set()
    
    # Sliding window
    step = window_size // 2
    for start in range(0, len(lines), step):
        end = min(start + window_size, len(lines))
        chunk = lines[start:end]
        
        if len(chunk) < min_distance:
            break
            
        # Analyze chunk
        result = detect_full_poem_rhyme_scheme(chunk)
        
        # Find long distance connections
        for conn in result['connections']:
            if conn['distance'] >= min_distance:
                # Calculate absolute line numbers
                abs_line1 = start + conn['line1']
                abs_line2 = start + conn['line2']
                
                pair_key = tuple(sorted((abs_line1, abs_line2)))
                
                if pair_key not in seen_pairs:
                    seen_pairs.add(pair_key)
                    found_rhymes.append({
                        'line1': abs_line1,
                        'line2': abs_line2,
                        'text1': lines[abs_line1],
                        'text2': lines[abs_line2],
                        'word1': conn['word1'],
                        'word2': conn['word2'],
                        'type': conn['type'],
                        'distance': conn['distance']
                    })
    
    # Sort by distance (descending)
    found_rhymes.sort(key=lambda x: -x['distance'])
    
    print(f"Found {len(found_rhymes)} long-distance rhyme pairs!\n")
    
    # Show top 20
    print(f"{'='*80}")
    print(f"TOP 20 EXTREME LONG-DISTANCE RHYMES")
    print(f"{'='*80}\n")
    
    for i, rhyme in enumerate(found_rhymes[:20], 1):
        print(f"{i}. Distance: {rhyme['distance']} lines (Lines {rhyme['line1']+1} ↔ {rhyme['line2']+1})")
        print(f"   Type: {rhyme['type']}")
        print(f"   Line {rhyme['line1']+1}: {rhyme['text1']}")
        print(f"   Line {rhyme['line2']+1}: {rhyme['text2']}")
        print(f"   Rhyme: '{rhyme['word1']}' ↔ '{rhyme['word2']}'")
        print()

if __name__ == "__main__":
    filename = sys.argv[1] if len(sys.argv) > 1 else "Data/TellosAgras.txt"
    scan_file_for_long_distance(filename)
