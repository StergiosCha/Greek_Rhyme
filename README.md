# Greek Rhyme: Hybrid Neuro-Symbolic System

This repository contains the official implementation of the **Hybrid Neuro-Symbolic Greek Rhyme Generation System**, as described in our research. It includes both the interactive web application and the code required to reproduce our experimental results.

## Repository Structure

- **`app.py`**: The FastAPI backend for the interactive web application.
- **`static/`**: Frontend assets (HTML, JS, CSS) for the web interface.
- **`src/`**: Core source code for the phonological engine and logic (used by both the App and Reproduction scripts).
- **`data/`**: The verified rhyme corpus (`complete_corpus_enhanced.json`).
- **`requirements.txt`**: Python dependencies.

## 1. Running the Web Application

The web app provides an interactive interface to generate poems with specific rhyme constraints and visualize the verification feedback loop.

### Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set API Keys in a `.env` file (see `.env.example` or code):
   - `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`

### Launch
Run the server:
```bash
uvicorn app:app --reload
```
Open `http://localhost:8000` in your browser.

## 2. Reproducing Research Results

To reproduce the statistics and benchmarks reported in the paper, use the scripts in the `src/` directory.

### Setup
Ensure your PYTHONPATH includes the `src` directory:
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

### Experiments

**A. Evaluation of Generation (Table 5)**
Measures validity rates of different models with and without verification.
```bash
python src/evaluate_system.py --model gpt-4o --num-samples 50
```

**B. Rhyme Identification Benchmarks (Table 2)**
Tests the model's ability to classify rhyme types (M, F2, F3, etc.).
```bash
python src/evaluate_identification.py --model claude-3-sonnet
```

## Citation
If you use this code or data, please cite our paper:
[BibTeX entry]
