#!/bin/bash
# Process all TXT files in Data folder with both formats

echo "=== Processing 6 poets from Data folder ==="
echo ""

for txt_file in Data/*.txt; do
    poet=$(basename "$txt_file" .txt)
    echo "Processing: $poet"
    
    # Regular format
    python build_corpus_from_txt.py "$txt_file" "corpus_${poet}.json"
    
    # Enhanced format
    python build_corpus_from_txt_enhanced.py "$txt_file" "corpus_${poet}_enhanced.json"
    
    echo ""
done

echo "=== All 6 poets processed! ==="
echo "Created 12 files (6 regular + 6 enhanced)"
