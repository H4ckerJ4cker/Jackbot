from discord.ext.commands import Cog, command, Context
from discord import utils, Embed, Colour, Member, PermissionOverwrite, Forbidden
from discord.ext import commands
import re


def check(ctx, member):
    # Check if the user's 'best' role is higher than the member he is trying to ban
    return ctx.author.top_role > member.top_role


async def mute(ctx, user, reason):
    role = utils.get(ctx.guild.roles, name="Muted")
    if not role:  # checks if there is muted role
        try:
            muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
            for channel in ctx.guild.channels:
                await channel.set_permissions(muted, send_messages=False)
        except Forbidden:
            return await ctx.send("I have no permissions to make a muted role")
        await user.add_roles(muted)
        await ctx.send(f"{user.mention} has been sent to hell for {reason}")
    else:
        await user.add_roles(role)
        await ctx.send(f"{user.mention} has been sent to hell for {reason}")


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
