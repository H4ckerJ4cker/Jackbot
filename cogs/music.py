from discord.ext.commands import Cog


class Music(Cog):
    """
    Music Commands
    """

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Music(bot))
