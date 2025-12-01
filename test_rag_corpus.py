import asyncio
from rag_system import get_relevant_examples, get_generation_examples

async def test_rag():
    print("Testing RAG with new corpus...")
    
    # Test 1: Identification Retrieval
    print("\n--- Test 1: Identification (Query: 'Valaoritis rich rhyme') ---")
    res1 = await get_relevant_examples("Valaoritis rich rhyme", top_k=1)
    print(res1[:500] + "...")
    
    # Test 2: Generation Retrieval
    print("\n--- Test 2: Generation (Type: F2, Features: ['RICH'], Theme: 'love') ---")
    res2 = await get_generation_examples("F2", ["RICH"], "love", top_k=1)
    print(res2[:500] + "...")

if __name__ == "__main__":
    asyncio.run(test_rag())
