from discord import Game, Intents
from discord.ext.commands import Bot, when_mentioned_or
from os import environ
import asyncpg
import asyncio
import logging
import time
from log import DiscordHandler

logger = logging.getLogger(__name__)
intents = Intents.default()
intents.members = True
intents.messages = True

async def get_prefix(bot, message):
    try:
        if message.guild is not None:
            prefix = bot.servers[message.guild.id]["prefix"]
            if prefix is None:
                prefix = '!'
        else:
            prefix = '!'
    except KeyError:
        prefix = '!'
    prefix_return = prefix
    return when_mentioned_or(prefix_return)(bot, message)


async def run():
    credentials = {"user": environ.get("PGUSER"), "password": environ.get("PGPASSWORD"),
                   "database": environ.get("PGDATABASE"), "host": environ.get("PGHOST")}
    if not environ.get("LOCAL_DEBUGGING"):
        db = await asyncpg.create_pool(**credentials)
        bot = Bot(command_prefix=get_prefix, intents=intents)
        bot.db = db
        
        
        async def get_vars():
            await bot.wait_until_ready()
            # set global vars
            bot.logging_channel = bot.get_channel(831649393123393547)
            bot.time_start = time.time()
            
            # pull database
            servers = {}
            for guild in bot.guilds:
                servers[guild.id] = {}

                prefix = await bot.db.fetchval(
                    "SELECT prefix FROM guilds WHERE guild_id = $1",
                    guild.id,
                )
                if prefix is None:
                    prefix = '!'
                servers[guild.id]["prefix"] = prefix

                join_role = await bot.db.fetchval(
                    "SELECT join_role_id FROM guilds WHERE guild_id = $1",
                    guild.id,
                )
                servers[guild.id]["join_role_id"] = join_role

                logging_channel_id = await bot.db.fetchval(
                    "SELECT logging_channel_id FROM guilds WHERE guild_id = $1",
                    guild.id,
                )
                servers[guild.id]["logging_channel_id"] = logging_channel_id

                poll_channel_id = await bot.db.fetchval(
                    "SELECT poll_channel_id FROM guilds WHERE guild_id = $1",
                    guild.id,
                )
                servers[guild.id]["poll_channel_id"] = poll_channel_id
                
                welcome_channel_id = await bot.db.fetchval(
                    "SELECT welcome_channel_id FROM guilds WHERE guild_id = $1",
                    guild.id,
                )
                servers[guild.id]["welcome_channel_id"] = welcome_channel_id

            bot.servers = servers

        logger.addHandler(DiscordHandler(bot))
        logger.setLevel(logging.INFO)
        bot.log = logger
        bot.loop.create_task(get_vars())
    else:
        bot = Bot(command_prefix='!', activity=Game(name="@JackBot help"), intents=intents)
        bot.servers = {}
        logger.setLevel(logging.INFO)
        bot.log = logger
    bot.load_extension("cogs.general")
    bot.load_extension("cogs.moderation")
    bot.load_extension("cogs.fun")
    bot.load_extension("cogs.help")
    bot.load_extension("cogs.settings")
    try:
        await bot.start(environ.get("BOT_TOKEN"))
    except KeyboardInterrupt:
        if not environ.get("LOCAL_DEBUGGING"):
            await db.close()
        await bot.logout()


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
