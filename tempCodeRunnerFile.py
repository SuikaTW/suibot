import discord
from discord import app_commands
from discord.ext import commands

bot = commands.Bot(command_prefix="*",intents= discord.Intents.all())