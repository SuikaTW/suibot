import discord
from discord import app_commands
from discord.ext import commands
import json
from pytube import YouTube
import os

from core.cogs import Cog_Extention

with open('setting.json', mode="r", encoding='utf8') as jfile:
    jdata = json.load(jfile)

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.playing_list = {}  # 使用字典來管理每個伺服器的播放清單

    def get_playing_list(self, guild_id):
        """取得伺服器的播放清單"""
        if guild_id not in self.playing_list:
            self.playing_list[guild_id] = []
        return self.playing_list[guild_id]

    @app_commands.command(name="join", description="join a voice channel")
    async def join(self, interaction: discord.Interaction):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("⚠ 你需要先加入語音頻道！", ephemeral=True)
            return
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message("✅ 已加入語音頻道。")

    @app_commands.command(name="music", description="play music")
    async def music(self, interaction: discord.Interaction, url: str):
        await interaction.response.send_message("✅ 已加入播放清單。", ephemeral=True)
        await interaction.channel.send(f"```已加入播放清單⬇```")
        await interaction.channel.send(url)
        await self.play(interaction, url)

    async def play(self, interaction: discord.Interaction, url: str = ""):
        playing_list = self.get_playing_list(interaction.guild.id)

        # 取得目前機器人狀態
        voice = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        # 如果機器人正在播放音樂, 將音樂放入播放清單
        if voice and voice.is_playing():
            playing_list.append(url)
            print(playing_list)
            await interaction.channel.send("🎵 已將歌曲加入播放清單。")
        else:
            # 如果還有找到之前已經被播放過的音樂檔, 進行刪除
            song_there = os.path.isfile("song.mp4")
            try:
                if song_there:
                    os.remove("song.mp4")
            except PermissionError:
                await interaction.channel.send("⚠ 請等待目前播放的音樂結束或使用 'stop' 指令。")
                return

            # 下載目標影片
            try:
                YouTube(url).streams.filter(only_audio=True).first().download()
            except Exception as e:
                await interaction.channel.send(f"❌ 無法下載音樂: {e}")
                return

            # 將目標影片改名, 方便找到它
            for file in os.listdir("./"):
                if file.endswith(".mp4"):
                    os.rename(file, "song.mp4")

            # 播放音樂並設定播放結束後的行為
            if not voice:
                channel = interaction.user.voice.channel
                voice = await channel.connect()

            try:
                voice.play(
                    discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source="song.mp4"),
                    after=lambda e: self.end_song("song.mp4", interaction.guild)
                )
                await interaction.channel.send("🎶 正在播放音樂。")
            except Exception as e:
                await interaction.channel.send(f"❌ 播放音樂時發生錯誤: {e}")

    def end_song(self, path, guild):
        playing_list = self.get_playing_list(guild.id)

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
                YouTube(url).streams.filter(only_audio=True).first().download()
                for file in os.listdir("./"):
                    if file.endswith(".mp4"):
                        os.rename(file, "song.mp4")

                voice.play(
                    discord.FFmpegPCMAudio(executable="ffmpeg/bin/ffmpeg.exe", source="song.mp4"),
                    after=lambda e: self.end_song("song.mp4", guild)
                )
            except Exception as e:
                print(f"❌ 播放下一首音樂時發生錯誤: {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(music(bot))