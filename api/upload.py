import os
import aiohttp
import asyncio
import random
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

@app.post("/api/upload")
async def upload_photo(userName: str = Form(...), photo: UploadFile = File(...)):
    if not DISCORD_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="Discord Webhook URL not set.")

    try:
        photo_data = await photo.read()
        score = random.randint(0, 100)
        
        # Webhookに送信するデータを準備
        data = aiohttp.FormData()
        payload = {
            "content": (
                f"**新しい写真がアップロードされました！**\n"
                f"**アップロードした人:** {userName}\n"
                f"**ランダムな点数:** {score}点"
            )
        }
        data.add_field('payload_json', str(payload))
        data.add_field('file', photo_data, filename="uploaded_photo.jpg", content_type="image/jpeg")
        
        # aiohttpを使ってWebhookに直接POSTリクエストを送信
        async with aiohttp.ClientSession() as session:
            async with session.post(DISCORD_WEBHOOK_URL, data=data) as response:
                response.raise_for_status()
                print("SUCCESS: Image and message sent to Discord via Webhook.")
        
        return {"status": "success", "message": "Upload received and processing"}
    except aiohttp.ClientResponseError as e:
        print(f"ERROR: Discord Webhook failed with status code: {e.status}")
        raise HTTPException(status_code=500, detail=f"Discord Webhook error: {e.status}")
    except Exception as e:
        print(f"ERROR: Error processing upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
