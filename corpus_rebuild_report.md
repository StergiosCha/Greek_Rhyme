# Corpus Rebuild Report - Fixed IMPERFECT Rhyme Rules

## Bug Fixed

**Problem:** False positives where open syllables (ending in vowel) were incorrectly matching closed syllables (ending in consonant).

**Example:** "τυχερό" (o) vs "δαρτός" (ós) - These do NOT rhyme but were classified as IMP-0.

**Root Cause:** Empty consonant list `[]` was treated as a subsequence of any consonant list, creating false matches.

**Fix:** Added strict check to reject open/closed syllable mismatches in `greek_phonology.py` line 812.

## Before vs After

### Total Pairs Removed: **835 false positives** (9,969 → 9,134)

### Per-Poet Impact:
| Poet | Before | After | Removed |
|------|--------|-------|---------|
| TellosAgras | 6,196 | 5,578 | **-618** |
| FotosGiofyllis | 1,561 | 1,476 | -85 |
| KostasOuranis | 790 | 727 | -63 |
| RomosFiliras | 500 | 466 | -34 |
| NapoleonLapathiotis | 492 | 457 | -35 |
| MitsosPapanikolaou | 430 | 430 | 0 |
| **TOTAL** | **9,969** | **9,134** | **-835** |

## Files Updated

✅ `greek_phonology.py` - Fixed IMP-0 logic
✅ `unified_corpus.json` - Cleaned 9,134 valid pairs
✅ `unified_corpus_enhanced.json` - With full context
✅ All 6 individual poet corpus files (regular + enhanced)

## Validation

```python
# Test case now works correctly
classify_rhyme_pair("τυχερό", "δαρτός")
# Returns: {'type': 'NONE'} ✓
```

## Next Steps

The corpus is now clean and ready for:
1. RAG-enhanced generation
2. ACL paper validation
3. Poet-specific rhyme detection
