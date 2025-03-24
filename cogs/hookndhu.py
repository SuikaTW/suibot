import discord
from discord.ext import commands, tasks
import requests
from bs4 import BeautifulSoup
import json
from core.cogs import Cog_Extention
with open('setting.json', mode="r", encoding='utf8') as jfile:
    jdata = json.load(jfile)

class HookNDHU(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.latest_article = None  # 儲存最新文章的標題
        self.check_updates.start()  # 啟動定時任務

    def fetch_latest_article(self):
        """抓取網站最新文章"""
        url = "https://www.ndhu.edu.tw/p/422-1000-1181.php?Lang=zh-tw"
        response = requests.get(url)
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        article = soup.find("div", class_="list-item")  # 根據網站結構調整選擇器
        if article:
            title = article.find("a").text.strip()
            link = article.find("a")["href"]
            return {"title": title, "link": link}
        return None

    @tasks.loop(seconds=300)  # 每 5 分鐘檢查一次
    async def check_updates(self):
        """檢查網站是否有新文章"""
        webhook_url = jdata.get("webhook_url")  # 從設定檔中讀取 Webhook URL
        if not webhook_url:
            return

        latest_article = self.fetch_latest_article()
        if not latest_article:
            return

        # 如果有新文章，且標題不同於之前的，則發送通知
        if self.latest_article != latest_article["title"]:
            self.latest_article = latest_article["title"]
            embed = {
                "title": "📢 東華大學最新公告",
                "description": f"[{latest_article['title']}]({latest_article['link']})",
                "color": 3447003  # Discord Embed 顏色 (藍色)
            }
            data = {
                "embeds": [embed]
            }
            # 發送 Webhook 請求
            requests.post(webhook_url, json=data)

    @check_updates.before_loop
    async def before_check_updates(self):
        """等待機器人準備完成後再啟動任務"""
        await self.bot.wait_until_ready()

async def setup(bot: commands.Bot):
    await bot.add_cog(HookNDHU(bot))