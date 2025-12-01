# Greek Rhyme System - System Overview

## Core Purpose
*   **AI-Powered Analysis & Generation**: A specialized system for analyzing and generating Modern Greek poetry, with a strong focus on phonologically accurate rhyme.
*   **Hybrid Architecture**: Combines Large Language Models (LLMs) with deterministic phonetic algorithms for high precision.

## Key Features

### 1. Rhyme Identification (Analysis)
*   **Phonetic Classification**: Detects and classifies rhymes based on stress position and phonetic matching:
    *   **Stress Types**: Masculine (Oxytone), Feminine (Paroxytone), Proparoxytone.
    *   **Rhyme Categories**:
        *   **Pure**: Perfect phonetic match.
        *   **Rich**: Matches involving more than the required rhyme domain.
        *   **Imperfect**: Assonance or consonance (e.g., matching vowels but different consonants).
        *   **Mosaic**: Rhymes formed by splitting words across lines or using multiple words.
        *   **Identical Vowel (IDV)**: Specific vowel-based rhymes.
*   **Advanced Prompting**: Utilizes multiple strategies to improve LLM accuracy:
    *   Zero-shot & Few-shot learning.
    *   Chain-of-Thought (CoT) reasoning.
    *   **RAG (Retrieval-Augmented Generation)**: Retrieves relevant examples from a verified corpus to guide the model.

### 2. Agentic Poetry Generation
*   **Feedback Loop**: Implements a "Generate-Verify-Refine" cycle:
    1.  **Draft**: LLM generates a poem based on user constraints (Theme, Rhyme Type, Style).
    2.  **Verify**: A deterministic Python tool (`VerificationTool`) checks every rhyme pair against phonological rules.
    3.  **Refine**: If errors are found, the agent receives specific feedback (e.g., "Lines 1-2 do not rhyme") and retries (up to 3 attempts).
*   **Stylistic Control**:
    *   **Poet Mimicry**: Can emulate specific poets (Solomos, Cavafy, Karyotakis, etc.) using RAG.
    *   **Constraint Satisfaction**: Enforces specific rhyme schemes and types (e.g., "Make a 4-line poem with Rich Feminine rhymes").

### 3. Technical Architecture
*   **Backend**: Python-based (FastAPI) application.
*   **Frontend**: Modern, responsive web interface (HTML/JS/CSS) for easy interaction.
*   **Phonological Engine**: Custom Python library (`greek_phonology.py`) for:
    *   Syllabification of Greek text.
    *   Stress detection.
    *   Rhyme domain extraction (handling clitics and multi-word phrases).
*   **Model Agnostic**: Supports multiple LLM providers:
    *   Anthropic (Claude 3.7/4.5)
    *   Google (Gemini 3/2.5)
    *   OpenAI (GPT-4o)
    *   Open Models via OpenRouter (Llama 3, Qwen 2.5)

### 4. Data & Corpus
*   **Extensive Corpus**: Built from major Modern Greek poets.
*   **Data Processing**: Pipeline for cleaning, normalizing, and analyzing raw text/Excel data into structured JSON corpora.
