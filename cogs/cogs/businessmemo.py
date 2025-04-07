import discord
from discord.ext import commands
import json
import asyncio
from discord import app_commands
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
from core.cogs import Cog_Extention
# 儲存帳本資料的字典
user_ledger = {}

class BusinessMemo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """處理按鈕互動"""
        user_id = str(interaction.user.id)  # 使用者 ID 作為帳本的 key

        # 確保帳本初始化
        if user_id not in user_ledger:
            user_ledger[user_id] = []

        if interaction.type == discord.InteractionType.component and "custom_id" in interaction.data:
            if interaction.data["custom_id"] == "add_income":
                # 顯示 Modal 讓使用者新增入帳
                modal = AddEntryModal(user_id, "income")
                await interaction.response.send_modal(modal)

            elif interaction.data["custom_id"] == "add_expense":
                # 顯示 Modal 讓使用者新增出帳
                modal = AddEntryModal(user_id, "expense")
                await interaction.response.send_modal(modal)

            elif interaction.data["custom_id"] == "view_ledger":
                # 查看帳本
                ledger = user_ledger[user_id]
                if not ledger:
                    await interaction.response.send_message("📒 你的帳本目前是空的！", ephemeral=True)
                else:
                    ledger_str = "\n".join([
                        f"{i + 1}. {entry['item']} - ${entry['amount']} ({'入帳' if entry['type'] == 'income' else '出帳'})"
                        for i, entry in enumerate(ledger)
                    ])
                    await interaction.response.send_message(f"📒 你的帳本內容：\n{ledger_str}", ephemeral=True)

            elif interaction.data["custom_id"] == "clear_ledger":
                # 清除帳本
                user_ledger[user_id].clear()
                await interaction.response.send_message("🗑 已清空你的帳本！", ephemeral=True)

            elif interaction.data["custom_id"] == "checkout":
                # 結算帳本
                ledger = user_ledger[user_id]
                if not ledger:
                    await interaction.response.send_message("📒 你的帳本目前是空的！", ephemeral=True)
                else:
                    total_income = sum(entry['amount'] for entry in ledger if entry['type'] == 'income')
                    total_expense = sum(entry['amount'] for entry in ledger if entry['type'] == 'expense')
                    balance = total_income - total_expense
                    await interaction.response.send_message(
                        f"📊 結算結果：\n總入帳：${total_income}\n總出帳：${total_expense}\n餘額：${balance}",
                        ephemeral=True
                    )

    @app_commands.command(name="memo", description="管理你的帳本")
    async def memo(self, interaction: discord.Interaction):
        """顯示記帳功能的按鈕"""
        view = discord.ui.View()

        # 新增入帳按鈕
        add_income_button = discord.ui.Button(
            custom_id="add_income",
            label="新增入帳",
            style=discord.ButtonStyle.green
        )
        view.add_item(add_income_button)

        # 新增出帳按鈕
        add_expense_button = discord.ui.Button(
            custom_id="add_expense",
            label="新增出帳",
            style=discord.ButtonStyle.red
        )
        view.add_item(add_expense_button)

        # 查看帳本按鈕
        view_button = discord.ui.Button(
            custom_id="view_ledger",
            label="查看帳本",
            style=discord.ButtonStyle.blurple
        )
        view.add_item(view_button)

        # 清除帳本按鈕
        clear_button = discord.ui.Button(
            custom_id="clear_ledger",
            label="清空帳本",
            style=discord.ButtonStyle.gray
        )
        view.add_item(clear_button)

        # 結算按鈕
        checkout_button = discord.ui.Button(
            custom_id="checkout",
            label="結算",
            style=discord.ButtonStyle.green
        )
        view.add_item(checkout_button)

        await interaction.response.send_message("📒 使用以下按鈕來管理你的帳本：", view=view, ephemeral=True)

class AddEntryModal(discord.ui.Modal, title="新增記錄"):
    def __init__(self, user_id, entry_type):
        super().__init__(timeout=30)  # 設定超時時間為 30 秒
        self.user_id = user_id
        self.entry_type = entry_type
        self.interaction = None  # 初始化 interaction 屬性

        # 帳目名稱輸入框
        self.item_input = discord.ui.TextInput(
            label="帳目名稱",
            placeholder="例如：午餐、交通費",
            required=True,
            max_length=100
        )
        self.add_item(self.item_input)

        # 金額輸入框
        self.amount_input = discord.ui.TextInput(
            label="金額",
            placeholder="例如：100",
            required=True,
            max_length=10
        )
        self.add_item(self.amount_input)

    async def on_submit(self, interaction: discord.Interaction):
        """處理 Modal 提交"""
        self.interaction = interaction  # 保存 interaction 物件
        try:
            amount = float(self.amount_input.value)  # 確保金額是數字
        except ValueError:
            await interaction.response.send_message("⚠ 金額必須是數字！", ephemeral=True)
            return

        # 新增記錄到帳本
        user_ledger[self.user_id].append({
            "item": self.item_input.value,
            "amount": amount,
            "type": self.entry_type
        })
        entry_type_str = "入帳" if self.entry_type == "income" else "出帳"
        await interaction.response.send_message(
            f"✅ 已新增記錄：{self.item_input.value} - ${amount} ({entry_type_str})",
            ephemeral=True
        )

    async def on_timeout(self):
        """處理超時"""
        if self.interaction:  # 確保 interaction 已保存
            await self.interaction.followup.send(
                content="⚠ 由於超時，表單已自動關閉！請重新嘗試。",
                ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(BusinessMemo(bot))