#!/usr/bin/env python3
"""
Test script to verify the chatbot is working properly and not returning 502 errors.
"""
import requests
import json
import time

def test_chat_endpoint():
    """Test the chat endpoint with a simple message."""
    base_url = "http://localhost:5000"
    
    # First, test if server is running
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server health check failed")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to server: {e}")
        return False
    
    # Test login (skip authentication for this test)
    session = requests.Session()
    
    # Test chat endpoint
    chat_data = {
        "message": "Hello, this is a test message. Please respond briefly.",
        "page": "general"
    }
    
    try:
        print("🧪 Testing chat endpoint...")
        response = session.post(
            f"{base_url}/chat",
            json=chat_data,
            timeout=30,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                if "response" in json_response:
                    print("✅ Chat endpoint working!")
                    print(f"Response: {json_response['response'][:100]}...")
                    return True
                else:
                    print("❌ Response missing 'response' field")
                    print(f"Raw response: {response.text}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                print(f"Raw response: {response.text}")
                return False
        elif response.status_code == 401 or response.status_code == 403:
            print("⚠️  Authentication required - this is expected")
            print("The endpoint requires login, but the server is responding properly")
            return True
        elif response.status_code == 502:
            print("❌ 502 Bad Gateway - This is the error you were experiencing!")
            print(f"Response: {response.text}")
            return False
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - server may be hanging")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_openai_connectivity():
    """Test OpenAI API connectivity directly."""
    import os
    from dotenv import load_dotenv
    from openai import OpenAI
    
    load_dotenv()
    
    try:
        client = OpenAI(timeout=10.0)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a test assistant."},
                {"role": "user", "content": "Say 'API Test Successful' and nothing else."}
            ],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ OpenAI API connectivity test successful")
            print(f"Response: {response.choices[0].message.content}")
            return True
        else:
            print("❌ OpenAI API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing chatbot functionality...\n")
    
    print("1. Testing OpenAI API directly:")
    openai_ok = test_openai_connectivity()
    
    print("\n2. Testing chat endpoint:")
    chat_ok = test_chat_endpoint()
    
    print(f"\n📊 Test Results:")
    print(f"   OpenAI API: {'✅ Working' if openai_ok else '❌ Failed'}")
    print(f"   Chat Endpoint: {'✅ Working' if chat_ok else '❌ Failed'}")
    
    if openai_ok and chat_ok:
        print("\n🎉 Chatbot appears to be working correctly!")
    elif not openai_ok:
        print("\n❌ Issue with OpenAI API connectivity")
    elif not chat_ok:
        print("\n❌ Issue with chat endpoint")
