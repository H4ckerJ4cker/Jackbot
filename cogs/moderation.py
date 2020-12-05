from discord.ext.commands import Cog, command, UserConverter
from discord import utils, Embed, Colour, Member, PermissionOverwrite, Forbidden, ChannelType, TextChannel, VoiceChannel
from discord.ext import commands
import re
from typing import Union


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
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: Member, *, reason="No reason given"):
        """
        Kick a member from the server.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send("You can't moderate a member with a higher or equal role than you!")
            return
        await user.kick(reason=reason)
        await ctx.send(f"**{user.display_name}** was kicked for **{reason}**.")

    @command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: Member, *, reason="No reason given"):
        """
        Bans a member from the server.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send("You can't moderate a member with a higher or equal role than you!")
            return
        await user.ban(reason=reason)
        await ctx.send(f"**{user.display_name}** was banned for **{reason}**.")

    @command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, full_username, *, reason="No reason given"):
        """
        Unbans a member from the server. Full username with discriminator must be used.
        """
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = full_username.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"**{user.mention}** was unbanned for **{reason}**.")
                is_banned = True
            else:
                is_banned = False

        if not is_banned:
            await ctx.send(f"**{full_username}** is not banned.")

    @command()
    @commands.has_permissions(manage_guild=True)
    async def mute(self, ctx, user: Member, *, reason="No reason given"):
        """
        Mutes a member.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send("You can't moderate a member with a higher or equal role than you!")
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
        await ctx.send(f"**{user.display_name}** was muted for **{reason}**.")

    @command()
    @commands.has_permissions(manage_guild=True)
    async def unmute(self, ctx, user: Member):
        """
        Unmutes a member. Does not affect users blocked from channels.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send("You can't moderate a member with a higher or equal role than you!")
            return
        muted_role = utils.get(user.roles, name="Muted")
        if muted_role is not None:
            await user.remove_roles(muted_role, reason="Unmuted")
            await ctx.send(f"**{user.display_name}** has been unmuted.")
        else:
            await ctx.send(f"**{user.display_name}** is not muted.")

    @command()
    @commands.has_permissions(manage_guild=True)
    async def block(self, ctx, user: Member, channel: Union[TextChannel, VoiceChannel] = None, *,
                    reason="No reason given"):
        """
        Block a member from speaking in a channel.
        If no channel is specified the user will be blocked in the channel the command was initiated in.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send("You can't moderate a member with a higher or equal role than you!")
            return
        if channel is None:
            channel = ctx.channel
        if channel.type == ChannelType.text:
            await channel.set_permissions(user, send_messages=False, reason=reason)
            await ctx.send(f"**{user.display_name}** can no longer send messages in the channel {channel.mention}. "
                           f"Reason: **{reason}**")
        elif channel.type == ChannelType.voice:
            await channel.set_permissions(user, speak=False, reason=reason)
            await ctx.send(
                f"**{user.display_name}** can no longer speak in the voice channel **{channel.name}**. Reason"
                f": **{reason}**")

    @command()
    @commands.has_permissions(manage_guild=True)
    async def unblock(self, ctx, user: Member, channel: Union[TextChannel, VoiceChannel] = None, *, reason="No reason "
                                                                                                           "given"):
        """
        Unblock a user, allowing them to speak in a channel again. Does not affect muted users.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send("You can't moderate a member with a higher or equal role than you!")
            return
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(user, overwrite=None, reason=reason)
        if channel.type == ChannelType.text:
            await ctx.send(f"**{user.display_name}** can now send messages in the channel {channel.mention} again. "
                           f"Reason: **{reason}**")
        elif channel.type == ChannelType.voice:
            await ctx.send(f"**{user.display_name}** can now speak in the voice channel **{channel.name}** again. "
                           f"Reason: **{reason}**")


def setup(bot):
    bot.add_cog(Moderation(bot))
