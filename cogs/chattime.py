import discord
from discord import app_commands
from discord.ext import commands
import json
from datetime import datetime
from bot import CHATTIME_FILE

with open(CHATTIME_FILE, mode="r", encoding="utf8") as file:
    chattime_data = json.load(file)

class ChatTime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chattime_file = "data/chattime.json"
        self.server_settings_file = "data/server_chat_setting.json"
        self.chattime_data = self.load_chattime_data()
        self.server_settings = self.load_server_settings()

    class ChatTimeView(discord.ui.View):
        def __init__(self, chattime_data):
            super().__init__()
            self.chattime_data = chattime_data

        @discord.ui.button(label="查看自己的語音時長", style=discord.ButtonStyle.primary, custom_id="view_own_time")
        async def view_own_time(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            user_id = str(button_interaction.user.id)
            if user_id in self.chattime_data:
                total_time = self.chattime_data[user_id].get("total_time", 0)
                hours, remainder = divmod(total_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                await button_interaction.response.send_message(
                    f"🕒 你在語音頻道的總時長為：{int(hours)} 小時 {int(minutes)} 分鐘 {int(seconds)} 秒",
                    ephemeral=True
                )
            else:
                await button_interaction.response.send_message("⚠ 你還沒有任何語音時長記錄！", ephemeral=True)

        @discord.ui.button(label="排行榜", style=discord.ButtonStyle.success, custom_id="view_leaderboard")
        async def view_leaderboard(self, button_interaction: discord.Interaction, button: discord.ui.Button):
            sorted_scores = sorted(self.chattime_data.items(), key=lambda x: x[1].get("total_time", 0), reverse=True)
            embed = discord.Embed(title="語音時長排行榜", color=discord.Color.blue())
            for i, (user_id, data) in enumerate(sorted_scores[:10], start=1):
                user = button_interaction.guild.get_member(int(user_id))
                username = user.name if user else "未知使用者"
                total_time = data.get("total_time", 0)
                hours, remainder = divmod(total_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                embed.add_field(
                    name=f"{i}. {username}",
                    value=f"🕒 {int(hours)} 小時 {int(minutes)} 分鐘 {int(seconds)} 秒",
                    inline=False
                )
            embed.set_footer(text=f"更新時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await button_interaction.response.send_message(embed=embed)

    def load_chattime_data(self):
        """載入 chattime.json 的數據"""
        try:
            with open(self.chattime_file, mode="r", encoding="utf8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_chattime_data(self):
        """保存數據到 chattime.json"""
        with open(self.chattime_file, mode="w", encoding="utf8") as file:
            json.dump(self.chattime_data, file, indent=4, ensure_ascii=False)

    def load_server_settings(self):
        """載入 server_chat_setting.json 的數據"""
        try:
            with open(self.server_settings_file, mode="r", encoding="utf8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_server_settings(self):
        """保存數據到 server_chat_setting.json"""
        with open(self.server_settings_file, mode="w", encoding="utf8") as file:
            json.dump(self.server_settings, file, indent=4, ensure_ascii=False)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """監聽使用者進入或離開語音頻道的事件"""
        # 忽略機器人本身的語音紀錄
        if member.bot:
            return

        user_id = str(member.id)
        guild_id = str(member.guild.id)

        # 使用者進入語音頻道
        if before.channel is None and after.channel is not None:
            self.chattime_data[user_id] = {
                "join_time": datetime.now().isoformat(),
                "total_time": self.chattime_data.get(user_id, {}).get("total_time", 0)
            }
            self.save_chattime_data()
            print(f"{member.name} 加入了語音頻道 {after.channel.name}")

            # 發送訊息到指定頻道
            if guild_id in self.server_settings and "log_channel" in self.server_settings[guild_id]:
                log_channel_id = self.server_settings[guild_id]["log_channel"]
                log_channel = member.guild.get_channel(log_channel_id)
                if log_channel:
                    await log_channel.send(f"✅ {member.display_name} 加入了語音頻道 **{after.channel.name}**")

        # 使用者離開語音頻道
        elif before.channel is not None and after.channel is None:
            if user_id in self.chattime_data and "join_time" in self.chattime_data[user_id]:
                join_time = datetime.fromisoformat(self.chattime_data[user_id]["join_time"])
                duration = (datetime.now() - join_time).total_seconds()
                self.chattime_data[user_id]["total_time"] += duration
                del self.chattime_data[user_id]["join_time"]
                self.save_chattime_data()
                print(f"{member.name} 離開了語音頻道，總時長更新為 {self.chattime_data[user_id]['total_time']} 秒")

                # 發送訊息到指定頻道
                if guild_id in self.server_settings and "log_channel" in self.server_settings[guild_id]:
                    log_channel_id = self.server_settings[guild_id]["log_channel"]
                    log_channel = member.guild.get_channel(log_channel_id)
                    if log_channel:
                        await log_channel.send(f"❌ {member.display_name} 離開了語音頻道 **{before.channel.name}**")

    @app_commands.command(name="chattime", description="顯示語音時長選單")
    async def chattime(self, interaction: discord.Interaction):
        """顯示語音時長選單，包含按鈕"""
        view = ChatTime.ChatTimeView(self.chattime_data)
        await interaction.response.send_message("請選擇一個選項：", view=view, ephemeral=True)

    @app_commands.command(name="set_channel", description="設定語音更新資訊的頻道")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """設定用於接收語音更新資訊的頻道"""
        guild_id = str(interaction.guild.id)
        self.server_settings[guild_id] = {"log_channel": channel.id}
        self.save_server_settings()
        await interaction.response.send_message(f"✅ 已設定語音更新資訊頻道為：{channel.mention}")

    @set_channel.error
    async def set_channel_error(self, interaction: discord.Interaction, error):
        """處理 set_channel 指令的錯誤"""
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("⚠ 你需要管理員權限才能使用此指令！", ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        """在機器人啟動時同步斜線指令"""
        await self.bot.tree.sync()
        print("斜線指令已同步")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """處理互動事件"""
        # 僅處理按鈕或選單互動
        if interaction.type == discord.InteractionType.component and "custom_id" in interaction.data:
            custom_id = interaction.data["custom_id"]
            # 處理按鈕或選單互動
            print(f"處理互動，custom_id: {custom_id}")
        elif interaction.type == discord.InteractionType.application_command:
            # 忽略斜線指令的互動
            return
        else:
            # 忽略其他類型的互動
            print("⚠ 無法處理此互動，缺少 custom_id！")

async def setup(bot: commands.Bot):
    await bot.add_cog(ChatTime(bot))