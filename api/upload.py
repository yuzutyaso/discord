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

# 環境変数からトークンとチャンネルIDを読み込み
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# チャンネルIDを整数に変換
try:
    CHANNEL_ID = int(DISCORD_CHANNEL_ID)
except (ValueError, TypeError):
    CHANNEL_ID = None

# Discord Botのクライアントを初期化
intents = discord.Intents.default()
client = discord.Client(intents=intents)

async def send_to_discord(user_name: str, photo_data: bytes):
    """Discordにメッセージと画像を送信する非同期関数"""
    try:
        score = random.randint(0, 100)
        channel = client.get_channel(CHANNEL_ID)
        
        if not channel:
            print(f"Error: Channel with ID {CHANNEL_ID} not found.")
            return

        message_content = (
            f"**新しい写真がアップロードされました！**\n"
            f"**アップロードした人:** {user_name}\n"
            f"**ランダムな点数:** {score}点"
        )
        
        discord_file = discord.File(photo_data, filename="uploaded_photo.jpg")

        await channel.send(content=message_content, file=discord_file)
        print("Sent image and message to Discord.")

    except Exception as e:
        print(f"Error uploading to Discord: {e}")

@app.post("/api/upload")
async def upload_photo(userName: str = Form(...), photo: UploadFile = File(...)):
    if not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_ID:
        return {"status": "error", "error": "Discord environment variables not set."}, 500

    if CHANNEL_ID is None:
        return {"status": "error", "error": "Invalid channel ID."}, 500

    try:
        # Botを起動し、Discordと接続
        # この部分がVercelのライフサイクルに合わせて修正された重要な部分です
        asyncio.create_task(client.start(DISCORD_BOT_TOKEN))
        await client.wait_until_ready()
        
        photo_data = await photo.read()
        await send_to_discord(userName, photo_data)
        
        # Botをシャットダウン
        await client.close()

        return {"status": "success", "message": "Upload received and processing"}
    except Exception as e:
        print(f"Error processing upload: {e}")
        return {"status": "error", "error": str(e)}, 500
