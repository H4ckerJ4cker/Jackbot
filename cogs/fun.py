from discord.ext.commands import Cog, command, Context, EmojiConverter, MessageConverter, GuildConverter
from discord.ext import commands
from discord import Embed, Colour
from typing import Optional


class Fun(Cog):
    """
    Fun Commands
    """

    def __init__(self, bot):
        self.bot = bot

    @command(hidden=True)
    @commands.is_owner()
    async def send(self, ctx, emote: Optional[EmojiConverter] = None, *, text):
        """
        Sends a message as the bot.
        """
        await ctx.message.delete()
        message = await ctx.send(text)
        if emote is not None:
            await message.add_reaction(emote)

    @command(hidden=True, aliases=["pull", "update"])
    @commands.is_owner()
    async def restart(self, ctx):
        """
        Restarts the bot and pulls in the latest changes.
        """
        await ctx.send("Restarting and pulling latest changes into production...")
        await self.bot.close()

    @command(hidden=True)
    @commands.is_owner()
    async def react(self, ctx, emote: EmojiConverter, message: MessageConverter):
        """
        reacts to messaage.
        """
        await ctx.message.delete()
        await message.add_reaction(emote)

    @command(hidden=True)
    @commands.is_owner()
    async def guilds(self, ctx):
        """
        Lists guilds.
        """
        embed = Embed(
            color=Colour.blue(),
            title="Guild List",
            description=f"Guilds I'm in..."
        )
        for guild in self.bot.guilds:
            embed.add_field(name=guild.name, value=f"Members: {guild.member_count}"
                                                   f"\nOwner: {guild.owner.name}#{guild.owner.discriminator}"
                                                   f"\nCreated on: {guild.created_at.date()}"
                                                   f"\nID: {guild.id}")
        await ctx.send(embed=embed)

    @command(hidden=True)
    @commands.is_owner()
    async def leave(self, ctx, *, guild: GuildConverter):
        await guild.leave()
        await ctx.message.add_reaction("✅")

    @command()
    async def poll(self, ctx: Context, *, poll_question: str):
        """
        Takes a poll question and creates a poll in the poll channel or in the same channel it was invoked if no poll
        channel is setup.
        """
        if ctx.guild.id not in self.bot.servers:
            self.bot.servers[ctx.guild.id] = {}
        poll_channel_id = self.bot.servers[ctx.guild.id].get("poll_channel_id")
        if poll_channel_id is not None:
            confirm_msg = Embed(
                description=f":white_check_mark: Your poll has been sent to <#{poll_channel_id}> to be voted on.",
                color=0x6ABE6C)
            confirm_msg.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
            await ctx.send(embed=confirm_msg)
        else:
            poll_channel_id = ctx.channel.id

        poll_channel = self.bot.get_channel(poll_channel_id)
        poll_embed = Embed(color=0x37A7F3, title=poll_question)
        poll_embed.set_author(name=ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        poll_embed.set_footer(text=f"React bellow to vote.")
        poll = await poll_channel.send(embed=poll_embed)
        await poll.add_reaction("<:yes:831665509454839890>")
        await poll.add_reaction("<:neutral:831665552908615751>")
        await poll.add_reaction("<:no:831665477104173057>")


def setup(bot):
    bot.add_cog(Fun(bot))
