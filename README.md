# Greek Rhyme Analyzer & Generator

A complete system for identifying and generating rhyme patterns in Modern Greek poetry using LLMs. Based on the taxonomy from Topintzi et al. (2019).

## Features

### 🔍 Rhyme Identification
- **Multiple Prompting Strategies**: Zero-shot, Few-shot, Chain-of-Thought
- **Comprehensive Taxonomy**: M/F2/F3, RICH, IDV, MOS, IMP, COPY patterns
- **Multi-Model Support**: Claude, Gemini, GPT, Llama, Qwen, Mistral

### ✍️ Rhyme Generation
- **Customizable Parameters**: Theme, rhyme type, features, line count
- **Pattern-Based**: Generate specific rhyme structures
- **RAG-Enhanced**: Use corpus examples for better quality

### 🤖 Supported Models

**Claude**
- Sonnet 4.5 (Latest)
- Sonnet 3.7

**Gemini**
- 3 Pro (Best multimodal)
- 2.5 Pro (Advanced thinking)
- 2.5 Flash (Fast & intelligent)
- 2.5 Flash-Lite (Ultra fast)
- 2.0 Flash

**OpenAI**
- GPT-4o

**Open Models (via OpenRouter)**
- Llama 3.3 70B / 3.1 70B
- Qwen 2.5 72B
- Mistral Large

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Backend
```bash
python app.py
```

### 4. Open Frontend
Open `index.html` in your browser or serve it:
```bash
python -m http.server 8080
```
Then visit http://localhost:8080

## Architecture

```
greek_rhyme_system/
├── app.py              # FastAPI backend with model APIs
├── prompts.py          # Prompting strategies (5 types)
├── rag_system.py       # RAG retrieval from corpus
├── index.html          # Frontend interface
├── requirements.txt    # Python dependencies
└── .env               # API keys (create from .env.example)
```

## Rhyme Classification System

### Position Types
- **M** (Masculine): Final stressed vowel
- **F2** (Feminine-2): Penultimate stressed vowel
- **F3** (Feminine-3): Antepenultimate stressed vowel

### Features
- **RICH**: Onset consonants match (TR-S, TR-CC, PR-C1, PR-C2)
- **IDV**: Pre-rhyme vowel identity (IDV-2W across words)
- **MOS**: Mosaic (crosses word boundaries)
- **IMP**: Imperfect (IMP-V vowel, IMP-C consonant, IMP-0F/0M zero alternation)
- **COPY**: Complete repetition

## API Endpoints

### POST /identify
Identify rhymes in Greek text.
```json
{
  "text": "Πάνω στην άμμο...",
  "model": "gemini-2.5-pro",
  "prompt_strategy": "few_shot_cot",
  "use_rag": true
}
```

### POST /generate
Generate Greek poetry with specified patterns.
```json
{
  "theme": "η θάλασσα",
  "rhyme_type": "F2",
  "features": ["RICH", "IDV"],
  "num_lines": 4,
  "model": "claude-sonnet-4.5",
  "use_rag": true
}
```

### GET /models
List available models.

## RAG System

The RAG system retrieves relevant examples from the Greek Rhyme corpus:
- Solomos (Hymn to Freedom)
- Mavilis (23 Sonnets)
- Palamas (The Twelve Words of the Gypsy)
- Karyotakis
- Varnalis

## Prompting Strategies

1. **Zero-Shot Structured**: Taxonomy-based instructions
2. **Zero-Shot Algorithm**: Mimics detection algorithm
3. **Few-Shot**: 4 worked examples
4. **Zero-Shot CoT**: Step-by-step reasoning framework
5. **Few-Shot CoT**: Examples with explicit reasoning

## Citation

Based on:
> Topintzi, N., Avdelidis, K., & Valkanou, T. (2019). Greek Rhyme (GrR): A database on rhyme in Greek poetry. *Selected Papers of ISTAL 23*, 429-447.

## Future Enhancements

- [ ] Vector embeddings for semantic RAG
- [ ] Fine-tuning on GRDD dataset
- [ ] Phonetic transcription integration
- [ ] Extended corpus (Seferis, Elytis, etc.)
- [ ] Statistical analysis dashboard
- [ ] Multi-poet comparison tools
- [ ] Real-time collaborative annotation

## License

Research use. See paper for corpus details.
