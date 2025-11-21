#!/usr/bin/env python3
"""
Test script for NVIDIA NIM integration
Run this to verify your NVIDIA API key and model access
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_nvidia_connection():
    """Test basic NVIDIA NIM API connection"""
    
    api_key = os.getenv("NVIDIA_API_KEY")
    model = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
    
    if not api_key:
        print("❌ Error: NVIDIA_API_KEY not found in .env file")
        print("Please add: NVIDIA_API_KEY=nvapi-YOUR_KEY_HERE")
        return False
    
    print(f"✓ API Key found: {api_key[:10]}...")
    print(f"✓ Model: {model}")
    print("\n🔄 Testing NVIDIA NIM connection with streaming...\n")
    
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
        # Test with streaming
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from NVIDIA NIM!' and explain in one sentence what you are."}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=100,
            stream=True
        )
        
        print("📝 Response: ", end="", flush=True)
        full_response = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
        
        print("\n\n✅ Success! NVIDIA NIM is working correctly.")
        print(f"✓ Received {len(full_response)} characters")
        print("✓ Streaming is functional")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your API key is correct")
        print("2. Verify you have access to the model")
        print("3. Visit https://build.nvidia.com/ to manage your API keys")
        return False

def test_ergonomic_analysis():
    """Test NVIDIA with ergonomic analysis prompt"""
    
    api_key = os.getenv("NVIDIA_API_KEY")
    model = os.getenv("NVIDIA_MODEL", "meta/llama-3.1-70b-instruct")
    
    if not api_key:
        return False
    
    print("\n🧪 Testing ergonomic analysis prompt...\n")
    
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
        prompt = """You are an expert ergonomist. Analyze this posture data:

Neck flexion: 35.2° (medium risk)
Shoulder asymmetry: 8.3%
Back lean: 28.4° (medium risk)

Provide a brief 2-sentence assessment."""
        
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are an expert Human Factors researcher and ergonomist."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=200,
            stream=True
        )
        
        print("📊 Ergonomic Analysis: ", end="", flush=True)
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)
        
        print("\n\n✅ Ergonomic analysis test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("NVIDIA NIM Integration Test")
    print("=" * 60)
    
    # Test 1: Basic connection
    test1 = test_nvidia_connection()
    
    if test1:
        # Test 2: Ergonomic analysis
        test2 = test_ergonomic_analysis()
        
        if test2:
            print("\n" + "=" * 60)
            print("🎉 All tests passed! NVIDIA NIM is ready to use.")
            print("=" * 60)
            print("\nYou can now:")
            print("1. Start the backend: python app.py")
            print("2. The platform will use NVIDIA NIM for insights")
            print("3. Check NVIDIA_NIM_SETUP.md for more options")
        else:
            print("\n⚠️  Basic connection works, but ergonomic test failed")
    else:
        print("\n❌ Connection test failed. Please fix the issues above.")
