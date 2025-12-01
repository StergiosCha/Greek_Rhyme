#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze real Greek poems for complex rhyme schemes
"""

from detect_full_poem_scheme import detect_full_poem_rhyme_scheme

# Read a poet file and split into stanzas
def analyze_poet_file(filepath: str, max_stanzas: int = 5):
    """Analyze rhyme schemes in a poet's work."""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if len(l.strip()) >= 10]
    
    print(f"=== Analyzing {filepath} ===")
    print(f"Total lines: {len(lines)}\n")
    
    # Analyze in chunks (stanzas of ~12 lines)
    chunk_size = 12
    interesting_patterns = []
    
    for start in range(0, min(len(lines), max_stanzas * chunk_size), chunk_size):
        chunk = lines[start:start + chunk_size]
        
        if len(chunk) < 4:
            continue
        
        result = detect_full_poem_rhyme_scheme(chunk)
        
        # Only show interesting patterns (not all X's)
        if result['rhyming_lines'] >= 3:
            interesting_patterns.append({
                'start': start,
                'lines': chunk,
                'result': result
            })
    
    # Show top patterns
    print(f"Found {len(interesting_patterns)} stanzas with interesting rhyme schemes\n")
    
    for idx, pattern in enumerate(interesting_patterns[:3], 1):
        result = pattern['result']
        print(f"{'='*60}")
        print(f"STANZA {idx} (lines {pattern['start']+1}-{pattern['start']+len(pattern['lines'])})")
        print(f"{'='*60}")
        print(f"Scheme: {result['scheme']}")
        print(f"Pattern: {result['pattern']}")
        print(f"Rhyming: {result['rhyming_lines']}/{result['total_lines']} lines\n")
        
        # Show rhyme groups
        print("Rhyme Groups:")
        for label in sorted(result['groups'].keys()):
            indices = result['groups'][label]
            print(f"\n  {label} → {len(indices)} lines:")
            for idx in indices:
                line = pattern['lines'][idx][:60]
                print(f"    {idx+1}. {line}...")
        
        # Show cross-rhymes (distance > 3)
        long_distance = [c for c in result['connections'] if c['distance'] > 3]
        if long_distance:
            print(f"\n  📍 Long-distance rhymes (>3 lines apart):")
            for conn in long_distance:
                print(f"    Lines {conn['line1']+1}↔{conn['line2']+1}: '{conn['word1']}' / '{conn['word2']}' (distance={conn['distance']})")
        
        print()


if __name__ == "__main__":
    # Analyze NapoleonLapathiotis
    analyze_poet_file("Data/NapoleonLapathiotis.txt", max_stanzas=10)
