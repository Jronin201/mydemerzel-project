"""
Test to verify that the chatbot is using GPT-5.3 after the upgrade.
"""
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

def test_configuration_uses_gpt53():
    """Test that all configuration points to gpt-5.3"""
    print("\n" + "=" * 70)
    print("TEST 1: Configuration Check")
    print("=" * 70)
    
    import ai_client
    import app
    
    # Check ai_client defaults
    assert ai_client.OPENAI_MODEL == "gpt-5.3", f"ai_client.OPENAI_MODEL should be gpt-5.3, got {ai_client.OPENAI_MODEL}"
    print(f"✓ ai_client.OPENAI_MODEL = {ai_client.OPENAI_MODEL}")
    
    assert ai_client.OPENAI_FALLBACK_MODEL == "gpt-4o", f"Fallback should be gpt-4o, got {ai_client.OPENAI_FALLBACK_MODEL}"
    print(f"✓ ai_client.OPENAI_FALLBACK_MODEL = {ai_client.OPENAI_FALLBACK_MODEL}")
    
    # Check app.py defaults
    assert app.OPENAI_CHAT_MODEL == "gpt-5.3", f"app.OPENAI_CHAT_MODEL should be gpt-5.3, got {app.OPENAI_CHAT_MODEL}"
    print(f"✓ app.OPENAI_CHAT_MODEL = {app.OPENAI_CHAT_MODEL}")
    
    # Check fallback list
    assert app.CHAT_MODEL_FALLBACKS[0] == "gpt-5.3", f"First fallback should be gpt-5.3, got {app.CHAT_MODEL_FALLBACKS[0]}"
    print(f"✓ app.CHAT_MODEL_FALLBACKS = {app.CHAT_MODEL_FALLBACKS}")
    
    print("\n✓ PASSED: All configurations point to gpt-5.3")


def test_system_prompt_identifies_gpt53():
    """Test that system prompt identifies the model as GPT-5.3"""
    print("\n" + "=" * 70)
    print("TEST 2: System Prompt Check")
    print("=" * 70)
    
    system_prompt_path = Path("system_prompt_master.txt")
    assert system_prompt_path.exists(), "system_prompt_master.txt should exist"
    
    content = system_prompt_path.read_text()
    first_line = content.split('\n')[0]
    
    print(f"System prompt first line: {first_line[:80]}...")
    
    assert "GPT-5.3" in first_line, f"System prompt should mention GPT-5.3, got: {first_line}"
    print(f"✓ System prompt correctly identifies GPT-5.3")
    
    # Make sure it doesn't incorrectly say GPT-4
    assert "GPT-4" not in first_line, f"System prompt should not mention GPT-4"
    print(f"✓ System prompt does not mention GPT-4")
    
    print("\n✓ PASSED: System prompt correctly identifies GPT-5.3")


def test_api_calls_use_gpt53():
    """Test that actual API calls use gpt-5.3 model"""
    print("\n" + "=" * 70)
    print("TEST 3: API Call Model Verification")
    print("=" * 70)
    
    import ai_client
    
    # Mock the OpenAI client
    mock_response = MagicMock()
    mock_response.output_text = "Test response"
    mock_response.model = "gpt-5.3"
    mock_response.id = "test_123"
    mock_response.usage = MagicMock(
        input_tokens=10,
        output_tokens=20,
        total_tokens=30
    )
    
    with patch.object(ai_client, '_client') as mock_client:
        mock_client.responses.create.return_value = mock_response
        
        # Make a test request
        messages = [
            {"role": "system", "content": "You are a test assistant"},
            {"role": "user", "content": "Hello"}
        ]
        
        result = ai_client.request(messages, max_output_tokens=100)
        
        # Verify the call was made
        assert mock_client.responses.create.called, "API should have been called"
        
        # Get the kwargs that were passed to the API
        call_kwargs = mock_client.responses.create.call_args[1]
        
        print(f"API call kwargs: {json.dumps({k: str(v)[:50] for k, v in call_kwargs.items()}, indent=2)}")
        
        # Verify model is gpt-5.3
        assert call_kwargs['model'] == 'gpt-5.3', f"API call should use gpt-5.3, got {call_kwargs['model']}"
        print(f"✓ API call model = {call_kwargs['model']}")
        
        # Verify NO reasoning parameter (since it's not supported)
        assert 'reasoning' not in call_kwargs, "API call should NOT include 'reasoning' parameter"
        print(f"✓ API call does NOT include unsupported 'reasoning' parameter")
        
        # Verify result
        assert result['output_text'] == "Test response", "Should return response text"
        assert result['model'] == "gpt-5.3", f"Response model should be gpt-5.3, got {result['model']}"
        print(f"✓ Response model = {result['model']}")
    
    print("\n✓ PASSED: API calls correctly use gpt-5.3 without unsupported parameters")


