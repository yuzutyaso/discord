import os
import discord
from dotenv import load_dotenv
from aiohttp import web
import json
import random
import asyncio

load_dotenv()

# 環境変数からトークンとチャンネルIDを読み込み
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# Intentsの設定
intents = discord.Intents.default()
# 以下のIntentsは今回使用しませんが、今後の拡張のために残します。
# intents.message_content = True
# intents.members = True

client = discord.Client(intents=intents)

# チャンネルIDが整数に変換できるか確認
try:
    CHANNEL_ID = int(DISCORD_CHANNEL_ID)
except (ValueError, TypeError):
    print("Error: DISCORD_CHANNEL_ID is not a valid integer.")
    CHANNEL_ID = None

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
        if CHANNEL_ID:
            asyncio.create_task(upload_to_discord(user_name, photo_data))
            return web.json_response({"status": "success", "message": "Upload received and processing"})
        else:
            print("Error: Invalid channel ID. Cannot upload to Discord.")
            return web.json_response({"status": "error", "error": "Invalid channel ID."}, status=500)

    except Exception as e:
        print(f"Error handling upload: {e}")
        return web.json_response({"status": "error", "error": str(e)}, status=500)

# 写真をDiscordにアップロードするための非同期関数
async def upload_to_discord(user_name, photo_data):
    try:
        score = random.randint(0, 100)
        channel = client.get_channel(CHANNEL_ID)

        if not channel:
            print(f"Error: Channel with ID {CHANNEL_ID} not found.")
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

client.run(DISCORD_BOT_TOKEN)import os
import discord
from dotenv import load_dotenv
from aiohttp import web
import json
import random
import asyncio

load_dotenv()

# 環境変数からトークンとチャンネルIDを読み込み
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

# Intentsの設定
intents = discord.Intents.default()
# 以下のIntentsは今回使用しませんが、今後の拡張のために残します。
# intents.message_content = True
# intents.members = True

client = discord.Client(intents=intents)

# チャンネルIDが整数に変換できるか確認
try:
    CHANNEL_ID = int(DISCORD_CHANNEL_ID)
except (ValueError, TypeError):
    print("Error: DISCORD_CHANNEL_ID is not a valid integer.")
    CHANNEL_ID = None

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
        if CHANNEL_ID:
            asyncio.create_task(upload_to_discord(user_name, photo_data))
            return web.json_response({"status": "success", "message": "Upload received and processing"})
        else:
            print("Error: Invalid channel ID. Cannot upload to Discord.")
            return web.json_response({"status": "error", "error": "Invalid channel ID."}, status=500)

    except Exception as e:
        print(f"Error handling upload: {e}")
        return web.json_response({"status": "error", "error": str(e)}, status=500)

# 写真をDiscordにアップロードするための非同期関数
async def upload_to_discord(user_name, photo_data):
    try:
        score = random.randint(0, 100)
        channel = client.get_channel(CHANNEL_ID)

        if not channel:
            print(f"Error: Channel with ID {CHANNEL_ID} not found.")
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
