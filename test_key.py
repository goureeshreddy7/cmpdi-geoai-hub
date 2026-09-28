"""
Quick diagnostic — run this in PowerShell to find what's wrong with your API key.
Usage: python test_key.py YOUR_API_KEY_HERE
"""
import sys
import requests

API_KEY = sys.argv[1] if len(sys.argv) > 1 else input("Paste your API key: ").strip()

BASE = "https://generativelanguage.googleapis.com"
MODELS = ["gemini-2.0-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro", "gemini-1.0-pro"]

print(f"\n{'='*60}")
print(f"Testing API Key: {API_KEY[:20]}...")
print(f"{'='*60}\n")

# Step 1: Try to list models
print("[ STEP 1 ] Listing available models...")
for ver in ["v1beta", "v1"]:
    r = requests.get(f"{BASE}/{ver}/models", params={"key": API_KEY}, timeout=15)
    print(f"  {ver}/models → HTTP {r.status_code}")
    if r.status_code == 200:
        models = r.json().get("models", [])
        print(f"  Found {len(models)} models:")
        for m in models[:10]:
            print(f"    - {m.get('name')}")
        break
    else:
        print(f"  Error: {r.json().get('error', {}).get('message', 'Unknown')}")

print()

# Step 2: Try generating content
print("[ STEP 2 ] Testing generateContent...")
for model in MODELS:
    for ver in ["v1beta", "v1"]:
        url = f"{BASE}/{ver}/models/{model}:generateContent"
        payload = {"contents": [{"parts": [{"text": "Say hi"}]}]}
        r = requests.post(url, params={"key": API_KEY}, json=payload, timeout=15)
        status = "✅ WORKS!" if r.status_code == 200 else f"❌ {r.status_code}"
        print(f"  {ver}/{model}: {status}")
        if r.status_code == 200:
            print(f"\n{'='*60}")
            print(f"✅ SUCCESS! Use this model: {model}")
            print(f"{'='*60}\n")
            sys.exit(0)
        elif r.status_code != 404:
            err = r.json().get('error', {}).get('message', '')
            print(f"     → {err[:80]}")

print(f"\n{'='*60}")
print("❌ NO MODELS WORK. Possible reasons:")
print("  1. Invalid API key — get a fresh one at https://aistudio.google.com/app/apikey")
print("  2. Gemini API not enabled for this project")
print("  3. Billing not set up (for some models)")
print("  4. Network/firewall blocking the API")
print(f"{'='*60}\n")
