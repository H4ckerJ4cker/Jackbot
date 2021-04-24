from typing import Optional, Union

from discord import utils, Member, ChannelType, TextChannel, VoiceChannel, Embed, Colour
from discord.ext import commands
from discord.ext.commands import Cog, command


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
    @commands.has_permissions(manage_guild=True)
    async def purge(self, ctx, user: Optional[Member], amount: int):
        """
        Deletes x amount of messages in a channel. (The default is 5.) Specify a user to only delete messages from
        that user.
        """

        def user_check(message):
            return message.author == user

        if user is None:
            purged = await ctx.channel.purge(limit=amount + 1)
        else:
            await ctx.message.delete()
            purged = await ctx.channel.purge(limit=amount + 1, check=user_check)

        # logging
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

        if log_channel_id is not None:
            embed = Embed(
                color=Colour.orange(),
                title="Messages Purged",
                description=f"**{len(purged) - 1}** messages were purged."
            )
            embed.add_field(name="Channel", value=f"<#{ctx.channel.id}>")
            embed.add_field(name="Moderator", value=ctx.message.author.mention)
            log_channel = self.bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

    @command()
    @commands.has_permissions(manage_channels=True)
    async def slowmode(self, ctx, channel: Optional[TextChannel], delay: Union[int, str]):
        """
        Turn on slowmode for a channel. Pass in a number of seconds to set the slowmode or ``off`` to disable slowmode.
        """
        if type(delay) == str and delay != "off" or type(delay) == int and delay > 21600:
            await ctx.send("\N{NO ENTRY SIGN} Invalid slowmode setting!")
            return

        if channel is None:
            channel = ctx.channel
            await ctx.message.delete()
        else:
            await ctx.message.add_reaction("✅")

        if delay == 0 or delay == "off":
            delay = 0
            message = "Slowmode disabled"
        else:
            message = f"Slowmode set to {delay}s"

        await channel.edit(reason="Slowmode", slowmode_delay=delay)
        embed = Embed(
            color=Colour.green(),
            title=f":white_check_mark: {message}",
        )
        await channel.send(embed=embed)

        # logging
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

        if log_channel_id is not None:
            embed = Embed(
                color=Colour.orange(),
                title="Slowmode Edited",
            )
            embed.add_field(name="Channel", value=f"<#{channel.id}>")
            embed.add_field(name="Moderator", value=ctx.message.author.mention)
            embed.add_field(name="Delay", value=f"{delay}s")

            log_channel = self.bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

    @command(aliases=['m'])
    @commands.check_any(commands.has_role('Among Us Overlord'), commands.has_permissions(manage_channels=True))
    async def mutevc(self, ctx):
        """
        Mutes everyone in the voice channel you are in. Useful for playing Among Us. (Requires Among Us Overlord role.)
        """
        await ctx.message.delete()
        try:
            vc = ctx.author.voice.channel
        except AttributeError:
            ctx.channel.send("⚠️ You need to be in a voice channel to use that command!")
            return
        for member in vc.members:
            await member.edit(mute=True)

        # logging
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

        if log_channel_id is not None:
            embed = Embed(
                color=Colour.orange(),
                title="Voice Channel Muted",
                description="All the members in a voice channel were muted."
            )
            embed.add_field(name="Voice Channel", value=f"{vc.name}")
            embed.add_field(name="Moderator", value=ctx.message.author.mention)
            log_channel = self.bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

    @command(aliases=['u'])
    @commands.check_any(commands.has_role('Among Us Overlord'), commands.has_permissions(manage_channels=True))
    async def unmutevc(self, ctx):
        """
        Unmutes everyone in the voice channel you are in. Useful for playing Among Us. (Requires Among Us Overlord 
        role.) 
        """
        await ctx.message.delete()
        try:

            vc = ctx.author.voice.channel
        except AttributeError:
            ctx.channel.send("⚠️ You need to be in a voice channel to use that command!")
            return
        for member in vc.members:
            await member.edit(mute=False)

        # logging
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

        if log_channel_id is not None:
            embed = Embed(
                color=Colour.orange(),
                title="Voice Channel Unmuted",
                description="All the members in a voice channel were unmuted."
            )
            embed.add_field(name="Voice Channel", value=f"{vc.name}")
            embed.add_field(name="Moderator", value=ctx.message.author.mention)
            log_channel = self.bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

    @command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: Member, *, reason="No reason given"):
        """
        Kick a member from the server.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send(
                "You can't moderate a member with a higher or equal role to you! (If this seems wrong make sure the "
                "JackBot role is higher in the role list than the top role of the user you are trying to moderate.)")
            return
        await user.kick(reason=reason)
        await ctx.send(f"**{user.display_name}** was kicked for **{reason}**.")

        # logging
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

        if log_channel_id is not None:
            embed = Embed(
                color=Colour.orange(),
                title="User Kicked",
                description=f"A user was kicked from the server."
            )
            embed.add_field(name="Moderator", value=ctx.message.author.mention)
            embed.add_field(name="User", value=user.mention)
            embed.add_field(name="Reason", value=reason)
            log_channel = self.bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

    @command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: Member, *, reason="No reason given"):
        """
        Bans a member from the server.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send(
                "You can't moderate a member with a higher or equal role to you! (If this seems wrong make sure the "
                "JackBot role is higher in the role list than the top role of the user you are trying to moderate.)")
            return
        await user.ban(reason=reason)
        await ctx.send(f"**{user.display_name}** was banned for **{reason}**.")

        # logging
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

        if log_channel_id is not None:
            embed = Embed(
                color=Colour.orange(),
                title="User Baned",
                description=f"A user was banned from the server."
            )
            embed.add_field(name="Moderator", value=ctx.message.author.mention)
            embed.add_field(name="User", value=user.mention)
            embed.add_field(name="Reason", value=reason)
            log_channel = self.bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

    @command()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, full_username):
        """
        Unbans a member from the server. Full username with discriminator must be used.
        """
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = full_username.split('#')
        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"**{user.mention}** was unbanned.")
                # logging
                if ctx.guild.id not in self.bot.servers:
                    self.bot.servers[ctx.guild.id] = {}
                log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

                if log_channel_id is not None:
                    embed = Embed(
                        color=Colour.orange(),
                        title="User Unbanned",
                        description=f"A user was unbanned from the server."
                    )
                    embed.add_field(name="Moderator", value=ctx.message.author.mention)
                    embed.add_field(name="User", value=full_username)
                    log_channel = self.bot.get_channel(log_channel_id)
                    await log_channel.send(embed=embed)

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
            await ctx.send(
                "You can't moderate a member with a higher or equal role to you! (If this seems wrong make sure the "
                "JackBot role is higher in the role list than the top role of the user you are trying to moderate.)")
            return
        guild = ctx.guild
        muted_role = utils.get(guild.roles, name="Muted")
        if muted_role in user.roles:
            await ctx.send(f"**{user.display_name}** is already muted.")
            return
        if muted_role is None:
            muted_role = await guild.create_role(name="Muted")
        await user.add_roles(muted_role, reason=reason)
        await ctx.send(f"**{user.display_name}** was muted for **{reason}**.")
        for channel in guild.channels:
            if channel.type == ChannelType.text:
                await channel.set_permissions(muted_role, send_messages=False)
            if channel.type == ChannelType.voice:
                await channel.set_permissions(muted_role, speak=False)

        # logging
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

        if log_channel_id is not None:
            embed = Embed(
                color=Colour.orange(),
                title="User Muted",
                description=f"A user was muted."
            )
            embed.add_field(name="Moderator", value=ctx.message.author.mention)
            embed.add_field(name="User", value=user.mention)
            embed.add_field(name="Reason", value=reason)
            log_channel = self.bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

    @command()
    @commands.has_permissions(manage_guild=True)
    async def unmute(self, ctx, user: Member):
        """
        Unmutes a member. Does not affect users blocked from channels.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send(
                "You can't moderate a member with a higher or equal role to you! (If this seems wrong make sure the "
                "JackBot role is higher in the role list than the top role of the user you are trying to moderate.)")
            return
        muted_role = utils.get(user.roles, name="Muted")
        if muted_role is not None:
            await user.remove_roles(muted_role, reason="Unmuted")
            await ctx.send(f"**{user.display_name}** has been unmuted.")
            # logging
            if ctx.guild.id not in self.bot.servers:
                self.bot.servers[ctx.guild.id] = {}
            log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

            if log_channel_id is not None:
                embed = Embed(
                    color=Colour.orange(),
                    title="User Unmuted",
                    description=f"A user was unmuted."
                )
                embed.add_field(name="Moderator", value=ctx.message.author.mention)
                embed.add_field(name="User", value=user.mention)
                log_channel = self.bot.get_channel(log_channel_id)
                await log_channel.send(embed=embed)
        else:
            await ctx.send(f"**{user.display_name}** is not muted.")

    @command()
    @commands.has_permissions(manage_guild=True)
    async def block(self, ctx, user: Member, channel: Union[TextChannel, VoiceChannel] = None):
        """
        Block a member from speaking in a channel.
        If no channel is specified the user will be blocked in the channel the command was initiated in.
        """
        reason = "User blocked from channel"
        check = perms(ctx, user)
        if check is not True:
            await ctx.send(
                "You can't moderate a member with a higher or equal role to you! (If this seems wrong make sure the "
                "JackBot role is higher in the role list than the top role of the user you are trying to moderate.)")
            return
        if channel is None:
            channel = ctx.channel
        if channel.type == ChannelType.text:
            await channel.set_permissions(user, send_messages=False, reason=reason)
            await ctx.send(f"**{user.display_name}** can no longer send messages in the channel {channel.mention}.")
        elif channel.type == ChannelType.voice:
            await channel.set_permissions(user, speak=False, reason=reason)
            await ctx.send(
                f"**{user.display_name}** can no longer speak in the voice channel **{channel.name}**.")
        # logging
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

        if log_channel_id is not None:
            embed = Embed(
                color=Colour.orange(),
                title="User Blocked",
                description=f"A user was blocked from speaking in a channel."
            )
            embed.add_field(name="Channel", value=f"{channel.name}")
            embed.add_field(name="Moderator", value=ctx.message.author.mention)
            embed.add_field(name="User", value=user.mention)
            log_channel = self.bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)

    @command()
    @commands.has_permissions(manage_guild=True)
    async def unblock(self, ctx, user: Member, channel: Union[TextChannel, VoiceChannel] = None):
        """
        Unblock a user, allowing them to speak in a channel again. Does not affect muted users.
        """
        check = perms(ctx, user)
        if check is not True:
            await ctx.send(
                "You can't moderate a member with a higher or equal role to you! (If this seems wrong make sure the "
                "JackBot role is higher in the role list than the top role of the user you are trying to moderate.)")
            return
        if channel is None:
            channel = ctx.channel
        await channel.set_permissions(user, overwrite=None, reason="User unblocked from channel")
        if channel.type == ChannelType.text:
            await ctx.send(f"**{user.display_name}** can now send messages in the channel {channel.mention} again.")
        elif channel.type == ChannelType.voice:
            await ctx.send(f"**{user.display_name}** can now speak in the voice channel **{channel.name}** again.")

        # logging
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        log_channel_id = self.bot.servers[ctx.message.guild.id].get("logging_channel_id")

        if log_channel_id is not None:
            embed = Embed(
                color=Colour.orange(),
                title="User Unblocked",
                description=f"A user was unblocked from a channel."
            )
            embed.add_field(name="Channel", value=f"{channel.name}")
            embed.add_field(name="Moderator", value=ctx.message.author.mention)
            embed.add_field(name="User", value=user.mention)
            log_channel = self.bot.get_channel(log_channel_id)
            await log_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
