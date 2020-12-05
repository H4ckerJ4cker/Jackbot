from discord.ext.commands import Cog, command, Context
from discord import utils, Embed, Colour, Member, PermissionOverwrite, Forbidden, ChannelType
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

    @command()
    @commands.has_permissions(manage_guild=True)
    async def mute(self, ctx, user: Member, *, reason="No reason given"):
        """
        Mutes a member.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send("You can't moderate a member with a higher role than you!")
            return
        guild = ctx.guild
        muted_role = utils.get(guild.roles, name="Muted")
        if muted_role in user.roles:
            await ctx.send(f"**{user.display_name}** is already muted.")
            return
        if muted_role is None:
            muted_role = await guild.create_role(name="Muted")
        for channel in guild.channels:
            if channel.type == ChannelType.text:
                await channel.set_permissions(muted_role, send_messages=False)
            if channel.type == ChannelType.voice:
                await channel.set_permissions(muted_role, speak=False)
        await user.add_roles(muted_role, reason=reason)
        await ctx.send(f"**{user.display_name}** was muted for **{reason}**")

    @command()
    @commands.has_permissions(manage_guild=True)
    async def unmute(self, ctx, user: Member):
        """
        Unmutes a member.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send("You can't moderate a member with a higher role than you!")
            return
        muted_role = utils.get(user.roles, name="Muted")
        if muted_role is not None:
            await user.remove_roles(muted_role, reason="Unmuted")
            await ctx.send(f"**{user.display_name}** was unmuted.")
        else:
            await ctx.send(f"**{user.display_name}** is not muted.")


def setup(bot):
    bot.add_cog(Moderation(bot))
