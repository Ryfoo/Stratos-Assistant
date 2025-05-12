# 🤖 STRATOS ASSISTANT

**STRATOS ASSISTANT** is a custom-built Discord bot for the [STRATOS Scientific Club], designed to organize and manage coding competitions efficiently within a Discord server. From sign-ups and announcements to score tracking and leaderboards — this bot keeps your tech community engaged and running smoothly.

---

## 🚀 Features

- 📝 Registration for coding competitions
- 📅 Automated scheduling and countdowns
- 🔔 Competition announcements and reminders
- 📩 Submission handling (text, links, or file uploads)
- 🧮 Auto-scoring and leaderboard generation
- 🎖️ Role rewards or tags for winners (optional)


## 📸 Screenshots / Demo

*Coming soon* – add screenshots or a short video demo of the bot in action here.

---

## 🛠 Setup Instructions

✅ 1. Environment Setup
A. Install Python and Dependencies

Make sure Python 3.8+ is installed. Then install required packages:

`pip install -U discord.py`

✅ 2. Stratos Assistant Folder Structure

Stratos-Assistant/
├── Driver.py
├── scores.py
├── scores.json
└── requirements.txt


✅ 3. Create the Bot on Discord

    Go to Discord Developer Portal

    Click New Application

    Name it and go to Bot > Add Bot

    Copy the Bot Token (used in config.py)

    Under OAuth2 > URL Generator:

        Scopes: bot

        Bot Permissions: Send Messages, Manage Messages, Read Message History

        Use generated URL to invite your bot to your server.

✅ 4. Setup Configuration (config.py)

# config file

make an '.env. file and copy paste this with changing the discord bot token according to yours:

TOKEN = "YOUR_DISCORD_BOT_TOKEN"  # Replace with your actual bot token

✅ 5. Create scores.json

make a scores.json file with this structure

{
    "teams":{
        "TEAM1_ROLE_ID":{
            "points": 0,
            "eliminated": false
        },
        "TEAM2_ROLE_ID":{
            "points": 0,
            "eliminated": false
        },
        .
        .
        .
        "TEAMn_ROLE_ID":{
            "points": 0,
            "eliminated": false
        }
    }
}

✅ 7. Run the Bot

`pyhton Driver.py`

✅ 8. Usage Guide
🎮 Start a Match:
`/startmatch @Team1 @Team2 #room https://leetcode.com/problems/example`

🔄 Reset Scores:
`/reset_scores`

clear messages:

`/clear n messages`





## 🧾 License

This project is licensed under the **GNU General Public License v3.0**.  
You are free to use, modify, and distribute it under the same license terms.  
See the [LICENSE](./LICENSE) file for full details.