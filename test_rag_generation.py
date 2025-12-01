import asyncio
from rag_system import get_generation_examples
from prompts import get_generation_prompt

async def test_rag_flow():
    print("Testing RAG Generation Flow...")
    
    # 1. Request examples for Rich Rhyme
    print("\n--- Retrieving Rich Rhyme Examples ---")
    examples = await get_generation_examples(
        rhyme_type="M", 
        features=["RICH"], 
        theme="nature", 
        top_k=2
    )
    print(examples)
    
    # 2. Generate Prompt
    print("\n--- Generating Prompt ---")
    prompt = get_generation_prompt(
        theme="The Sea",
        rhyme_type="M",
        features=["RICH"],
        num_lines=4,
        rag_context=examples
    )
    print(prompt[:500] + "...") # Print first 500 chars

if __name__ == "__main__":
    asyncio.run(test_rag_flow())
