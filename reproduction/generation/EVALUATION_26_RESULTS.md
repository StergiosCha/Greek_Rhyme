# EVALUATION TEST BREAKDOWN

## Overview
Each model evaluation produces **26 result objects** covering **52 data points**:
- 13 test cases (different rhyme types and features)
- 2 RAG configurations (WITH-RAG, WITHOUT-RAG)
- 2 verification modes (data for both in each result)

**Total: 13 cases × 2 RAG × 2 verification = 52 data points per model**

---

## What Each Result Contains

Each of the 26 result objects has:
- `no_verify_poem` - Poem generated WITHOUT verification loop
- `no_verify_time` - Time taken
- `no_verify_valid` - Whether it passed symbolic validation
- `no_verify_correct_pairs` - Number of correct rhyme pairs
- `no_verify_total_pairs` - Total rhyme pairs expected
- `with_verify_poem` - Poem generated WITH verification loop
- `with_verify_time` - Time taken
- `with_verify_attempts` - Number of attempts in verification loop
- `with_verify_valid` - Whether it passed symbolic validation
- `with_verify_correct_pairs` - Number of correct rhyme pairs
- `with_verify_total_pairs` - Total rhyme pairs expected
- `improvement` - Accuracy improvement from verification

---

## The 26 Results Breakdown

### Test Case 1: M (Masculine) - Basic
**Theme**: αγάπη (love)
- Result 1: WITH-RAG
- Result 14: WITHOUT-RAG

### Test Case 2: F2 (Feminine-2) - Basic
**Theme**: θάλασσα (sea)
- Result 2: WITH-RAG
- Result 15: WITHOUT-RAG

### Test Case 3: F3 (Feminine-3) - Basic
**Theme**: ουρανός (sky)
- Result 3: WITH-RAG
- Result 16: WITHOUT-RAG

### Test Case 4: M + PURE
**Theme**: φως (light)
- Result 4: WITH-RAG
- Result 17: WITHOUT-RAG

### Test Case 5: F2 + RICH
**Theme**: νύχτα (night)
- Result 5: WITH-RAG
- Result 18: WITHOUT-RAG

### Test Case 6: F3 + IMPERFECT
**Theme**: ελπίδα (hope)
- Result 6: WITH-RAG
- Result 19: WITHOUT-RAG

### Test Case 7: M + PURE + IDV
**Theme**: καρδιά (heart)
- Result 7: WITH-RAG
- Result 20: WITHOUT-RAG

### Test Case 8: F2 + RICH + IDV
**Theme**: όνειρο (dream)
- Result 8: WITH-RAG
- Result 21: WITHOUT-RAG

### Test Case 9: F3 + IMPERFECT + IDV
**Theme**: μνήμη (memory)
- Result 9: WITH-RAG
- Result 22: WITHOUT-RAG

### Test Case 10: M + MOSAIC
**Theme**: φεγγάρι (moon)
- Result 10: WITH-RAG
- Result 23: WITHOUT-RAG

### Test Case 11: F2 + MOSAIC
**Theme**: άνεμος (wind)
- Result 11: WITH-RAG
- Result 24: WITHOUT-RAG

### Test Case 12: M + RICH + MOSAIC
**Theme**: χρόνος (time)
- Result 12: WITH-RAG
- Result 25: WITHOUT-RAG

### Test Case 13: F2 + PURE + IDV + MOSAIC
**Theme**: ψυχή (soul)
- Result 13: WITH-RAG
- Result 26: WITHOUT-RAG

---

## Key Comparisons You Can Make

### 1. Verification Impact
Compare `no_verify_*` vs `with_verify_*` fields in each result to see:
- Does verification improve accuracy?
- How many attempts does it take?
- Time cost of verification

### 2. RAG Impact
Compare results 1-13 (WITH-RAG) vs 14-26 (WITHOUT-RAG) to see:
- Does RAG improve quality?
- Does RAG help with complex features (RICH, MOSAIC, IDV)?

### 3. Rhyme Type Difficulty
Compare M vs F2 vs F3 test cases:
- Which stress patterns are harder?
- Does verification help more for certain types?

### 4. Feature Complexity
Compare basic tests (1-3) vs feature tests (4-13):
- Are PURE/RICH/IMPERFECT harder than basic?
- Does MOSAIC increase difficulty?
- Does IDV (identical vowels) increase difficulty?

---

## Files

**Claude-sonnet-4.5**:
- Checkpoint: `checkpoint_claude_sonnet_4_5.json`
- Results: `results_claude_sonnet_4_5.json`

**Claude-sonnet-3.7**:
- Checkpoint: `checkpoint_claude_sonnet_3_7.json`
- Results: `results_claude_sonnet_3_7.json`

---

## Quick Check Commands

**Check progress**:
```bash
python -c "import json; d=json.load(open('checkpoint_claude_sonnet_4_5.json')); print(f'{d[\"completed_tests\"]}/26')"
```

**List all test IDs**:
```bash
python -c "import json; d=json.load(open('checkpoint_claude_sonnet_4_5.json')); [print(f'{i+1}. {r[\"test_id\"]}') for i,r in enumerate(d['results'])]"
```

**Check if running**:
```bash
ps aux | grep "claude-sonnet" | grep -v grep
```
