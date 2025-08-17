import os
import discord
import requests
from dotenv import load_dotenv
from aiohttp import web
import json
import random
import aiohttp
import asyncio

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 写真をDiscordにアップロードするための非同期関数
async def upload_to_discord(user_name, photo_data):
    try:
        score = random.randint(0, 100)
        channel = client.get_channel(DISCORD_CHANNEL_ID)

        if not channel:
            print(f"Error: Channel with ID {DISCORD_CHANNEL_ID} not found.")
            return

        # Discordに送信するメッセージを作成
        message_content = (
            f"**新しい写真がアップロードされました！**\n"
            f"**アップロードした人:** {user_name}\n"
            f"**ランダムな点数:** {score}点"
        )
        
        # バイナリデータとしてファイルを送信
        discord_file = discord.File(photo_data, filename="uploaded_photo.jpg")

        await channel.send(content=message_content, file=discord_file)
        print("Sent image and message to Discord.")

    except Exception as e:
        print(f"Error uploading to Discord: {e}")

# HTMLからのアップロードを処理するハンドラ
async def handle_upload(request):
    try:
        reader = await request.multipart()
        
        # フォームからデータを読み取る
        field = await reader.next()
        user_name = await field.read_text()
        
        field = await reader.next()
        photo_data = await field.read()
        
        # Discordへのアップロードをタスクとして実行
        asyncio.create_task(upload_to_discord(user_name, photo_data))
        
        return web.json_response({"status": "success", "message": "Upload received and processing"})

    except Exception as e:
        print(f"Error handling upload: {e}")
        return web.json_response({"status": "error", "error": str(e)}, status=500)

async def start_webserver():
    app = web.Application()
    
    # ルートパスに静的ファイル（HTML）を配信する
    app.router.add_get('/', lambda r: web.FileResponse('./index.html'))
    
    # アップロード用のPOSTエンドポイント
    app.router.add_post('/upload', handle_upload)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()
    print("Web server started.")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    asyncio.create_task(start_webserver())

client.run(DISCORD_BOT_TOKEN)
