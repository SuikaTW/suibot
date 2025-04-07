import discord
from discord import app_commands
from discord.ext import commands
import json
import yt_dlp  # 替代 pytube 的下載工具
import os


from core.cogs import Cog_Extention

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        self.playing_list = {}  # 使用字典來管理每個伺服器的播放清單

    def get_playing_list(self, guild_id):
        """取得伺服器的播放清單"""
        if guild_id not in self.playing_list:
            self.playing_list[guild_id] = []
        return self.playing_list[guild_id]

    @app_commands.command(name="join", description="讓機器人加入語音頻道")
    async def join(self, interaction: discord.Interaction):
        print("join 指令被觸發")  # 除錯訊息
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("⚠ 你需要先加入語音頻道！", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f"✅ 已加入語音頻道：{channel.name}")

    @app_commands.command(name="leave", description="讓機器人離開語音頻道")
    async def leave(self, interaction: discord.Interaction):
        voice = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if not voice or not voice.is_connected():
            await interaction.response.send_message("⚠ 機器人目前不在任何語音頻道中！", ephemeral=True)
            return

        await voice.disconnect()
        await interaction.response.send_message("✅ 已離開語音頻道。")

    @app_commands.command(name="play", description="播放音樂（支持 URL 或關鍵字搜尋）")
    async def play(self, interaction: discord.Interaction, *, query: str):
        """播放音樂，支持 URL 或關鍵字搜尋"""
        await interaction.response.defer()  # 延遲回應，避免超時
        guild_id = interaction.guild.id
        playing_list = self.get_playing_list(guild_id)

        # 檢查是否是 URL
        if query.startswith("http://") or query.startswith("https://"):
            url = query
            print(f"🔗 輸入的是 URL：{url}")  # 除錯訊息
        else:
            print(f"🔍 正在搜尋關鍵字：{query}")  # 除錯訊息
            url = self.search_youtube(query)
            if not url:
                await interaction.channel.send("❌ 無法找到相關音樂，請嘗試其他關鍵字！")
                return
            print(f"✅ 搜尋到的 URL：{url}")  # 除錯訊息

        # 如果機器人正在播放音樂，將音樂加入播放清單
        voice = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        if voice and voice.is_playing():
            playing_list.append(url)
            await interaction.channel.send(f"🎵 已將歌曲加入播放清單：{url}")
            return

        # 播放音樂
        await self.start_playing(interaction, url)

    def search_youtube(self, query: str) -> str:
        """使用 yt-dlp 搜尋 YouTube 並返回第一個結果的完整 URL"""
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": False,  # 設為 False 以顯示更多日誌
            "noplaylist": True,
            "default_search": "ytsearch",  # 使用 YouTube 搜尋
            "extract_flat": True,  # 只提取搜尋結果的 URL
        }
        search_query = f"ytsearch:{query}"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # 使用 yt-dlp 搜尋關鍵字
                print(f"🔍 正在搜尋關鍵字：{query}")  # 除錯訊息
                info= ydl.extract_info(search_query, download=False)
                print(f"🔍 搜尋結果資訊：{info}")  # 打印完整的搜尋結果
                if "entries" in info and len(info["entries"]) > 0:
                    first_result = info["entries"][0]
                    print(f"✅ 搜尋成功，第一個結果：{first_result}")  # 除錯訊息

                    # 檢查並補全 URL
                    url = first_result.get("url")
                    if not url.startswith("http"):
                        url = f"https://www.youtube.com{url}"  # 補全為完整的 YouTube URL
                    return url
                else:
                    print("❌ 未找到任何搜尋結果")
            except Exception as e:
                print(f"❌ 搜尋失敗：{e}")
        return None

    async def start_playing(self, interaction: discord.Interaction, url: str):
        """開始播放音樂"""
        guild_id = interaction.guild.id
        voice = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        # 刪除舊的音樂檔案
        if os.path.isfile(f"song_{guild_id}.mp4"):
            os.remove(f"song_{guild_id}.mp4")

        # 嘗試下載音樂
        try:
            await interaction.channel.send("🎵 正在下載音樂，請稍候...")
            self.download_audio(url, guild_id)
        except Exception as e:
            await interaction.channel.send(f"❌ 無法下載音樂：{e}")
            return

        # 播放音樂
        if not voice:
            channel = interaction.user.voice.channel
            voice = await channel.connect()

        print(f"🔗 最終播放的 URL：{url}")  # 在播放前打印最終的 URL
        try:
            voice.play(
                discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(
                        executable="C:/ffmpeg/bin/ffmpeg.exe",  # 使用正確的 ffmpeg 路徑
                        source=f"song_{guild_id}.mp4"
                    ),
                    volume=0.5  # 設置初始音量為 50%
                ),
                after=lambda e: self.end_song(f"song_{guild_id}.mp4", interaction.guild)
            )
            await interaction.channel.send("🎶 正在播放音樂。")
        except Exception as e:
            await interaction.channel.send(f"❌ 播放音樂時發生錯誤：{e}")

    def download_audio(self, url, guild_id):
        """下載音樂"""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'song_{guild_id}.mp4',
                'quiet': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            raise Exception(f"下載失敗: {e}")

    def end_song(self, path, guild):
        guild_id = guild.id
        playing_list = self.get_playing_list(guild_id)

        # 播放完後刪除檔案
        if os.path.isfile(path):
            os.remove(path)

        # 播放下一首音樂
        if playing_list:
            url = playing_list.pop(0)
            voice = discord.utils.get(self.bot.voice_clients, guild=guild)

            if not voice:
                return  # 如果機器人已離開語音頻道，則不繼續播放

            try:
                self.download_audio(url, guild_id)
                voice.play(
                    discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=f"song_{guild_id}.mp4"),
                    after=lambda e: self.end_song(f"song_{guild_id}.mp4", guild)
                )
            except Exception as e:
                print(f"❌ 播放下一首音樂時發生錯誤：{e}")

    @app_commands.command(name="playlist", description="顯示目前的播放清單")
    async def playlist(self, interaction: discord.Interaction):
        playing_list = self.get_playing_list(interaction.guild.id)
        if not playing_list:
            await interaction.response.send_message("🎵 播放清單目前是空的！", ephemeral=True)
            return

        playlist_str = "\n".join([f"{i + 1}. {url}" for i, url in enumerate(playing_list)])
        await interaction.response.send_message(f"🎶 播放清單：\n{playlist_str}")

    @app_commands.command(name="manage_playlist", description="管理播放清單")
    async def manage_playlist(self, interaction: discord.Interaction):
        view = PlaylistView(self, interaction.guild.id)
        await interaction.response.send_message("🎶 使用以下按鈕來管理播放清單：", view=view)


