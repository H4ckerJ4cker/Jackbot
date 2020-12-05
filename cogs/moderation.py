from discord.ext.commands import Cog, command, Context
from discord import utils, Embed, Colour, Member, PermissionOverwrite, Forbidden
from discord.ext import commands
import re


def perms(ctx, member):
    # Check if the user's 'best' role is higher than the member he is trying to mod.
    return ctx.author.top_role > member.top_role


class Moderation(Cog):
    """
    Moderation Commands and Events
    """

    def __init__(self, bot):
        self.bot = bot

    @command()
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, amount=6):
        """
        Deletes x amount of messages in a channel. (The default is 5.)
        """
        await ctx.channel.purge(limit=amount + 1)

    @command(aliases=['m'])
    @commands.check_any(commands.has_role('Among Us Overlord'), commands.has_permissions(manage_channels=True))
    async def mutevc(self, ctx):
        """
        Mutes everyone in the voice channel you are in. Useful for playing Among Us. (Requires Among Us Overlord role.)
        """
        await ctx.message.delete()
        vc = ctx.author.voice.channel
        for member in vc.members:
            await member.edit(mute=True)

    @command(aliases=['u'])
    @commands.check_any(commands.has_role('Among Us Overlord'), commands.has_permissions(manage_channels=True))
    async def unmutevc(self, ctx):
        """
        Unmutes everyone in the voice channel you are in. Useful for playing Among Us. (Requires Among Us Overlord 
        role.) 
        """
        await ctx.message.delete()
        vc = ctx.author.voice.channel
        for member in vc.members:
            await member.edit(mute=False)


def setup(bot):
    bot.add_cog(Moderation(bot))
