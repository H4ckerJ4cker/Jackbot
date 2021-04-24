
<a target="_blank" href="LICENSE" title="License: MIT"><img src="https://img.shields.io/badge/License-MIT-blue.svg"></a>
<a target="_blank" href="https://www.python.org/downloads/" title="Python version"><img src="https://img.shields.io/badge/python-3.9.4-green.svg"></a>
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/pwnker/jackbot/Basic%20Lint)



# JackBot

JackBot is a breath of fresh air for small discord servers who need a simple bot to help run their server smoothly without having to deal with complex web panels and configuration. If you have a small community and need to do a bit more as an admin than the built in discord functions, JackBot is for you.

JackBot has various features to help you automate your server, such as autorole on join and easy to understand moderation commands and logs. JackBot also boasts various other commands such as minecraft server stats and polls, to give your server extra utility.

If you have any suggestions or need support don't hesitate to join the server linked below

[![Invite](https://img.shields.io/website?style=for-the-badge&up_message=Invite%20Jackbot&label=&up_color=%236F85CDFF&url=https%3A%2F%2Fpwnker.com)](https://pwnker.com)

[![Discord](https://img.shields.io/discord/827894573711228948?color=%236F85CDFF&logo=discord&style=for-the-badge&label=Support)](https://pwnker.com/discord) 
## Features
JackBot has a range of features to make your server the best it can be! JackBot can also be configured to use custom prefixes and to send messages to specific channels after certain events happen (e.g on user join.)

### Moderation
JackBot has various moderation commands to help keep your server safe. All moderation actions are logged to a log channel if one is configured.

![image](https://user-images.githubusercontent.com/56278210/115973455-fd422480-a54c-11eb-926b-6e4889676e2b.png)

 - `!purge` - Bulk delete messages
 - `!mute` - Mute a member server wide
 - `!block` - Mute a member in a single channel
 - `!ban` - Ban a member from your server
 - `!slowmode` - Set the slowmode for a channel

 ### Server Miscellaneous
 JackBot can also be configured to run automated actions to make your server run smoothly.
 
 - Giving users a role when they join.
 - Sending welcome messages to a channel when a user joins.
 - Sending all polls to a specific polls channel.

 ### Logging
 If a logging channel is configured JackBot will log deleted and edited messages. All moderation actions are also logged.

![image](https://user-images.githubusercontent.com/56278210/115974873-d89f7a00-a557-11eb-8413-961e80d27021.png)

![image](https://user-images.githubusercontent.com/56278210/115974638-fc61c080-a555-11eb-839d-be8095cf2f1a.png)

### Special Commands

JackBot also has a few extra commands to improve the functionallity of your server. These include getting the status of a mincraft server, polls and more.

`!mcstatus`

 ![image](https://user-images.githubusercontent.com/56278210/115974607-cde3e580-a555-11eb-8967-e77a965757e7.png)


 `!poll`

 ![image](https://user-images.githubusercontent.com/56278210/115974594-befd3300-a555-11eb-87db-b682a7e1e4b1.png)


 `!quote`

 ![image](https://user-images.githubusercontent.com/56278210/115974570-9b39ed00-a555-11eb-9f22-3a58770cf0ea.png)


## Documentation

If you need more detailed information about JackBot you can check out the [documentation](https://github.com/pwnker/Jackbot/wiki)

  
## Contributing

Contributions are always welcome!


### Installation

#### Docker
You can install JackBot using docker with the provided dockerfiles in the repository.

```
git clone https://github.com/pwnker/Jackbot
cd Jackbot
docker-compose up
```

#### Bare Metal
If you prefer you can also install JackBot bare metal by cloning the repository and installing the dependencies. You might want to set the enviroment variable `LOCAL_DEBUGGING=1` to stop JackBot trying to connect to a database if you havent set one up.
```
git clone https://github.com/pwnker/Jackbot
cd Jackbot
python3 -m pip install requirements.txt
python3 bot.py
``` 
#### Environment Variables

Make sure you set the correct environment variables either in the docker-compose.yml or in the bare metal installation to ensure the bot functions correctly.

Setting `LOCAL_DEBUGGING=1` Will stop JackBot from trying to connect to a database and disable the command error handler.

If you are using the database features then you must also set the correct credentials in the environment variables `PGUSER`, `PGDATABASE`, `PGHOST` and `PGPASSWORD`.

Of course also make sure you set the bot token using `BOT_TOKEN` 
