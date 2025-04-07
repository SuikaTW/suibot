import discord
from discord import app_commands
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="顯示機器人的所有功能")
    async def help(self, interaction: discord.Interaction):
        """顯示機器人的所有功能，使用下拉選單選擇特定部分"""
        view = HelpView(self.bot)
        await interaction.response.send_message("請選擇要查看的指令部分：", view=view, ephemeral=True)


class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=60)  # 設定互動超時時間為 60 秒
        self.bot = bot

        # 排除的 Cogs 名稱清單
        excluded_cogs = ["Admin", "Debug","HookNDHU"]  # 這裡填入您不想顯示的 Cogs 名稱

        # 建立下拉選單，過濾掉排除的 Cogs
        options = [
            discord.SelectOption(label=cog_name, description=f"查看 {cog_name} 的指令")
            for cog_name in bot.cogs.keys() if cog_name not in excluded_cogs
        ]
        self.add_item(HelpSelect(bot, options))


class HelpSelect(discord.ui.Select):
    def __init__(self, bot, options):
        super().__init__(placeholder="選擇指令類型", options=options)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        """處理下拉選單的選擇"""
        selected_cog = self.values[0]  # 獲取使用者選擇的 Cog 名稱
        cog = self.bot.cogs.get(selected_cog)

        if cog:
            commands_list = cog.get_app_commands()
            if commands_list:
                embed = discord.Embed(
                    title=f"📖 關於 {selected_cog} 指令列表",
                    description="以下是該部分的所有指令：",
                    color=discord.Color.green()
                )
                command_descriptions = "\n".join(
                    [f"/{cmd.name} - {cmd.description}" for cmd in commands_list]
                )
                embed.add_field(name="指令", value=command_descriptions, inline=False)
                embed.set_footer(text="使用 /help 指令查看此列表")
                await interaction.response.edit_message(content=None, embed=embed, view=None)
            else:
                await interaction.response.edit_message(content=f"**{selected_cog}** 沒有可用的指令。", view=None)
        else:
            await interaction.response.edit_message(content="選擇的部分不存在。", view=None)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))