#!/bin/bash

# Run Topintzi Variant Pipeline
# Builds all corpora using permissive logic (allowing Open vs Closed rhymes)

echo "=================================================="
echo "🚀 STARTING TOPINTZI VARIANT PIPELINE"
echo "=================================================="

# 1. Build TXT Corpora (Regular & Enhanced)
echo ""
echo "--- 1. Processing TXT Files ---"
POETS=("FotosGiofyllis" "KostasOuranis" "MitsosPapanikolaou" "NapoleonLapathiotis" "RomosFiliras" "TellosAgras")

for poet in "${POETS[@]}"; do
    echo "Processing $poet..."
    # Regular
    venv/bin/python build_corpus_topintzi.py "Data/${poet}.txt" "corpus_${poet}_topintzi.json"
    # Enhanced
    venv/bin/python build_corpus_from_txt_enhanced_topintzi.py "Data/${poet}.txt" "corpus_${poet}_enhanced_topintzi.json"
done

# 2. Build XLSX Corpora (Regular & Enhanced)
echo ""
echo "--- 2. Processing XLSX File ---"
XLSX_FILE="GLC_Anemoskala_select_text.xlsx"

# Regular
venv/bin/python build_corpus_xlsx_topintzi.py "$XLSX_FILE" "rhyme_corpus_topintzi.json"
# Enhanced
venv/bin/python build_corpus_xlsx_enhanced_topintzi.py "$XLSX_FILE" "rhyme_corpus_enhanced_topintzi.json"

# 3. Merge All
echo ""
echo "--- 3. Merging Corpora ---"
venv/bin/python merge_all_corpora_topintzi.py
venv/bin/python merge_complete_corpus_topintzi.py
venv/bin/python merge_complete_enhanced_topintzi.py

echo ""
echo "=================================================="
echo "✅ PIPELINE COMPLETE"
echo "=================================================="