from discord.ui import View, Button

class PlaylistView(View):
    def __init__(self, cog, guild_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id

    @discord.ui.button(label="上移", style=discord.ButtonStyle.primary)
    async def move_up(self, interaction: discord.Interaction, button: Button):
        playing_list = self.cog.get_playing_list(self.guild_id)
        if len(playing_list) < 2:
            await interaction.response.send_message("⚠ 播放清單中沒有足夠的歌曲來更改順序！", ephemeral=True)
            return

        song = playing_list.pop(0)
        playing_list.append(song)
        await interaction.response.send_message("✅ 已將第一首歌曲移到最後！")

    @discord.ui.button(label="下移", style=discord.ButtonStyle.primary)
    async def move_down(self, interaction: discord.Interaction, button: Button):
        playing_list = self.cog.get_playing_list(self.guild_id)
        if len(playing_list) < 2:
            await interaction.response.send_message("⚠ 播放清單中沒有足夠的歌曲來更改順序！", ephemeral=True)
            return

        song = playing_list.pop(-1)
        playing_list.insert(0, song)
        await interaction.response.send_message("✅ 已將最後一首歌曲移到最前！")

    @discord.ui.button(label="顯示清單", style=discord.ButtonStyle.secondary)
    async def show_playlist(self, interaction: discord.Interaction, button: Button):
        playing_list = self.cog.get_playing_list(self.guild_id)
        if not playing_list:
            await interaction.response.send_message("🎵 播放清單目前是空的！", ephemeral=True)
            return

        playlist_str = "\n".join([f"{i + 1}. {url}" for i, url in enumerate(playing_list)])
        await interaction.response.send_message(f"🎶 播放清單：\n{playlist_str}")

    @discord.ui.button(label="清除清單", style=discord.ButtonStyle.danger)
    async def clear_playlist(self, interaction: discord.Interaction, button: Button):
        playing_list = self.cog.get_playing_list(self.guild_id)
        playing_list.clear()
        await interaction.response.send_message("✅ 播放清單已清空！")

    @discord.ui.button(label="跳過", style=discord.ButtonStyle.primary)
    async def skip(self, interaction: discord.Interaction, button: Button):
        voice = discord.utils.get(self.cog.bot.voice_clients, guild=interaction.guild)
        if not voice or not voice.is_playing():
            await interaction.response.send_message("⚠ 目前沒有正在播放的音樂！", ephemeral=True)
            return

        voice.stop()
        await interaction.response.send_message("✅ 已跳過當前音樂！")

    @discord.ui.button(label="暫停/繼續", style=discord.ButtonStyle.primary)
    async def pause_resume(self, interaction: discord.Interaction, button: Button):
        voice = discord.utils.get(self.cog.bot.voice_clients, guild=interaction.guild)
        if not voice or not voice.is_connected():
            await interaction.response.send_message("⚠ 機器人目前不在語音頻道中！", ephemeral=True)
            return

        # 如果音樂已暫停，恢復播放
        if voice.is_paused():
            try:
                voice.resume()
                await interaction.response.send_message("▶ 音樂已繼續播放！")
            except Exception as e:
                await interaction.response.send_message(f"❌ 無法繼續播放音樂: {e}", ephemeral=True)
            return

        # 如果音樂正在播放，暫停播放
        if voice.is_playing():
            try:
                voice.pause()
                await interaction.response.send_message("⏸ 音樂已暫停！")
            except Exception as e:
                await interaction.response.send_message(f"❌ 無法暫停音樂: {e}", ephemeral=True)
            return

        # 如果既沒有播放也沒有暫停，表示沒有音樂在播放
        await interaction.response.send_message("⚠ 目前沒有正在播放的音樂！", ephemeral=True)

    @discord.ui.button(label="音量+", style=discord.ButtonStyle.success)
    async def volume_up(self, interaction: discord.Interaction, button: Button):
        voice = discord.utils.get(self.cog.bot.voice_clients, guild=interaction.guild)
        if not voice or not isinstance(voice.source, discord.PCMVolumeTransformer):
            await interaction.response.send_message("⚠ 目前沒有正在播放的音樂或音量不可調整！", ephemeral=True)
            return

        voice.source.volume = min(voice.source.volume + 0.1, 1.0)
        await interaction.response.send_message(f"🔊 音量已增加到 {voice.source.volume:.1f}！")

    @discord.ui.button(label="音量-", style=discord.ButtonStyle.danger)
    async def volume_down(self, interaction: discord.Interaction, button: Button):
        voice = discord.utils.get(self.cog.bot.voice_clients, guild=interaction.guild)
        if not voice or not isinstance(voice.source, discord.PCMVolumeTransformer):
            await interaction.response.send_message("⚠ 目前沒有正在播放的音樂或音量不可調整！", ephemeral=True)
            return

        voice.source.volume = max(voice.source.volume - 0.1, 0.0)
        await interaction.response.send_message(f"🔉 音量已減少到 {voice.source.volume:.1f}！")

async def setup(bot: commands.Bot):
    await bot.add_cog(music(bot))