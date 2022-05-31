import discord
from discord.ext import commands

@commands.command(name = "info", aliases = ["information"], description = "Information about the bot")
@commands.bot_has_permissions(send_messages=True)
@commands.guild_only()
@commands.cooldown(1, 5, commands.BucketType.user)
async def info(ctx):

    em = discord.Embed(title = "Bot Information", description = "This is a bot created by Morpheye#9690, as a discord game meant to simulate 45 strafing in Minecraft Parkour. Hosted by bear_#8151", color = ctx.author.color)

    em.add_field(name = "Development Assistance", value = "bear_#8151 \ndude_guy_boy#3136")
    em.add_field(name = "Physics Help", value = "mine_pvpkill#8588 \nlavalaph#7013 \nBenjamaster7#9895 \nSrock#4106")
    em.add_field(name = "Beta Testing", value = "naryka#0001 \nalexhuhu#6502 \nAlphaEclipse#2220 \nbtf#1111 \nFirePK#8557 \nVince#5774 \nYes24#2424")

    await ctx.send(embed = em)


def setup(bot):
    bot.add_command(info)
