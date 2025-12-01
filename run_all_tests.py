import subprocess
import sys
import time

def run_test(script_name):
    print(f"\n{'='*20} Running {script_name} {'='*20}")
    start_time = time.time()
    try:
        # Run the script and capture output
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            check=True
        )
        duration = time.time() - start_time
        print(result.stdout)
        print(f"✅ {script_name} PASSED ({duration:.2f}s)")
        return True
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print(e.stdout)
        print(e.stderr)
        print(f"❌ {script_name} FAILED ({duration:.2f}s)")
        return False

def main():
    print("🚀 STARTING FULL SYSTEM VERIFICATION 🚀")
    
    tests = [
        "test_phonology_experimental.py", # Core phonology rules
        "test_enhanced_phonology.py",    # Rhyme classification (Rich/Imp)
        "test_rag_validation.py",        # Corpus validation
        "test_rag_generation.py",        # RAG retrieval flow
        "test_pipeline.py"               # End-to-end Agentic Pipeline
    ]
    
    results = []
    for test in tests:
        success = run_test(test)
        results.append((test, success))
        
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for test, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test}")
        if not success:
            all_passed = False
            
    if all_passed:
        print("\n🎉 ALL SYSTEMS GO! The entire pipeline is operational.")
        sys.exit(0)
    else:
        print("\n⚠️ SOME TESTS FAILED. Check output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
