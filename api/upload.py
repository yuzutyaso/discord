import os
import discord
import asyncio
import random
from fastapi import FastAPI, UploadFile, File, Form, HTTPException

# FastAPIアプリの初期化
app = FastAPI()

# 環境変数をVercelのダッシュボードから直接読み込み
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')

@app.post("/api/upload")
async def upload_photo(userName: str = Form(...), photo: UploadFile = File(...)):
    if not DISCORD_BOT_TOKEN or not DISCORD_CHANNEL_ID:
        raise HTTPException(status_code=500, detail="Discord environment variables not set.")

    intents = discord.Intents.default()
    client = discord.Client(intents=intents)

    # チャンネルIDを整数に変換
    try:
        channel_id = int(DISCORD_CHANNEL_ID)
    except (ValueError, TypeError):
        raise HTTPException(status_code=500, detail="Invalid channel ID. Cannot convert to integer.")

    async def send_to_discord():
        try:
            # BotをDiscordに接続
            await client.login(DISCORD_BOT_TOKEN)
            await client.wait_until_ready()
            
            # メッセージ送信処理
            photo_data = await photo.read()
            score = random.randint(0, 100)
            
            channel = client.get_channel(channel_id)
            if not channel:
                raise HTTPException(status_code=500, detail=f"Channel with ID {channel_id} not found.")

            message_content = (
                f"**新しい写真がアップロードされました！**\n"
                f"**アップロードした人:** {userName}\n"
                f"**ランダムな点数:** {score}点"
            )
            
            discord_file = discord.File(photo_data, filename="uploaded_photo.jpg")

            await channel.send(content=message_content, file=discord_file)
            print("SUCCESS: Image and message sent to Discord.")

        except discord.errors.LoginFailure:
            raise HTTPException(status_code=401, detail="Invalid Discord Bot Token.")
        except HTTPException:
            raise
        except Exception as e:
            print(f"ERROR: Error processing upload: {e}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
        finally:
            # 処理が完了したら接続を閉じる
            if not client.is_closed():
                await client.close()

    try:
        # 非同期タスクとして実行
        await send_to_discord()
        return {"status": "success", "message": "Upload received and processing"}
    except HTTPException as e:
        return {"status": "error", "error": e.detail}, e.status_code
