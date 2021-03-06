from discord import Colour, Embed
from discord.ext import commands


class EmbeddedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(command_attrs={'help': 'Gives detailed information about a command.'})

    async def command_callback(self, ctx, *, command=None):
        if command is not None:
            for cog in ctx.bot.cogs:
                if str(command).casefold() == cog.casefold():
                    command = cog
                    break
        return await super().command_callback(ctx, command=command)

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = Embed(
            color=Colour.blue(),
            description=f"Type ``{self.clean_prefix}help [command]`` for more info on a command.\n""You can also type "
                        f"``{self.clean_prefix}help [category]`` for more info on a category."
        )
        for cog in mapping.keys():
            if cog is not None:
                if cog.get_commands():
                    embed.add_field(name=cog.qualified_name,
                                    value=f"``{self.clean_prefix}help {cog.qualified_name.lower()}``")
                embed.set_footer(text=f"Run {self.clean_prefix} prefix in a server to get my prefix in that server.")

        await ctx.send(embed=embed)

    async def send_cog_help(self, cog):
        ctx = self.context
        embed = Embed(
            color=Colour.blue(),
            title=cog.description,
            description=f"Type ``{self.clean_prefix}help [command]`` for more info on a command.\n You can also type "
                        f"``{self.clean_prefix}help [category]`` for more info on a different category."
        )
        embed.set_footer(text=f"Run {self.clean_prefix}prefix in a server to get my prefix in that server.")
        for command in cog.get_commands():
            if command.hidden is not True:
                embed.add_field(name=f"``{self.clean_prefix}{command.name}``", value=command.help)

        await ctx.send(embed=embed)

    async def send_command_help(self, command):
        ctx = self.context
        if command.root_parent is None:
            parent = ""
        else:
            parent = command.root_parent.name + " "
        if command.hidden is not True:
            embed = Embed(
                color=Colour.blue(),
                title=f"``{self.clean_prefix}{parent}{command.name}``",
                description=command.help
            )
            embed.add_field(name="Usage", value=f"``{self.clean_prefix}{parent}{command.name} {command.signature}``",
                            inline=False)

            if command.aliases:
                embed.add_field(name="Aliases", value=", ".join(f'``{self.clean_prefix}{parent}{alias}``'
                                                                for alias in command.aliases), inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f'No command called "{command.name}" found.')


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot._original_help_command = bot.help_command
        bot.help_command = EmbeddedHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self.bot._original_help_command


def setup(bot):
    bot.add_cog(Help(bot))
