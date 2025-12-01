import asyncio
from agent_pipeline import AgentPipeline

# Mock the generator to return different things based on request
class MockGenerator:
    async def generate(self, prompt: str) -> str:
        if "RICH" in prompt:
            # Return a Rich Rhyme (matching onset)
            # e.g. "καλά" - "χαλά" (Not rich, k vs x)
            # "βαρά" - "βαρά"? No.
            # "τρέχω" - "βρέχω" (trexo - vrexo). tr vs vr.
            # "σώματα" - "χώματα" (somata - xomata). s vs x.
            # "αυγή" - "ναυγή" (avji - navji). Rich!
            return "MOCK RESPONSE (RICH):\nLine 1: ... η αυγή\nLine 2: ... η ναυγή"
        elif "IMPERFECT" in prompt:
            return "MOCK RESPONSE (IMP):\nLine 1: ... χάνεται\nLine 2: ... γίνεται"
        else:
            # Pure
            return "MOCK RESPONSE (PURE):\nLine 1: ... χαρά\nLine 2: ... φορά"

async def test_pipeline():
    print("=== Testing Agentic Rhyme Pipeline ===")
    
    pipeline = AgentPipeline()
    # Inject mock
    pipeline.generator = MockGenerator()
    
    # Test 1: Pure Rhyme
    print("\n--- TEST 1: Pure Rhyme (M) ---")
    result = await pipeline.generate_poem(
        theme="Joy",
        rhyme_type="M",
        features=[],
        num_lines=2
    )
    print("Result:", result)
    
    # Test 2: Rich Rhyme
    print("\n--- TEST 2: Rich Rhyme (M-RICH) ---")
    result = await pipeline.generate_poem(
        theme="Morning",
        rhyme_type="M",
        features=["RICH"],
        num_lines=2
    )
    print("Result:", result)
    
    # Test 3: Imperfect Rhyme
    print("\n--- TEST 3: Imperfect Rhyme (IMP) ---")
    result = await pipeline.generate_poem(
        theme="Loss",
        rhyme_type="F3",
        features=["IMPERFECT"],
        num_lines=2
    )
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(test_pipeline())
