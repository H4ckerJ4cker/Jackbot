from discord.ext.commands import Cog, command, Context
from discord import Embed
from discord.ext import commands


class Fun(Cog):
    """
    Fun Commands
    """

    def __init__(self, bot):
        self.bot = bot

    @command()
    @commands.has_permissions(administrator=True)
    async def send(self, ctx, *, text):
        """
        Sends a message as the bot.
        """
        await ctx.message.delete()
        await ctx.send(text)

    @command()
    async def poll(self, ctx: Context, *, poll_question: str):
        """
        Takes a poll question and creates a poll in the poll channel or in the same channel it was invoked if no poll channel is setup.
        """
        poll_channel_id = self.bot.servers[ctx.guild.id]["poll_channel_id"]
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
        await poll.add_reaction("<:yes:779124573286957078>")
        await poll.add_reaction("<:neutral:779124664660131912>")
        await poll.add_reaction("<:no:779124611643080734>")


def setup(bot):
    bot.add_cog(Fun(bot))
