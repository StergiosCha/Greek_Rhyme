#!/bin/bash

# Run Strict Pipeline
# Rebuilds all corpora using strict logic (rejecting Open vs Closed rhymes)
# Includes punctuation fixes.

echo "=================================================="
echo "🚀 STARTING STRICT PIPELINE"
echo "=================================================="

# 1. Build TXT Corpora (Regular & Enhanced)
echo ""
echo "--- 1. Processing TXT Files ---"
POETS=("FotosGiofyllis" "KostasOuranis" "MitsosPapanikolaou" "NapoleonLapathiotis" "RomosFiliras" "TellosAgras")

for poet in "${POETS[@]}"; do
    echo "Processing $poet..."
    # Regular
    venv/bin/python build_corpus_from_txt.py "Data/${poet}.txt" "corpus_${poet}.json"
    # Enhanced
    venv/bin/python build_corpus_from_txt_enhanced.py "Data/${poet}.txt" "corpus_${poet}_enhanced.json"
done

# 2. Build XLSX Corpora (Regular & Enhanced)
echo ""
echo "--- 2. Processing XLSX File ---"
XLSX_FILE="GLC_Anemoskala_select_text.xlsx"

# Regular
venv/bin/python build_corpus_from_xlsx.py "$XLSX_FILE" "rhyme_corpus.json"
# Enhanced
venv/bin/python build_corpus_enhanced.py "$XLSX_FILE" "rhyme_corpus_enhanced.json"

# 3. Merge All
echo ""
echo "--- 3. Merging Corpora ---"
venv/bin/python merge_all_corpora.py
venv/bin/python merge_complete_corpus.py
venv/bin/python merge_complete_enhanced.py

echo ""
echo "=================================================="
echo "✅ STRICT PIPELINE COMPLETE"
echo "=================================================="
