import discord
from discord import app_commands
from discord.ext import commands
import openai
import json
import os
import logging

# 從 token.json 中讀取 OpenAI API 金鑰
with open('token.json', mode="r", encoding='utf8') as jfile:
    jdata = json.load(jfile)

openai.api_key = jdata['openai_api_key']  # 設置 OpenAI API 金鑰

class OpenAIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conversations = {}  # 用於存儲每個伺服器的對話上下文

    def get_conversation(self, guild_id):
        """取得伺服器的對話上下文"""
        if guild_id not in self.conversations:
            # 初始化對話上下文
            self.conversations[guild_id] = [
                {"role": "system", "content": "你是一個友好的助手，請回答使用者的問題。"},
            ]
        return self.conversations[guild_id]

    @app_commands.command(name="ask", description="向 OpenAI 提問")
    async def ask(self, interaction: discord.Interaction, question: str):
        """處理 /ask 指令，向 OpenAI 提問"""
        await interaction.response.defer()  # 延遲回應，避免超時
        guild_id = interaction.guild.id
        conversation = self.get_conversation(guild_id)  # 獲取對話上下文

        # 將使用者的提問加入對話上下文
        conversation.append({"role": "user", "content": question})

        try:
            # 發送請求到 OpenAI API
            response = await openai.ChatCompletion.acreate(
                model="gpt-4o-mini",  # 或 "gpt-4"（如果您有權限）
                messages=conversation,
                max_tokens=500,  # 限制回應的最大字數
                temperature=0.7  # 控制生成文字的隨機性
            )

            # 獲取回應內容
            answer = response["choices"][0]["message"]["content"]

            # 將機器人的回應加入對話上下文
            conversation.append({"role": "assistant", "content": answer})

            # 將問題和回答一併發送到聊天室
            await interaction.followup.send(f"**你問了：** {question}\n\n🤖 **OpenAI 回應：**\n{answer}")

        except Exception as e:
            await interaction.followup.send("❌ 無法處理您的請求，請稍後再試！")
            print(f"發生錯誤：{e}")

    @app_commands.command(name="aireset", description="重置對話記憶")
    async def aireset(self, interaction: discord.Interaction):
        """處理 /aireset 指令，重置對話記憶"""
        guild_id = interaction.guild.id
        if guild_id in self.conversations:
            del self.conversations[guild_id]  # 刪除伺服器的對話上下文
        await interaction.response.send_message("✅ 對話記憶已重置！")

async def setup(bot: commands.Bot):
    await bot.add_cog(OpenAIChat(bot))