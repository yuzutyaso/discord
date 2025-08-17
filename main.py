import os
import discord
from dotenv import load_dotenv
from aiohttp import web
import json
import random

load_dotenv()

# 環境変数からトークンとチャンネルIDを読み込み
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
DISCORD_CHANNEL_ID = int(os.getenv('DISCORD_CHANNEL_ID'))

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

async def handle_github_webhook(request):
    try:
        data = await request.json()
        print("Received GitHub webhook event.")

        # プッシュイベントかどうかのチェック
        if 'commits' in data:
            for commit in data['commits']:
                for added_file in commit.get('added', []):
                    # 画像ファイルかどうかのチェック
                    if added_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        repo_url = data['repository']['html_url']
                        image_url = f"{repo_url}/raw/main/{added_file}"
                        user_name = commit['author']['name']
                        
                        # 0から100までのランダムな点数を生成
                        score = random.randint(0, 100)

                        # Discordに送信するメッセージを作成
                        message_content = (
                            f"**新しい写真がアップロードされました！**\n"
                            f"**アップロードした人:** {user_name}\n"
                            f"**ランダムな点数:** {score}点"
                        )

                        channel = client.get_channel(DISCORD_CHANNEL_ID)
                        if channel:
                            # Embedを使ってメッセージと画像を送信
                            embed = discord.Embed(
                                title="画像アップロード通知",
                                description=message_content,
                                color=discord.Color.blue()
                            )
                            embed.set_image(url=image_url)
                            await channel.send(embed=embed)
                            print(f"Sent image to Discord: {image_url}")
    except json.JSONDecodeError:
        print("Invalid JSON received.")
        return web.Response(text="Invalid JSON", status=400)
    except Exception as e:
        print(f"Error handling webhook: {e}")
        return web.Response(text="Error", status=500)
    
    return web.Response(text="OK")

async def start_webserver():
    app = web.Application()
    app.router.add_post('/webhook', handle_github_webhook)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.environ.get('PORT', 8080)))
    await site.start()
    print("Web server started.")

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    client.loop.create_task(start_webserver())

client.run(DISCORD_BOT_TOKEN)
