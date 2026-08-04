# 🤖 Fabrizio Romano Telegram Monitor

[![GitHub Actions](https://img.shields.io/badge/Automated%20via-GitHub%20Actions-blue?logo=github-actions)](https://github.com/features/actions)
[![Telegram](https://img.shields.io/badge/Bot-@abrizioMonitorBot-blue?logo=telegram)](https://t.me/abrizioMonitorBot)
[![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Online-brightgreen)](https://github.com/raedbenbettaieb-cyber/fabrizio-monitor/actions)

An automated Telegram bot that monitors Fabrizio Romano's Facebook page and instantly sends his transfer news, "Here we go!" announcements, and updates directly to your Telegram. The bot runs 24/7 for free using GitHub Actions, checks every 15 minutes, scrapes posts via Apify, and sends text with images while preventing duplicates. Simply add your Telegram token, chat ID, and Apify API key as GitHub secrets, then deploy with one click.

## 📸 What You Get

When Fabrizio posts, you receive instantly:
📢 NEW POST FROM FABRIZIO ROMANO!

Mika Godts said this some time ago: "The three best players
in the world right now? Dembélé, Nuno Mendes and Yamal"

🔗 View Original Post
📸 [Image attached]

## ✨ Features

- 🚀 Real-time monitoring - Checks every 15 minutes
- 📱 Instant notifications - Get posts directly on Telegram
- 🖼️ Image support - Sends post images with captions
- 🔄 Smart tracking - No duplicate notifications
- ☁️ 100% Cloud-based - Runs 24/7 without any hardware
- 💰 Completely FREE - Uses GitHub Actions + Apify free tier
- ⚡ Easy to deploy - Fork, configure, and run in 5 minutes!

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python 3.10 | Core bot logic |
| Apify Client | Facebook scraping |
| python-telegram-bot | Telegram integration |
| GitHub Actions | Free 24/7 hosting |
| GitHub Secrets | Secure credential storage |

## 🚀 Quick Setup

### Prerequisites

- [GitHub Account](https://github.com) (free)
- [Telegram Account](https://telegram.org) (free)
- [Apify Account](https://apify.com) (free)

### Step 1: Get Your Telegram Credentials

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and choose a name
3. Save your bot token
4. Send a message to your new bot
5. Get your Chat ID from `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`

### Step 2: Get Apify API Key

1. Go to [apify.com/settings/integrations](https://apify.com/settings/integrations)
2. Click **"Create new API token"**
3. Copy your API key

### Step 3: Deploy to GitHub

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:

| Secret Name | Your Value |
|-------------|------------|
| TELEGRAM_TOKEN | Your bot token |
| CHAT_ID | Your chat ID |
| APIFY_API_KEY | Your Apify API key |

3. Go to **Actions** tab
4. Click **"Run workflow"** → **"Run workflow"**
5. Check your Telegram!

## 📁 Project Structure
fabrizio-monitor/
├── .github/workflows/
│ └── monitor1.yml
├── bot.py
├── requirements.txt
├── .gitignore
└── README.md
## 📦 Dependencies
python-telegram-bot==20.7
apify-client==1.6.1
requests==2.31.0

## ⚙️ Configuration

### Change Check Frequency

Edit `.github/workflows/monitor1.yml`:

```yaml
# Every 15 minutes (default)
- cron: '*/15 * * * *'

# Every 5 minutes (more frequent)
- cron: '*/5 * * * *'

# Every hour (less frequent)
- cron: '0 * * * *'

###  Monitor Different Page

python
FACEBOOK_PAGE = "fabrizioromanoherewego"  # Change this
