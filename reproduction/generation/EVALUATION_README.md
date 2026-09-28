# Greek Rhyme System Evaluation

## Overview

This evaluation framework compares two approaches to poem generation:

1. **Without Verification** (Fast): Single-shot generation, no feedback loop
2. **With Verification** (Accurate): Iterative generation with symbolic rule validation

The evaluation uses **symbolic phonological rules** as ground truth, testing all parameter combinations:
- **Stress types**: M (Masculine/Oxytone), F2 (Paroxytone), F3 (Proparoxytone)
- **Rhyme quality**: PURE, RICH, IMPERFECT
- **Special features**: MOSAIC, IDV (Identical Pre-stress Vowel), COPY

## Files

- **`evaluate_system.py`**: Main evaluation script with comprehensive testing
- **`quick_evaluate.py`**: Quick demo version (uses mock LLM)
- **`evaluation_results.json`**: Output file with detailed results

## How It Works

### 1. Generation Without Verification

```python
# Generate once, no feedback
result = await pipeline.generate_poem(
    theme="αγάπη",
    rhyme_type="M",
    features=["PURE"],
    use_verification=False  # KEY: No verification loop
)
```

### 2. Symbolic Validation

The `SymbolicValidator` class uses `greek_phonology.py` to check:

```python
# Extract rhyme domains
rd1 = extract_rhyme_domain(line1)
rd2 = extract_rhyme_domain(line2)

# Classify rhyme type
rhyme_result = classify_rhyme_pair(w1, w2)

# Check stress position
stress1 = detect_stress_position(w1)
stress2 = detect_stress_position(w2)

# Validate all constraints
if rhyme_result['type'] != expected_type:
    errors.append(f"Expected {expected_type}, got {rhyme_result['type']}")
```

### 3. Generation With Verification

```python
# Generate with feedback loop (up to 15 attempts)
result = await pipeline.generate_poem(
    theme="αγάπη",
    rhyme_type="M",
    features=["PURE"],
    use_verification=True  # Verification enabled
)
```

### 4. Comparison

The system compares:
- **Accuracy**: Percentage of correct rhyme pairs
- **Speed**: Time taken (with verification is slower but more accurate)
- **Attempts**: Number of iterations needed
- **Validity**: Whether all constraints are satisfied

## Usage

### Quick Test (Mock LLM)

```bash
python quick_evaluate.py
```

This runs a quick demo with mock LLM responses to show how the evaluation works.

### Full Evaluation (Real LLM)

You need to integrate your LLM API. Modify `evaluate_system.py`:

```python
# Example: OpenAI integration
async def my_generate_callback(model_name, prompt):
    response = await openai.ChatCompletion.acreate(
        model=model_name,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    tokens = response.usage.total_tokens
    return text, tokens

# Run evaluation
evaluator = SystemEvaluator(
    model_name="gpt-4o",
    generate_callback=my_generate_callback
)
```

Then run:

```bash
python evaluate_system.py --model gpt-4o --num-samples 3 --output results.json
```

### Custom Test Cases

Create a JSON file with your test cases:

```json
[
  {
    "theme": "αγάπη",
    "rhyme_type": "M",
    "features": ["PURE"]
  },
  {
    "theme": "θάλασσα",
    "rhyme_type": "F2",
    "features": ["RICH", "IDV"]
  }
]
```

Run with:

```bash
python evaluate_system.py --test-cases my_tests.json --num-samples 5
```

## Output Format

The evaluation produces a JSON file with detailed results:

```json
{
  "metadata": {
    "model": "gpt-4o",
    "timestamp": "2025-12-08T07:20:00",
    "total_tests": 13
  },
  "results": [
    {
      "test_id": "1_1",
      "theme": "αγάπη",
      "rhyme_type": "M",
      "features": [],
      
      "no_verify_poem": "...",
      "no_verify_time": 2.3,
      "no_verify_valid": false,
      "no_verify_errors": ["Stress mismatch: ..."],
      "no_verify_correct_pairs": 1,
      "no_verify_total_pairs": 2,
      
      "with_verify_poem": "...",
      "with_verify_time": 8.7,
      "with_verify_attempts": 3,
      "with_verify_valid": true,
      "with_verify_errors": [],
      "with_verify_correct_pairs": 2,
      "with_verify_total_pairs": 2,
      
      "improvement": 50.0
    }
  ]
}
```

