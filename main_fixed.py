import time
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
from facebook_scraper import get_posts

# ===== CONFIGURATION =====
TELEGRAM_TOKEN = "8936438800:AAF0TyJ7A2lZk1Tq0BQXYBplqACPHKCwNOM"
CHAT_ID = "6002099959"
STATE_FILE = "last_post_id.txt"
FACEBOOK_PAGE = "FabrizioRomano"

print("=" * 60)
print("🤖 FABRIZIO ROMANO MONITOR BOT")
print("=" * 60)
print(f"📱 Bot: @abrizioMonitorBot")
print(f"👤 Chat ID: {CHAT_ID}")
print(f"📄 Tracking: {FACEBOOK_PAGE}")
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

async def send_post_to_telegram(bot, post):
    """Send a single post to Telegram"""
    try:
        # Build the message
        message = f"📢 *NEW POST FROM FABRIZIO ROMANO!*\n\n"
        if post.get("text"):
            text = post["text"][:4000]
            message += text
        else:
            message += "(No text content)"
        
        message += f"\n\n🔗 [View Original Post]({post.get('url', '#')})"
        
        # Send text
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        print("✅ Text sent")
        
        # Send images
        if post.get("images"):
            for img_url in post["images"][:3]:
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
    except TelegramError as e:
        print(f"❌ Telegram error: {e}")
        return False

async def check_for_new_posts():
    """Main function: check for new posts and send them"""
    print(f"\n⏰ Checking at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔄 Fetching posts from Facebook...")
    
    try:
        # Increase pages to get more results
        posts = []
        try:
            # Try with higher page count
            for post in get_posts(FACEBOOK_PAGE, pages=3, options={"allow_extra_requests": True}):
                post_data = {
                    "id": post.get("post_id", ""),
                    "text": post.get("text", ""),
                    "image": post.get("image", ""),
                    "images": post.get("images", []),
                    "url": post.get("post_url", ""),
                    "time": post.get("time", datetime.now())
                }
                if post_data["text"] or post_data["images"]:  # Only add posts with content
                    posts.append(post_data)
                    print(f"📄 Found post: {post_data['text'][:50] if post_data['text'] else 'Image post'}...")
                if len(posts) >= 5:  # Limit to 5 most recent
                    break
        except Exception as e:
            print(f"⚠️ Scraper error: {e}")
            print("🔄 Trying alternative approach...")
            # Try without options
            try:
                for post in get_posts(FACEBOOK_PAGE, pages=2):
                    post_data = {
                        "id": post.get("post_id", ""),
                        "text": post.get("text", ""),
                        "image": post.get("image", ""),
                        "images": post.get("images", []),
                        "url": post.get("post_url", ""),
                        "time": post.get("time", datetime.now())
                    }
                    if post_data["text"] or post_data["images"]:
                        posts.append(post_data)
                        print(f"📄 Found post: {post_data['text'][:50] if post_data['text'] else 'Image post'}...")
                    if len(posts) >= 5:
                        break
            except Exception as e2:
                print(f"❌ Alternative also failed: {e2}")
                return
        
        if not posts:
            print("\n❌ No posts found on Facebook page.")
            print("\n💡 This usually means Facebook is blocking the request.")
            print("   Here's how to fix it:")
            print("   1. Get cookies from Facebook (I'll show you how)")
            print("   2. Use the Apify version (more reliable)")
            print("\n📝 To use cookies:")
            print("   - Log into Facebook in your browser")
            print("   - Install 'Cookie-Editor' extension")
            print("   - Export cookies as 'cookies.json'")
            print("   - Save it in this folder")
            return
        
        print(f"✅ Found {len(posts)} post(s)")
        
        # Check which posts are new
        last_id = load_last_post_id()
        new_posts = []
        
        # Process from oldest to newest
        for post in reversed(posts):
            if post["id"] == last_id:
                print(f"⏹️ Found already-seen post: {post['id'][:20]}...")
                break
            new_posts.append(post)
        
        if not new_posts:
            print("📭 No new posts found.")
            if posts and last_id != posts[0]["id"]:
                save_last_post_id(posts[0]["id"])
                print(f"💾 Updated state to latest post: {posts[0]['id'][:20]}...")
            return
        
        print(f"🎯 Found {len(new_posts)} new post(s)!")
        
        # Initialize bot
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Send each new post
        for post in reversed(new_posts):
            print(f"\n📨 Sending post: {post['id'][:30]}...")
            success = await send_post_to_telegram(bot, post)
            if success:
                save_last_post_id(post["id"])
                print(f"💾 Saved state: {post['id'][:30]}...")
            await asyncio.sleep(1)  # Avoid rate limits
        
        # Update with latest post
        if posts and posts[0]["id"] != load_last_post_id():
            save_last_post_id(posts[0]["id"])
            print(f"💾 Updated to latest post: {posts[0]['id'][:30]}...")
        
        print("\n✅ Check complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    """Main async entry point"""
    # Test Telegram connection
    try:
        print("🔌 Testing Telegram connection...")
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(
            chat_id=CHAT_ID,
            text="🟢 Bot is starting up! Monitoring Fabrizio Romano...\n\n⏳ Will check for new posts."
        )
        print("✅ Telegram connection successful!")
    except Exception as e:
        print(f"❌ Failed to connect to Telegram: {e}")
        print("Please check your TOKEN and CHAT_ID")
        return
    
    # Run the check
    await check_for_new_posts()
    
    print("\n" + "=" * 60)
    print("✅ Bot ran successfully!")
    print("To run it again: python main_fixed.py")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())