import time
import os
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
    """Load the last post ID we've already sent"""
    try:
        with open(STATE_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def save_last_post_id(post_id):
    """Save the last post ID so we don't send duplicates"""
    with open(STATE_FILE, 'w') as f:
        f.write(str(post_id))

def check_for_new_posts():
    """Main function: check for new posts and send them to Telegram"""
    print(f"\n⏰ Checking at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🔄 Fetching posts from Facebook...")
    
    try:
        # Get posts from Facebook
        posts = []
        for post in get_posts(FACEBOOK_PAGE, pages=1):
            post_data = {
                "id": post.get("post_id", ""),
                "text": post.get("text", ""),
                "image": post.get("image", ""),
                "images": post.get("images", []),
                "url": post.get("post_url", ""),
                "time": post.get("time", datetime.now())
            }
            posts.append(post_data)
            print(f"📄 Found post: {post_data['text'][:50] if post_data['text'] else 'No text'}...")
        
        if not posts:
            print("❌ No posts found on Facebook page.")
            print("💡 This could mean:")
            print("   - Fabrizio hasn't posted recently")
            print("   - Facebook is blocking the request")
            print("   - The page name is incorrect")
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
            # Update state with latest post if needed
            if posts and last_id != posts[0]["id"]:
                save_last_post_id(posts[0]["id"])
                print(f"💾 Updated state to latest post: {posts[0]['id'][:20]}...")
            return
        
        print(f"🎯 Found {len(new_posts)} new post(s)!")
        
        # Initialize Telegram bot
        bot = Bot(token=TELEGRAM_TOKEN)
        
        # Send each new post (oldest first)
        for post in reversed(new_posts):
            print(f"\n📨 Sending post: {post['id'][:30]}...")
            
            # Build the message
            message = f"📢 *NEW POST FROM FABRIZIO ROMANO!*\n\n"
            
            if post["text"]:
                # Truncate if too long (Telegram limit: 4096 characters)
                text = post["text"][:4000]
                message += text
            else:
                message += "(No text content)"
            
            message += f"\n\n🔗 [View Original Post]({post['url']})"
            
            # Send text message
            try:
                bot.send_message(
                    chat_id=CHAT_ID,
                    text=message,
                    parse_mode="Markdown",
                    disable_web_page_preview=True
                )
                print("✅ Text sent")
            except TelegramError as e:
                print(f"❌ Failed to send text: {e}")
            
            # Send images
            images_sent = 0
            
            # Try sending multiple images
            if post.get("images"):
                for img_url in post["images"][:3]:  # Max 3 images
                    try:
                        bot.send_photo(
                            chat_id=CHAT_ID,
                            photo=img_url,
                            caption=f"📸 Image {images_sent + 1}" if images_sent > 0 else "📸 Image from the post"
                        )
                        images_sent += 1
                        print(f"✅ Image {images_sent} sent")
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"❌ Failed to send image: {e}")
            
            # Fallback: try single image if no images array
            elif post.get("image") and images_sent == 0:
                try:
                    bot.send_photo(
                        chat_id=CHAT_ID,
                        photo=post["image"],
                        caption="📸 Image from the post"
                    )
                    print("✅ Image sent")
                except Exception as e:
                    print(f"❌ Failed to send image: {e}")
            
            # Save the post ID so we don't send it again
            save_last_post_id(post["id"])
            print(f"💾 Saved state: {post['id'][:30]}...")
            time.sleep(1)  # Avoid rate limits
        
        # Update with the absolute latest post
        if posts and posts[0]["id"] != load_last_post_id():
            save_last_post_id(posts[0]["id"])
            print(f"💾 Updated to latest post: {posts[0]['id'][:30]}...")
        
        print("\n✅ Check complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

# ===== MAIN ENTRY POINT =====
if __name__ == "__main__":
    # Test Telegram connection first
    try:
        print("🔌 Testing Telegram connection...")
        bot = Bot(token=TELEGRAM_TOKEN)
        bot.send_message(
            chat_id=CHAT_ID,
            text="🟢 Bot is starting up! Monitoring Fabrizio Romano...\n\n⏳ Will check for new posts every 15 minutes."
        )
        print("✅ Telegram connection successful!")
    except Exception as e:
        print(f"❌ Failed to connect to Telegram: {e}")
        print("Please check your TOKEN and CHAT_ID")
        exit(1)
    
    # Run the check
    check_for_new_posts()
    
    print("\n" + "=" * 60)
    print("✅ Bot ran successfully!")
    print("To run it again: python main.py")
    print("For automatic 24/7 operation, we'll set up GitHub Actions next.")
    print("=" * 60)