def test_no_reasoning_parameter_in_kwargs():
    """Test that reasoning parameter is not included in API kwargs"""
    print("\n" + "=" * 70)
    print("TEST 4: Reasoning Parameter Removal Verification")
    print("=" * 70)
    
    import ai_client
    
    # Mock the OpenAI client
    mock_response = MagicMock()
    mock_response.output_text = "Test"
    mock_response.model = "gpt-5.3"
    mock_response.id = "test"
    mock_response.usage = MagicMock(input_tokens=5, output_tokens=5, total_tokens=10)
    
    with patch.object(ai_client, '_client') as mock_client:
        mock_client.responses.create.return_value = mock_response
        
        # Test with different reasoning_effort values
        for effort in ["low", "medium", "high"]:
            messages = [{"role": "user", "content": "test"}]
            result = ai_client.request(messages, reasoning_effort=effort, max_output_tokens=100)
            
            call_kwargs = mock_client.responses.create.call_args[1]
            
            # Verify reasoning is NOT in kwargs
            assert 'reasoning' not in call_kwargs, f"'reasoning' should not be in kwargs with effort={effort}"
            print(f"✓ No 'reasoning' parameter with reasoning_effort={effort}")
    
    print("\n✓ PASSED: Reasoning parameter is never sent to API")


def test_circuit_breaker_state():
    """Test that circuit breaker is in correct state"""
    print("\n" + "=" * 70)
    print("TEST 5: Circuit Breaker State")
    print("=" * 70)
    
    import ai_client
    
    state = ai_client.circuit_state()
    print(f"Circuit breaker state: {state}")
    
    assert state['state'] == 'closed', f"Circuit breaker should be closed, got {state['state']}"
    print(f"✓ Circuit breaker is closed (primary model gpt-5.3 is active)")
    
    print("\n✓ PASSED: Circuit breaker allows gpt-5.3 to be used")


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("GPT-5.3 UPGRADE VERIFICATION TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Configuration", test_configuration_uses_gpt53),
        ("System Prompt", test_system_prompt_identifies_gpt53),
        ("API Calls", test_api_calls_use_gpt53),
        ("Reasoning Parameter", test_no_reasoning_parameter_in_kwargs),
        ("Circuit Breaker", test_circuit_breaker_state),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ FAILED: {name}")
            print(f"   Error: {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERROR in {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(tests)}")
    print(f"✓ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("The chatbot is correctly configured to use GPT-5.3")
        print("\nKey verifications:")
        print("  • Configuration defaults to gpt-5.3")
        print("  • System prompt identifies as GPT-5.3")
        print("  • API calls use gpt-5.3 model")
        print("  • No unsupported 'reasoning' parameter sent")
        print("  • Circuit breaker allows primary model")
    else:
        print("\n⚠️ SOME TESTS FAILED")
        print("Please review the errors above")
        sys.exit(1)
    
    print("=" * 70)


if __name__ == "__main__":
    main()
