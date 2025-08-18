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

# グローバル変数としてBotクライアントを初期化
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# Botが起動済みかを確認するフラグ
bot_is_running = False

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時にBotを一度だけ起動する"""
    global bot_is_running
    if not bot_is_running:
        try:
            # Botのバックグラウンドタスクを開始
            asyncio.create_task(client.start(DISCORD_BOT_TOKEN))
            bot_is_running = True
            print("Discord Bot startup task created.")
        except Exception as e:
            print(f"Error starting Discord Bot: {e}")

@app.post("/api/upload")
async def upload_photo(userName: str = Form(...), photo: UploadFile = File(...)):
    if not client.is_ready():
        try:
            # Botがまだ準備できていない場合は待機
            await asyncio.wait_for(client.wait_until_ready(), timeout=15.0)
        except asyncio.TimeoutError:
            print("Error: Bot failed to connect to Discord in time.")
            return {"status": "error", "error": "Bot connection timeout."}, 500

    # チャンネルIDを整数に変換
    try:
        channel_id = int(DISCORD_CHANNEL_ID)
    except (ValueError, TypeError):
        return {"status": "error", "error": "Invalid channel ID."}, 500

    try:
        photo_data = await photo.read()
        score = random.randint(0, 100)
        
        channel = client.get_channel(channel_id)
        if not channel:
            return {"status": "error", "error": "Invalid channel ID or channel not found."}, 500

        message_content = (
            f"**新しい写真がアップロードされました！**\n"
            f"**アップロードした人:** {userName}\n"
            f"**ランダムな点数:** {score}点"
        )
        
        discord_file = discord.File(photo_data, filename="uploaded_photo.jpg")

        await channel.send(content=message_content, file=discord_file)
        print("Sent image and message to Discord.")

        return {"status": "success", "message": "Upload received and processing"}
    except Exception as e:
        print(f"Error processing upload: {e}")
        return {"status": "error", "error": str(e)}, 500
