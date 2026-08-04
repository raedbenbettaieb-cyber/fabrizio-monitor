import requests
import time

TOKEN = "8936438800:AAF0TyJ7A2lZk1Tq0BQXYBplqACPHKCwNOM"

print("=" * 50)
print("🔍 TELEGRAM BOT DIAGNOSTIC")
print("=" * 50)

# Step 1: Check if token works
print("\n1️⃣ Checking token...")
try:
    url = f"https://api.telegram.org/bot{TOKEN}/getMe"
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if data["ok"]:
        bot_name = data["result"]["first_name"]
        bot_username = data["result"]["username"]
        print(f"✅ Token is valid!")
        print(f"   Bot name: {bot_name}")
        print(f"   Bot username: @{bot_username}")
    else:
        print(f"❌ Token invalid: {data}")
        exit()
except Exception as e:
    print(f"❌ Connection error: {e}")
    exit()

# Step 2: Get updates
print("\n2️⃣ Checking for messages...")
print("   (Make sure you've sent a message to your bot first!)")
time.sleep(1)

url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?timeout=5"
try:
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if data["ok"] and data["result"]:
        print("✅ Found messages!")
        for update in data["result"]:
            if "message" in update:
                msg = update["message"]
                chat_id = msg["chat"]["id"]
                chat_type = msg["chat"]["type"]
                text = msg.get("text", "No text")
                print(f"\n   📨 Message: {text[:50]}")
                print(f"   📱 Chat ID: {chat_id}")
                print(f"   📊 Chat type: {chat_type}")
    else:
        print("❌ No messages found!")
        print("   📝 Please:")
        print("   1. Open Telegram")
        print("   2. Search for @your_bot_username")
        print("   3. Click 'Start' or send 'Hello'")
        print("   4. Run this script again")
        exit()
except Exception as e:
    print(f"❌ Error: {e}")
    exit()

# Step 3: Send test message
print("\n3️⃣ Sending test message...")
chat_id = data["result"][0]["message"]["chat"]["id"]
print(f"   Using Chat ID: {chat_id}")

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": "🟢 Test message! Your bot is working correctly!",
    "parse_mode": "Markdown"
}

try:
    response = requests.post(url, json=payload, timeout=10)
    result = response.json()
    
    if result["ok"]:
        print("✅ Test message sent successfully!")
        print("   Check Telegram on your phone/computer!")
    else:
        print(f"❌ Failed: {result}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Diagnostic complete!")