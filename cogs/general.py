from discord.ext.commands import Cog, command, Context, BucketType
from discord import utils, Embed, Colour, Message, NotFound, Activity, ActivityType, Forbidden
from discord.ext import commands, tasks
import random
from mcstatus import MinecraftServer
import aiohttp
from os import environ


class General(Cog):
    """
    General Purpose Commands and Events
    """

    def __init__(self, bot):
        self.bot = bot
        self.status.start()
        self.update_dbl.start()

    def cog_unload(self):
        self.status.cancel()

    @Cog.listener()
    async def on_ready(self):
        print("Logged in as")
        print(self.bot.user.name)
        print(self.bot.user.id)
        print("------")

    @tasks.loop(seconds=125)
    async def status(self):
        activity_guilds = Activity(name=f'{len(self.bot.guilds)} servers', type=ActivityType.watching)
        activity_help = Activity(name='@Jackbot help', type=ActivityType.playing)
        activity_listening = Activity(name='to your suggestions', type=ActivityType.listening)
        activity_list = [activity_help, activity_guilds, activity_listening]
        await self.bot.change_presence(activity=random.choice(activity_list))

    @tasks.loop(minutes=30)
    async def update_dbl(self):
        url = "https://top.gg/api/bots/758352287101353995/stats"
        payload = {'server_count': len(self.bot.guilds)}
        headers = {'Authorization': environ.get("DBL_TOKEN")}
        if not environ.get("LOCAL"):

            async with aiohttp.ClientSession() as cs:
                r = await cs.post(url, headers=headers, data=payload)
                if r.status != 200:
                    log = self.bot.get_channel(772502152719499277)
                    await log.send(f"Updating server count on dbl failed with **{r.status}**.")

    @status.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

    @update_dbl.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()

    @Cog.listener()
    async def on_guild_join(self, guild):
        general = utils.find(lambda x: x.name == 'general', guild.text_channels)
        join_msg = (
            "Hi I'm JackBot, here for all your small time discord needs. My default prefix is **!** but "
            "you can change it with ``!settings prefix [new_prefix]`` and you can always summon me with a mention. "
            "I've got you covered for all your basic moderation and server misc but if you need specific feature feel "
            "free to send a message to the support server. To see all my available commands you can run ``!help`` and "
            "I will send you a DM. To find out how to customise me for your server run ``!settings`` for a list of "
            "settings you can change. If you need any help feel free to ask in my support server. Thank you for "
            "choosing JackBot, your no fuss bot for small servers :) https://discord.gg/t58T4mU9v9 "
        )
        try:
            await general.send(join_msg)
        except AttributeError:
            await guild.owner.send(join_msg)
        log = self.bot.get_channel(772502152719499277)
        await log.send(f"I just joined **{guild.name}**")

    @Cog.listener()
    async def on_member_join(self, member):
        join_role = self.bot.servers[member.guild.id]["join_role_id"]
        if join_role is not None:
            role = member.guild.get_role(join_role)
            await member.add_roles(role)

    @Cog.listener()
    async def on_guild_remove(self, guild):
        await self.bot.db.execute(
            "DELETE FROM guilds WHERE guild_id = $1",
            guild.id
        )
        log = self.bot.get_channel(772502152719499277)
        await log.send(f"I just left **{guild.name}**")

    @Cog.listener()
    async def on_message_delete(self, message):
        message_context = await self.bot.get_context(message)
        if message.guild is None:
            return
        try:
            log_channel_id = self.bot.servers[message.guild.id]["logging_channel_id"]
        except KeyError:
            log_channel_id = None
        if log_channel_id is None or message_context.valid is True or message.author.bot is True:
            return
        else:
            log_channel = self.bot.get_channel(log_channel_id)

            if not message.attachments:
                message_embed = Embed(
                    color=Colour.red(),
                    title="Message deleted",
                )
                message_embed.add_field(name="Channel", value=f"<#{message.channel.id}>")
                message_embed.add_field(name="Message Content", value=message.content, inline=False)
                message_embed.add_field(name="Author", value=message.author.mention, inline=False)
                await log_channel.send(embed=message_embed)
            else:
                for attachment in message.attachments:
                    if attachment.height is not None:
                        image_embed = Embed(
                            color=Colour.red(),
                            title="Image deleted",
                        )
                        image_embed.set_image(url=attachment.proxy_url)
                        image_embed.add_field(name="Channel", value=f"<#{message.channel.id}>")
                        image_embed.add_field(name="Author", value=message.author.mention, inline=False)
                        if message.content:
                            image_embed.add_field(name="Message Content", value=message.content, inline=False)
                        image_embed.add_field(name="Filename", value=attachment.filename, inline=False)
                        await log_channel.send(embed=image_embed)
                    else:
                        file_embed = Embed(
                            color=Colour.red(),
                            title="File deleted",
                        )
                        file_embed.add_field(name="Channel", value=f"<#{message.channel.id}>")
                        file_embed.add_field(name="Author", value=message.author.mention, inline=False)
                        if message.content:
                            file_embed.add_field(name="Message Content", value=message.content, inline=False)
                        file_embed.add_field(name="Filename", value=attachment.filename, inline=False)
                        await log_channel.send(embed=file_embed)

    @Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild is None:
            return
        try:
            log_channel_id = self.bot.servers[before.guild.id]["logging_channel_id"]
        except KeyError:
            log_channel_id = None
        if log_channel_id is None or before.author.bot is True:
            return
        else:
            log_channel = self.bot.get_channel(log_channel_id)
            if before.author.id != self.bot.user.id:

                message_embed = Embed(
                    color=Colour.orange(),
                    title="Message Edited",
                )
                message_embed.add_field(name="Channel", value=f"<#{before.channel.id}>")
                message_embed.add_field(name="Message", value=f"[**Jump to message.**]({after.jump_url})", inline=False)
                if before.content:
                    message_embed.add_field(name="Message Before", value=before.content, inline=False)
                if after.content:
                    message_embed.add_field(name="Message After", value=after.content, inline=False)
                message_embed.add_field(name="Author", value=before.author.mention, inline=False)
                await log_channel.send(embed=message_embed)

    @command()
    async def ping(self, ctx):
        """
        Checks the bot is online and returns the number of members in the server.
        """
        guild = ctx.guild
        embed = Embed(
            color=Colour.blue(),
            title="Pong!",
        )

        embed.add_field(name="Members", value=guild.member_count, inline=False)
        embed.add_field(name="Bot latency", value=f"{round(self.bot.latency * 1000)}ms", inline=False)
        embed.set_footer(icon_url=self.bot.user.avatar_url, text="Serving servers since 2020.")
        await ctx.send(embed=embed)

    @command(aliases=['mc'])
    @commands.cooldown(6, 120, BucketType.user)
    @commands.cooldown(30, 1800, BucketType.guild)
    async def mcstatus(self, ctx, server_address):
        """
        Get information on a minecraft server.
        """
        online_embed = Embed(
            title=f"{server_address} Status",
            colour=Colour.orange(),
            description="**Loading...**"
        )
        loading_message = await ctx.send(embed=online_embed)
        try:
            server = MinecraftServer(str(server_address), 25565)
            status = server.status()
            online = status.players.online
            max_players = status.players.max
            ping = round(status.latency)
            version = status.raw['version']['name']
            online_embed = Embed(
                title=f"{server_address} Status",
                colour=Colour.green(),
                description="Server is online!"
            )

            if version:
                online_embed.add_field(name="Server Version", value=version, inline=True)
            online_embed.add_field(name="Ping", value=f"{ping}ms", inline=True)
            online_embed.add_field(name="Players Online", value=f"{online}/{max_players}", inline=False)

            if online != 0:
                try:
                    names = ", ".join([user['name'] for user in server.status().raw['players']['sample']])
                    if online > 12:
                        names = names + "..."
                    if "§" not in names:
                        if names:
                            online_embed.add_field(name="Player Names", value=f"{names}", inline=False)
                except KeyError:
                    pass

            await loading_message.edit(embed=online_embed)
        except (ConnectionRefusedError, OSError):
            offline_embed = Embed(
                title=f"{server_address} Status",
                description="The specified server is offline or could not be queried. Please try again later.",
                colour=Colour.red()
            )
            await loading_message.edit(embed=offline_embed)

    @command()
    async def support(self, ctx):
        """
        Sends an invite link to the support server for the bot.
        """
        await ctx.send("https://discord.gg/t58T4mU9v9")

    @command()
    async def vote(self, ctx):
        """
        Sends an link to a page where you can vote for the bot to help it grow.
        """
        await ctx.send("https://top.gg/bot/758352287101353995/vote")

    @command()
    async def invite(self, ctx):
        """
        Sends a link you can use to add the bot to your server.
        """
        embed = Embed(
            color=Colour.blue(),
            title="Add Me to Your Server",
        )

        embed.set_footer(icon_url=self.bot.user.avatar_url, text="Serving servers since 2020.")
        embed.add_field(name="Admin", value="[**Click here**](https://discord.com/oauth2/authorize?client_id"
                                            "=758352287101353995&permissions=8&scope=bot) if you want to add "
                                            "the bot to your server as an "
                                            "administrator. (recommended)", inline=True)
        embed.add_field(name="Cherry Pick", value="[**Click here**](https://discord.com/oauth2/authorize?client_id"
                                                  "=758352287101353995&permissions=2147483639&scope=bot) if you want "
                                                  "to choose what permissions the bot "
                                                  "has on your server. (may cause bugs)", inline=True)
        await ctx.send(embed=embed)

    @command()
    async def prefix(self, ctx):
        """
        Get the current prefix.
        """
        if ctx.guild is not None:
            try:
                dbprefix = self.bot.servers[ctx.guild.id]["prefix"]
            except KeyError:
                self.bot.servers[ctx.guild.id] = {}
                dbprefix = self.bot.servers[ctx.guild.id]["prefix"]
            if dbprefix is None:
                prefix = '!'
            else:
                prefix = dbprefix

            await ctx.send(f"The current prefix is **{prefix}**.")
        else:
            await ctx.send("\N{NO ENTRY SIGN} That command is only available in servers.")

    @command()
    async def quote(self, ctx: Context, message_id: Message, channel=None):
        """
        Quotes the specified message.
        """
        message = message_id
        embed = Embed(
            description=f"{message.content}\n\n[Jump to message]({message.jump_url})",
            colour=Colour.blue(),
            timestamp=message.created_at,
        )
        embed.set_image(url=message.attachments[0].url) if message.attachments else ...
        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}",
                         icon_url=message.author.avatar_url)
        embed.set_footer(text=f"{message.guild.name} | #{message.channel}")

        await ctx.send(embed=message.embeds[0] if message.embeds else embed)

    @Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, "original", error)

        if isinstance(error, commands.CommandNotFound):
            return  # No need to log unfound commands anywhere or return feedback

        if isinstance(error, commands.MissingRequiredArgument):
            # Missing arguments are likely human error so do not need logging
            parameter_name = error.param.name
            return await ctx.send(
                f"⚠️ The required argument **{parameter_name}** was missing."
            )
        elif isinstance(error, commands.MissingPermissions):
            missing = error.missing_perms
            return await ctx.send(
                f"\N{NO ENTRY SIGN} You are missing the permission **{' '.join(str(x) for x in missing)}**"
            )
        elif isinstance(error, commands.CommandOnCooldown):
            retry_after = round(error.retry_after)
            return await ctx.send(
                f"\N{HOURGLASS} Command is on cooldown, try again after **{retry_after}** seconds."
            )
        elif isinstance(error, commands.MemberNotFound):
            return await ctx.send("⚠️ Member not found, please try again.")

        # All errors below this need reporting and so do not return

        if isinstance(error, commands.ArgumentParsingError):
            # Provide feedback & report error
            await ctx.send(
                "⚠️ An issue occurred while attempting to parse an argument."
            )
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ A error occurred as you supplied a bad argument.")
        elif isinstance(error, Forbidden):
            await ctx.send(f"⚠️ I do not have the correct permissions to run that command for you.")
        else:
            await ctx.send(
                "⚠️ An error occurred with that command, the error has been reported."
            )

        extra_context = {
            "discord_info": {
                "Channel": ctx.channel.mention,
                "User": ctx.author.mention,
                "Command": ctx.message.content,
                "Server": ctx.guild.name,
                "Owner": ctx.guild.owner.mention,
            }
        }

        if ctx.guild is not None:
            # We are NOT in a DM
            extra_context["discord_info"]["Message"] = (
                f"[{ctx.message.id}](https://discordapp.com/channels/"
                f"{ctx.guild.id}/{ctx.channel.id}/{ctx.message.id})"
            )
        else:
            extra_context["discord_info"]["Message"] = f"{ctx.message.id} (DM)"

        self.bot.log.exception(error, extra=extra_context)


def setup(bot):
    bot.add_cog(General(bot))
