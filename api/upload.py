import os
import discord
import asyncio
import random
from fastapi import FastAPI, UploadFile, File, Form
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

# FastAPIアプリの初期化
app = FastAPI()

# Discord Botのクライアントを初期化
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
bot_ready = asyncio.Event()

# チャンネルIDを整数に変換
try:
    CHANNEL_ID = int(DISCORD_CHANNEL_ID)
except (ValueError, TypeError):
    CHANNEL_ID = None

# Botがログインするまで待機
@client.event
async def on_ready():
    bot_ready.set()
    print(f'Logged in as {client.user}')

async def run_bot():
    try:
        await client.start(DISCORD_BOT_TOKEN)
    except Exception as e:
        print(f"Error starting bot: {e}")

# Botの実行をバックグラウンドタスクとして開始
asyncio.create_task(run_bot())

@app.post("/api/upload")
async def upload_photo(userName: str = Form(...), photo: UploadFile = File(...)):
    if not bot_ready.is_set():
        await asyncio.wait_for(bot_ready.wait(), timeout=10.0)

    try:
        photo_data = await photo.read()
        score = random.randint(0, 100)
        
        channel = client.get_channel(CHANNEL_ID)
        if not channel:
            return {"status": "error", "error": "Invalid channel ID or channel not found."}, 500

        # Discordに送信するメッセージを作成
        message_content = (
            f"**新しい写真がアップロードされました！**\n"
            f"**アップロードした人:** {userName}\n"
        )
        
        discord_file = discord.File(photo_data, filename="uploaded_photo.jpg")

        await channel.send(content=message_content, file=discord_file)
        print("Sent image and message to Discord.")

        return {"status": "success", "message": "Upload received and processing"}

    except Exception as e:
        print(f"Error processing upload: {e}")
        return {"status": "error", "error": str(e)}, 500
