"""
Test script for LLM Integration

Verifies that the LLM integration works correctly with available providers.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ptcc.backend.core.llm_integration import (
    get_llm_orchestrator,
    generate_text,
    generate_with_context
)


def test_basic_generation():
    """Test basic text generation."""
    print("\n" + "="*60)
    print("TEST 1: Basic Text Generation")
    print("="*60)
    
    try:
        prompt = "Explain photosynthesis in simple terms for a 5th grade student."
        
        print(f"\nPrompt: {prompt}")
        print("\nGenerating response...")
        
        response_text = generate_text(
            prompt=prompt,
            provider="gemini",
            temperature=0.7,
            max_tokens=300
        )
        
        print(f"\nResponse:\n{response_text}")
        print("\n✅ Basic generation test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Basic generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_generation_with_context():
    """Test generation with context."""
    print("\n" + "="*60)
    print("TEST 2: Generation with Context")
    print("="*60)
    
    try:
        context = {
            "grade_level": "5th grade",
            "subject": "Science",
            "topic": "Photosynthesis",
            "learning_objective": "Understand the basic process of photosynthesis",
            "time_available": "30 minutes"
        }
        
        prompt = "Create a brief lesson plan for teaching this topic."
        
        print(f"\nContext:")
        for key, value in context.items():
            print(f"  {key}: {value}")
        
        print(f"\nPrompt: {prompt}")
        print("\nGenerating response...")
        
        response = generate_with_context(
            prompt=prompt,
            context=context,
            provider="gemini"
        )
        
        print(f"\nResponse:\n{response.text}")
        print(f"\nTokens used: {response.usage['total_tokens']}")
        print("\n✅ Context-based generation test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Context-based generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_orchestrator_features():
    """Test orchestrator features."""
    print("\n" + "="*60)
    print("TEST 3: Orchestrator Features")
    print("="*60)
    
    try:
        orchestrator = get_llm_orchestrator()
        
        # Test generation with metadata
        prompt = "What are the three states of matter?"
        print(f"\nPrompt: {prompt}")
        print("\nGenerating response...")
        
        response = orchestrator.generate(
            prompt=prompt,
            provider="gemini",
            model="gemini-1.5-flash",  # Using faster model
            temperature=0.5,
            max_tokens=200
        )
        
        print(f"\nResponse:\n{response.text}")
        print(f"\nMetadata:")
        print(f"  Model: {response.model}")
        print(f"  Provider: {response.provider}")
        print(f"  Prompt tokens: {response.usage['prompt_tokens']}")
        print(f"  Completion tokens: {response.usage['completion_tokens']}")
        print(f"  Total tokens: {response.usage['total_tokens']}")
        
        # Test cost estimation
        cost = orchestrator.estimate_cost(response)
        print(f"  Estimated cost: ${cost:.6f}")
        
        print("\n✅ Orchestrator features test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Orchestrator features test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_educational_use_case():
    """Test a realistic educational use case."""
    print("\n" + "="*60)
    print("TEST 4: Educational Use Case - Assessment Question Generation")
    print("="*60)
    
    try:
        prompt = """Generate 3 multiple-choice questions about photosynthesis for 5th grade students.

For each question, provide:
1. The question text
2. Four answer options (A, B, C, D)
3. The correct answer
4. A brief explanation

Format your response clearly."""
        
        print(f"\nGenerating assessment questions...")
        
        response_text = generate_text(
            prompt=prompt,
            provider="gemini",
            temperature=0.8,  # Higher for more variety
            max_tokens=800
        )
        
        print(f"\nGenerated Questions:\n{response_text}")
        print("\n✅ Educational use case test passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Educational use case test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PTCC LLM Integration Test Suite")
    print("="*60)
    
    tests = [
        ("Basic Generation", test_basic_generation),
        ("Generation with Context", test_generation_with_context),
        ("Orchestrator Features", test_orchestrator_features),
        ("Educational Use Case", test_educational_use_case)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! LLM integration is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
