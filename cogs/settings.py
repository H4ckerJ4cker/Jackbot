from discord.ext.commands import Cog, command
from discord.ext import commands
from discord import utils, TextChannel, Embed, Colour


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

    @settings.command()
    @commands.has_permissions(manage_guild=True)
    async def prefix(self, ctx, *, new_prefix):
        """
        Set the prefix of the bot.
        """
        if ctx.guild is not None:
            await self.bot.db.execute(
                "INSERT INTO guilds(guild_id, prefix) VALUES($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
                ctx.guild.id,
                new_prefix,
            )
            try:
                self.bot.servers[ctx.guild.id]["prefix"] = new_prefix
            except KeyError:
                # server is not in dict.
                self.bot.servers[ctx.guild.id] = {}
                self.bot.servers[ctx.guild.id]["prefix"] = new_prefix
            await ctx.send(f"Prefix set to **{new_prefix}**.")
        else:
            await ctx.send("\N{NO ENTRY SIGN} That command is only available in servers.")

    @settings.command()
    @commands.has_permissions(manage_guild=True)
    async def autorole(self, ctx, *, role_name=None):
        """
        Set the role members will get when they join the server. If you don't specify a role autorole will be reset.
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
                join_role = self.bot.servers[ctx.guild.id]["join_role_id"]
                await ctx.send(f"The current autorole for new members is **{join_role.name}**")
                return

            role = utils.get(ctx.guild.roles, name=role_name)
            if role is not None:
                await self.bot.db.execute(
                    "INSERT INTO guilds(guild_id, join_role_id) VALUES($1, $2) ON CONFLICT (guild_id) DO UPDATE SET "
                    "join_role_id = $2",
                    ctx.guild.id,
                    role.id,
                )
                try:
                    self.bot.servers[ctx.guild.id]["join_role_id"] = role.id
                except KeyError:
                    self.bot.servers[ctx.guild.id] = {}
                    self.bot.servers[ctx.guild.id]["join_role_id"] = role.id

                await ctx.send(f"When a member joins they will be given the role **{role.name}**.")
            else:
                await ctx.send(f"The role, **{role_name}** was not found. No change")
        else:
            await ctx.send("\N{NO ENTRY SIGN} That command is only available in servers.")

    @settings.command()
    @commands.has_permissions(manage_guild=True)
    async def polls(self, ctx, *, poll_channel: TextChannel = None):
        """
        Set the poll channel where polls should be sent. If no channel is specified the poll channel will be reset.
        """
        if ctx.guild is not None:
            if poll_channel is None:
                await self.bot.db.execute(
                    "UPDATE guilds SET poll_channel_id = null WHERE guild_id = $1;",
                    ctx.guild.id
                )
                self.bot.servers[ctx.guild.id]["poll_channel_id"] = None
                await ctx.send("Poll channel reset. If a user makes a poll it will be sent to the channel they ran "
                               "the command in.")
                return

            await self.bot.db.execute(
                "INSERT INTO guilds(guild_id, poll_channel_id) VALUES($1, $2) ON CONFLICT (guild_id) DO UPDATE SET "
                "poll_channel_id = $2",
                ctx.guild.id,
                poll_channel.id,
            )
            try:
                self.bot.servers[ctx.guild.id]["poll_channel_id"] = poll_channel.id
            except KeyError:
                self.bot.servers[ctx.guild.id] = {}
                self.bot.servers[ctx.guild.id]["poll_channel_id"] = poll_channel.id

            await ctx.send(f"Poll channel set to **{poll_channel.name}**")
        else:
            await ctx.send("\N{NO ENTRY SIGN} That command is only available in servers.")


def setup(bot):
    bot.add_cog(Settings(bot))
