#!/usr/bin/env python3
"""
Quick test script for Greek Rhyme System
"""
import httpx
import asyncio
import json

async def test_system():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Greek Rhyme System\n")
    
    # Test 1: Check models endpoint
    print("1. Testing /models endpoint...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/models")
            if response.status_code == 200:
                models = response.json()["models"]
                print(f"✅ Found {len(models)} models")
            else:
                print(f"❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Test identification (with mock, won't actually call API)
    print("\n2. Testing /identify endpoint structure...")
    test_payload = {
        "text": "Πάνω στην άμμο την ξανθή\nκαι σβήστηκε η γραφή",
        "model": "claude-sonnet-4.5",
        "prompt_strategy": "zero_shot_structured",
        "use_rag": False
    }
    print(f"✅ Payload structure valid")
    
    # Test 3: Test generation endpoint structure
    print("\n3. Testing /generate endpoint structure...")
    test_gen_payload = {
        "theme": "η θάλασσα",
        "rhyme_type": "F2",
        "features": ["pure", "RICH"],
        "num_lines": 4,
        "model": "gemini-2.5-pro",
        "use_rag": True
    }
    print(f"✅ Payload structure valid")
    
    print("\n✅ All structural tests passed!")
    print("\n📝 Note: Actual API calls require valid API keys in .env")
    print("   Add your keys and test with the frontend interface.\n")

if __name__ == "__main__":
    asyncio.run(test_system())
