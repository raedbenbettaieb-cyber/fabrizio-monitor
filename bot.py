import os
import time
import json
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from apify_client import ApifyClient

# ===== CONFIGURATION (Read from environment variables) =====
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "8936438800:AAF0TyJ7A2lZk1Tq0BQXYBplqACPHKCwNOM")
CHAT_ID = os.environ.get("CHAT_ID", "6002099959")
APIFY_API_KEY = os.environ.get("APIFY_API_KEY", "")  # ← Read from environment, NOT hardcoded!
STATE_FILE = "last_post_id.txt"
FACEBOOK_PAGE = "fabrizioromanoherewego"

print("=" * 60)
print("🤖 FABRIZIO ROMANO MONITOR BOT (Cloud Version)")
print("=" * 60)
print(f"📱 Bot: @abrizioMonitorBot")
print(f"👤 Chat ID: {CHAT_ID}")
print(f"📄 Tracking: {FACEBOOK_PAGE}")
print(f"🔗 URL: https://www.facebook.com/{FACEBOOK_PAGE}")
print(f"🔑 Apify API: {'✅ Set' if APIFY_API_KEY else '❌ Missing!'}")
print("=" * 60)

def load_last_post_id():
    try:
        with open(STATE_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_post_id(post_id):
    with open(STATE_FILE, 'w') as f:
        f.write(str(post_id))

def get_facebook_posts(page_name, limit=3):
    """Fetch posts using Apify API (Reliable & cloud-friendly)"""
    if not APIFY_API_KEY:
        print("❌ No Apify API key found!")
        print("📝 Get one at: https://apify.com/settings/integrations")
        return []
    
    try:
        print(f"🔄 Fetching posts from Facebook page: {page_name}")
        print(f"🔗 URL: https://www.facebook.com/{page_name}")
        
        client = ApifyClient(APIFY_API_KEY)
        
        run_input = {
            "startUrls": [{"url": f"https://www.facebook.com/{page_name}"}],
            "maxPosts": limit,
            "scrapeComments": False,
            "scrapeReactions": False,
            "scrapeImages": True,
        }
        
        run = client.actor("apify/facebook-posts-scraper").call(run_input=run_input)
        
        posts = []
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            post_data = {
                "id": item.get("id", ""),
                "text": item.get("text", item.get("content", "")),
                "image": item.get("imageUrls", [None])[0] if item.get("imageUrls") else None,
                "images": item.get("imageUrls", []),
                "url": item.get("url", ""),
                "timestamp": item.get("timestamp", str(datetime.now()))
            }
            posts.append(post_data)
            print(f"📄 Found post: {post_data['text'][:50] if post_data['text'] else 'Image post'}...")
        
        print(f"✅ Found {len(posts)} post(s) via Apify")
        return posts
        
    except Exception as e:
        print(f"❌ Apify error: {e}")
        return []

async def send_post_to_telegram(bot, post):
    try:
        message = f"📢 *NEW POST FROM FABRIZIO ROMANO!*\n\n"
        if post.get("text"):
            text = post["text"][:4000]
            message += text
        else:
            message += "(No text content)"
        
        message += f"\n\n🔗 [View Original]({post.get('url', '#')})"
        
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        print("✅ Text sent")
        
        images = post.get("images", [])
        if images:
            for img_url in images[:3]:
                try:
                    await bot.send_photo(
                        chat_id=CHAT_ID,
                        photo=img_url,
                        caption="📸 Image from the post"
                    )
                    print("✅ Image sent")
                    await asyncio.sleep(0.5)
                except Exception as e:
                    print(f"❌ Failed to send image: {e}")
        elif post.get("image"):
            try:
                await bot.send_photo(
                    chat_id=CHAT_ID,
                    photo=post["image"],
                    caption="📸 Image from the post"
                )
                print("✅ Image sent")
            except Exception as e:
                print(f"❌ Failed to send image: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

async def check_for_new_posts():
    print(f"\n⏰ Checking at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    posts = get_facebook_posts(FACEBOOK_PAGE, limit=5)
    
    if not posts:
        print("❌ No posts retrieved from Apify.")
        print("💡 Check your Apify API key and try again.")
        return
    
    last_id = load_last_post_id()
    new_posts = []
    
    for post in reversed(posts):
        if post["id"] == last_id:
            print(f"⏹️ Found already-seen post")
            break
        new_posts.append(post)
    
    if not new_posts:
        print("📭 No new posts found.")
        if posts and last_id != posts[0]["id"]:
            save_last_post_id(posts[0]["id"])
        return
    
    print(f"🎯 Found {len(new_posts)} new post(s)!")
    
    bot = Bot(token=TELEGRAM_TOKEN)
    
    for post in reversed(new_posts):
        print(f"\n📨 Sending post: {post['id'][:30]}...")
        success = await send_post_to_telegram(bot, post)
        if success:
            save_last_post_id(post["id"])
            print(f"💾 Saved state")
        await asyncio.sleep(1)
    
    if posts:
        save_last_post_id(posts[0]["id"])
    
    print("\n✅ Check complete!")

async def main():
    try:
        print("🔌 Testing Telegram connection...")
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"🟢 Bot is starting up!\n\n📱 Monitoring Fabrizio Romano\n🔗 {FACEBOOK_PAGE}\n⏳ Will check every 15 minutes"
        )
        print("✅ Telegram connection successful!")
    except Exception as e:
        print(f"❌ Failed to connect to Telegram: {e}")
        return
    
    await check_for_new_posts()
    
    print("\n" + "=" * 60)
    print("✅ Bot execution complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())