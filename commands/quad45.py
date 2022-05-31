import discord
from discord.ext import commands

@commands.command(name = "quad45", description = "Attempt a triple 45")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def quad45(ctx):

    await ctx.send(f"**{ctx.author}**, please resist the urge of self-harm.")

def setup(bot):
    bot.add_command(quad45)