## Metrics Explained

### Accuracy
Percentage of rhyme pairs that satisfy ALL constraints:
- Correct stress position (M/F2/F3)
- Correct rhyme quality (PURE/RICH/IMPERFECT)
- Correct special features (MOSAIC, IDV, etc.)

### Improvement
Difference in accuracy between with and without verification:
- **Positive**: Verification helps
- **Zero**: Both approaches perform equally
- **Negative**: Verification hurts (rare, indicates bug)

### Time Cost
How much slower verification is:
- Typical: 3-5x slower
- Worth it if accuracy gain is significant

## Example Output

```
┌─ SUMMARY ─────────────────────────────────────────────────────────┐
│ Test ID: 1_1                                                      │
│ Config: M + PURE                                                  │
├───────────────────────────────────────────────────────────────────┤
│ WITHOUT Verification:                                             │
│   Time:   2.30s                                                   │
│   Accuracy: 1/2 pairs ( 50.0%)                                    │
│   Valid: False                                                    │
├───────────────────────────────────────────────────────────────────┤
│ WITH Verification:                                                │
│   Time:   8.70s                                                   │
│   Attempts: 3                                                     │
│   Accuracy: 2/2 pairs (100.0%)                                    │
│   Valid: True                                                     │
├───────────────────────────────────────────────────────────────────┤
│ Improvement: +50.0%                                               │
└───────────────────────────────────────────────────────────────────┘
```

## Integration with Web App

To integrate with your Flask app (`app.py`), add an evaluation endpoint:

```python
@app.route('/api/evaluate', methods=['POST'])
async def evaluate_endpoint():
    data = request.json
    test_cases = data.get('test_cases', DEFAULT_TEST_CASES)
    num_samples = data.get('num_samples', 1)
    
    evaluator = SystemEvaluator(
        model_name=data.get('model', 'gpt-4o'),
        generate_callback=your_llm_callback
    )
    
    await evaluator.run_evaluation(test_cases, num_samples)
    
    return jsonify({
        'results': [asdict(r) for r in evaluator.results]
    })
```

## Validation Rules

The symbolic validator checks:

1. **Rhyme Existence**: Words must rhyme according to `classify_rhyme_pair()`
2. **Stress Match**: Both words must have the requested stress position
3. **Quality Match**: Rhyme type must match (PURE/RICH/IMPERFECT)
4. **MOSAIC**: If requested, rhyme must span word boundaries
5. **IDV**: If requested, pre-stress vowels must match phonetically
6. **No COPY**: Identical words rejected unless explicitly requested

## Troubleshooting

### Mock LLM Returns Same Output
This is expected for `quick_evaluate.py`. For real evaluation, integrate your LLM API.

### Low Accuracy Without Verification
This is normal! The verification loop is designed to improve accuracy through feedback.

### High Time Cost
If verification takes too long:
- Reduce `max_attempts` in `agent_pipeline.py` (default: 15)
- Use faster model for verification
- Cache successful patterns

## Next Steps

1. **Integrate LLM**: Add your LLM API callback
2. **Run Full Evaluation**: Test all parameter combinations
3. **Analyze Results**: Identify which features benefit most from verification
4. **Optimize**: Tune `max_attempts` based on accuracy/speed tradeoff
5. **Deploy**: Use findings to configure production system

## References

- **Symbolic Rules**: `greek_phonology.py`
- **Verification Logic**: `verification_utils.py`
- **Pipeline**: `agent_pipeline.py`
- **Topintzi et al. (2019)**: `topintzi_summary.md`
