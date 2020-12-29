from discord.ext.commands import Cog, command
from discord.ext import commands
from discord import utils, TextChannel, Embed, Colour
import typing


class Settings(Cog):
    """
    Customize the bot for your server.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def settings(self, ctx):
        """
        Sends the list of available settings.
        """
        embed = Embed(
            color=Colour.blue(),
            title="Settings",
        )

        embed.set_footer(icon_url=self.bot.user.avatar_url, text="Type @JackBot help settings [setting name] "
                                                                 "for more info on a setting.")

        for command in self.bot.commands:
            if isinstance(command, commands.Group):
                for subcommand in command.commands:
                    embed.add_field(name=f"``!settings {subcommand.name}``", value=subcommand.help, inline=True)

        await ctx.send(embed=embed)

    @settings.command(aliases=['prefix', 'newprefix'])
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, *, new_prefix=None):
        """
        Set the prefix of the bot.
        """
        if ctx.guild is not None:
            if new_prefix is None:
                if ctx.guild.id not in self.bot.servers:
                    self.bot.servers[ctx.guild.id] = {}
                dbprefix = self.bot.servers[ctx.guild.id].get("prefix")
                if dbprefix is None:
                    prefix = '!'
                else:
                    prefix = dbprefix

                await ctx.send(f"The current prefix is **{prefix}**. To change it type ``@JackBot settings setprefix "
                               f"[new prefix]``")
            else:
                await self.bot.db.execute(
                    "INSERT INTO guilds(guild_id, prefix) VALUES($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
                    ctx.guild.id,
                    new_prefix,
                )
                if ctx.guild.id not in self.bot.servers:
                    self.bot.servers[ctx.guild.id] = {}
                self.bot.servers[ctx.guild.id]["prefix"] = new_prefix
                await ctx.send(f"Prefix set to **{new_prefix}**.")
        else:
            await ctx.send("\N{NO ENTRY SIGN} That command is only available in servers.")

    @settings.command(aliases=['autorole', 'joinrole'])
    @commands.has_permissions(manage_guild=True)
    async def setautorole(self, ctx, *, role_name=None):
        """
        Set the role members will get when they join the server. To turn off autorole type ``!settings autorole reset``
        """
        if ctx.guild is not None:
            if role_name == "reset":
                await self.bot.db.execute(
                    "UPDATE guilds SET join_role_id = null WHERE guild_id = $1;",
                    ctx.guild.id
                )
                self.bot.servers[ctx.guild.id]["join_role_id"] = None
                await ctx.send("Auto role disabled. To enable, run the command again with a role value.")
                return
            elif role_name is None:
                if ctx.guild.id not in self.bot.servers:
                    self.bot.servers[ctx.guild.id] = {}
                join_role = self.bot.servers[ctx.guild.id].get("join_role_id")
                if join_role is None:
                    await ctx.send(f"No autorole configured to add one type. ``@JackBot settings setautorole ["
                                   f"role_name]``")
                    return
                role = ctx.guild.get_role(join_role)
                await ctx.send(f"The current autorole for new members is **{role.name}**")
                return

            role = utils.get(ctx.guild.roles, name=role_name)
            if role is not None:
                await self.bot.db.execute(
                    "INSERT INTO guilds(guild_id, join_role_id) VALUES($1, $2) ON CONFLICT (guild_id) DO UPDATE SET "
                    "join_role_id = $2",
                    ctx.guild.id,
                    role.id,
                )
                if ctx.guild.id not in self.bot.servers:
                    self.bot.servers[ctx.guild.id] = {}
                self.bot.servers[ctx.guild.id]["join_role_id"] = role.id

                await ctx.send(f"When a member joins they will be given the role **{role.name}**.")
            else:
                await ctx.send(f"The role, **{role_name}** was not found. No change")
        else:
            await ctx.send("\N{NO ENTRY SIGN} That command is only available in servers.")

    @settings.command(aliases=['polls', 'pollschannel'])
    @commands.has_permissions(manage_guild=True)
    async def setpollchannel(self, ctx, *, poll_channel: typing.Union[TextChannel, str] = None):
        """
        Set the poll channel where polls should be sent. If "reset" is passed the poll channel will be reset.
        """
        if ctx.guild is not None:
            if poll_channel == "reset":
                await self.bot.db.execute(
                    "UPDATE guilds SET poll_channel_id = null WHERE guild_id = $1;",
                    ctx.guild.id
                )
                self.bot.servers[ctx.guild.id]["poll_channel_id"] = None
                await ctx.send("Poll channel disabled. If a user makes a poll it will be sent to the channel they ran "
                               "the command in. To add a poll channel type ``@JackBot settings setpollchannel ["
                               "channel]`` ")
                return
            elif poll_channel is None:
                if ctx.guild.id not in self.bot.servers:
                    self.bot.servers[ctx.guild.id] = {}
                db_channel = self.bot.servers[ctx.guild.id].get("poll_channel_id")
                if db_channel is None:
                    await ctx.send(
                        "Poll channel is disabled. If a user makes a poll it will be sent to the channel they ran "
                        "the command in. To add a poll channel type ``@JackBot settings setpollchannel ["
                        "channel]`` ")
                    return
                else:
                    channel = db_channel

                    await ctx.send(
                        f"The current poll channel is is **<#{channel}>**. To change it run the command again with"
                        " a channel as an argument. ``@JackBot settings setpollchannel [channel]``")

            elif type(poll_channel) == TextChannel:
                await self.bot.db.execute(
                    "INSERT INTO guilds(guild_id, poll_channel_id) VALUES($1, $2) ON CONFLICT (guild_id) DO UPDATE SET "
                    "poll_channel_id = $2",
                    ctx.guild.id,
                    poll_channel.id,
                )
                if ctx.guild.id not in self.bot.servers:
                    self.bot.servers[ctx.guild.id] = {}
                self.bot.servers[ctx.guild.id]["poll_channel_id"] = poll_channel.id

                await ctx.send(f"Poll channel set to <#{poll_channel.id}>")
            else:
                await ctx.send("⚠️ Channel not found, please try again.")
        else:
            await ctx.send("\N{NO ENTRY SIGN} That command is only available in servers.")

    @settings.command(aliases=['logs', 'setlogs', 'setloggingchannel'])
    @commands.has_permissions(manage_guild=True)
    async def setlogging(self, ctx, *, logs_channel: typing.Union[TextChannel, str] = None):
        """
        Set the logging channel where logs should be sent. If you pass in "reset" logging channel will be reset.
        All moderation commands are logged.
        """
        if ctx.guild is not None:
            if logs_channel == "reset":
                await self.bot.db.execute(
                    "UPDATE guilds SET logging_channel_id = null WHERE guild_id = $1;",
                    ctx.guild.id
                )
                self.bot.servers[ctx.guild.id]["logging_channel_id"] = None
                await ctx.send("Logging disabled. I will not log any action. To enable run the command again with"
                               " a channel as an argument. ``@JackBot settings setlogging [channel]``")
                return
            elif logs_channel is None:
                if ctx.guild.id not in self.bot.servers:
                    self.bot.servers[ctx.guild.id] = {}
                db_channel = self.bot.servers[ctx.guild.id].get("logging_channel_id")
                if db_channel is None:
                    await ctx.send("Logging disabled. I will not log any action. To enable run the command again with"
                                   " a channel as an argument. ``@JackBot settings setlogging [channel]``")
                    return
                else:
                    channel = db_channel

                    await ctx.send(
                        f"The current logging channel is is **<#{channel}>**. To change it run the command again with"
                        " a channel as an argument. ``@JackBot settings setlogging [channel]``")

            elif type(logs_channel) == TextChannel:
                await self.bot.db.execute(
                    "INSERT INTO guilds(guild_id, logging_channel_id) VALUES($1, $2) ON CONFLICT (guild_id) DO UPDATE SET "
                    "logging_channel_id = $2",
                    ctx.guild.id,
                    logs_channel.id,
                )
                if ctx.guild.id not in self.bot.servers:
                    self.bot.servers[ctx.guild.id] = {}
                self.bot.servers[ctx.guild.id]["logging_channel_id"] = logs_channel.id

                await ctx.send(f"Logging channel set to <#{logs_channel.id}>")
            else:
                await ctx.send("⚠️ Channel not found, please try again.")
        else:
            await ctx.send("\N{NO ENTRY SIGN} That command is only available in servers.")


def setup(bot):
    bot.add_cog(Settings(bot))
