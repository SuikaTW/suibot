import discord
from discord import app_commands
from discord.ext import commands
import json
from discord.ext.commands.cog import Cog
from discord.ext.commands.core import command
from discord.utils import get

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="顯示機器人的所有功能")
    async def help(self, interaction: discord.Interaction):
        """顯示機器人的所有功能"""
        embed = discord.Embed(
            title="📖 機器人指令列表",
            description="以下是機器人目前支援的所有功能：",
            color=discord.Color.blue()
        )

        # 遍歷所有已載入的 Cogs
        for cog_name, cog in self.bot.cogs.items():
            commands_list = cog.get_app_commands()
            if commands_list:
                command_descriptions = "\n".join(
                    [f"/{cmd.name} - {cmd.description}" for cmd in commands_list]
                )
                embed.add_field(name=f"**{cog_name}**", value=command_descriptions, inline=False)

        embed.set_footer(text="使用 /help 指令查看此列表 2025.03.24")
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))