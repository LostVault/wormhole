# ------------- ИМПОРТ МОДУЛЕЙ

import logging  # Импортируем моудль логирования

import aiosqlite # Импортируем моудль работы с базами SQLite
import discord  # Импортируем основной модуль
from discord.ext import commands  # Импортируем команды из модуля discord.ext
from discord.ext.commands import has_permissions
from discord_slash import SlashCommand, SlashContext # Импортируем модуль команд с косой чертой (slash)
# from discord_slash.utils.manage_commands import create_choice, create_option

import config  # Импортируем настройки приложения

# ------------- ИМПОРТ МОДУЛЕЙ // КОНЕЦ


# ------------- СОЗДАЁМ ПРИЛОЖЕНИЕ И НАЗЫВАЕМ ЕГО CLIENT
client = commands.Bot(description="Test bot", command_prefix=commands.when_mentioned_or(config.prefix),
                      case_insensitive=True, help_command=None)


# ------------- СОЗДАЁМ ОБРАБОТКУ КОМАНДЫ С КОСОЙ ЧЕРТОЙ ЧЕРЕЗ СОЗДАННОЕ ПРИЛОЖЕНИЕ
slash = SlashCommand(client, sync_commands=True)


# ------------- СОЗДАЁМ ОБРАБОТКУ КОМАНДЫ С КОСОЙ ЧЕРТОЙ ЧЕРЕЗ СОЗДАННОЕ ПРИЛОЖЕНИЕ // КОНЕЦ


# ------------- ВЫВОДИМ ДАННЫЕ ПРДКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ В КОНСОЛЬ
logging.basicConfig(level=logging.INFO)


# ------------- ВЫВОДИМ ДАННЫЕ ПРДКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ В КОНСОЛЬ // КОНЕЦ


# ------------- БЫСТЫРЫЙ СКРИПТ НА ОТПРАВКУ СООБЩЕНИЙ
async def send_to_servers(*args, **kwargs):
    """
    :param args:
    :param kwargs:
    :return:
    send message to all connected servers to config.globalchannel channel, arguments as for channel.send()
    """
    for guild in client.guilds:
        if channel := discord.utils.get(guild.text_channels, name=config.globalchannel):
            try:
                await channel.send(*args, **kwargs)
            except discord.Forbidden:
                print(f"System: Невозможно отправить сообщение на сервер {guild.name}: Недостаточно прав")
            except discord.HTTPException as e:
                print(f"System: Невозможно отправить сообщение на сервер {guild.name}: {e}")
            except Exception as e:
                print(f"System: Не получилось отправить сообщение на сервер {guild.name}: {e}")

# ------------- БЫСТЫРЫЙ СКРИПТ НА ОТПРАВКУ СООБЩЕНИЙ // КОНЕЦ


# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ
@client.event
async def on_ready():
    client.sql_conn = await aiosqlite.connect('Wormhole.sqlite')
    await client.sql_conn.execute('create table if not exists black_list (userid integer not null, add_timestamp text '
                                  'default current_timestamp, reason text, banner_id integer);')

    print('\n-••••••••••••••••••••••••••••••-')
    # Показывает имя приложения, указанное на discordapp.com
    print(f' APP Username: {client.user} ')
    print(f' Using token {config.token[0:2]}...{config.token[-3:-1]}')
    print(f' Using global channel {config.globalchannel}')
    # Показывает ID приложения указанное на discordapp.com
    print(' APP Client ID: {0.user.id} '.format(client))
    print(
        ' Link for connection: https://discordapp.com/oauth2/authorize?&client_id={0.user.id}&permissions=0&scope=bot%20applications.commands'
        '=bot&permissions=0'.format(
            client))
    print('-••••••••••••••••••••••••••••••-')
    # Выводит список серверов, к которым подключено приложение
    print('Servers connected to:')
    for guild in client.guilds:
        print(guild.name)
    print('-••••••••••••••••••••••••••••••-\n')
    # Изменяем статус приложения
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Elite Dangerous'))

    # Отправляем сообщение в общий канал
    emStatusOn = discord.Embed(title='⚠ • ВНИМАНИЕ!', description='Приложение запущено.', colour=0x90D400)
    emStatusOn.set_image(
        url="https://media.discordapp.net/attachments/682731260719661079/682731350922493952/ED1.gif")
    await send_to_servers(embed=emStatusOn, delete_after=13)
    # Отправляем сообщение


# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ // КОНЕЦ


# ------------- ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА
@client.event
async def on_message(message):
    # Дублирует сообщения в консоль приложения
    print('{0.guild} / #{0.channel} / {0.author}: {0.content}'.format(message))

    # Пропускает комманды для регистрации
    await client.process_commands(message)

    # Игнорируем сообщения, начинающиеся с преффикса комманд
    if message.content.startswith(config.prefix) or client.user.mentioned_in(message):
        return

    # Игнорируем сообщения, отправленные другими приложениеми
    if message.author.bot:
        return

    # Игнорируем сообщения, отправленные этим приложением
    if message.author.id == client.user.id:
        return

    # Игнорируем сообщения, отправленные не в забриджованный канал
    if message.channel.name != config.globalchannel:
        return

    # Игнорируем сообщения с упоминанием
    if message.mentions or message.mention_everyone:
        await message.delete()
        await message.channel.send(
            '` ⚠ • ВНИМАНИЕ! ` Сообщения, с упоминанием всех активных и неактивных пользователей, не пропускаются в '
            'общий чат.'.format(
                message), delete_after=13)
        return

    # Игнорируем сообщения с символом @
    if "@" in message.content:
        await message.delete()
        await message.channel.send('` ⚠ • ВНИМАНИЕ! ` Упс! Что-то пошло не так.'.format(message), delete_after=13)
        return

    # Игнорируем сообщения, отправленные пользователем из чёрного списка
    if (await (await client.sql_conn.execute(
            'select count(*) from black_list where userid = ?;', [message.author.id])).fetchone())[0] == 1:
        await message.delete()
        await message.channel.send(
            '` ⚠ • ВНИМАНИЕ! ` Пользователи, нахоядщиеся в списке **Black Overlord List**, не могут отправлять '
            'собщения на другие сервера.'.format(
                message), delete_after=13)
        return

    # Удаляем сообщение, отправленное пользователем
    try:
        await message.delete()
    except Exception:
        pass

    # Создаём сообщение
    emGlobalMessage = discord.Embed(description=f" **{message.author.name}**: {message.content}", colour=0x2F3136)
    emGlobalMessage.set_footer(icon_url=message.guild.icon_url,
                               text=f"Сервер: {message.guild.name} // ID пользователя: {message.author.id}")

    for attachment in message.attachments:
        if attachment.filename.endswith(('bmp', 'jpeg', 'jpg', 'png', 'gif')):
            emGlobalMessage.set_image(url=attachment.url)

    # Отправляем сообщение
    await send_to_servers(embed=emGlobalMessage)


# ------------- ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА // КОНЕЦ


# ------------- ОБРАБАТЫВАВЕМ ОШИБКИ КОММАНД
@client.event
async def on_command_error(ctx, error, amount=1):
    if isinstance(error, commands.CommandNotFound):
        # Удаляем сообщение отправленное пользователем
        await ctx.channel.purge(limit=amount)
        # Создаём сообщение
        embedcommandnotfound = discord.Embed(title='ВНИМАНИЕ!',
                                             description='' + ctx.author.mention + ', к сожалению, команды **'
                                                         + ctx.message.content + '** не существует.',
                                             color=0xd40000)
        embedcommandnotfound.set_footer(icon_url=ctx.author.avatar_url,
                                        text='Vox Galactica // Сообщение удалится через 13 секудн.')
        # Отправляем сообщение и удаляем его через 13 секунд
        await ctx.send(embed=embedcommandnotfound, delete_after=13)
        return
    if isinstance(error, commands.MissingPermissions):
        # Удаляем сообщение отправленное пользователем
        await ctx.channel.purge(limit=amount)

        # Создаём информационное сообщение
        embedcommandMissingPermissions = discord.Embed(title='ВНИМАНИЕ!',
                                                       description='' + ctx.author.mention
                                                                   + ', к сожалению, у вас нет прав на комманду **'
                                                                   + ctx.message.content + '',
                                                       color=0xd40000)
        embedcommandMissingPermissions.set_footer(icon_url=ctx.author.avatar_url,
                                                  text='Vox Galactica // Сообщение удалится через 13 секудн.')
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await ctx.send(embed=embedcommandMissingPermissions, delete_after=13)
        return
    print(ctx.message.content, error)


# ------------- ОБРАБАТЫВАВАЕМ ОШБИКИ КОММАНД // КОНЕЦ


# ------------- КОМАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ
@slash.slash(name="ping", description="Проверить состояние приложения.", guild_ids=config.guild_ids)
# Команду может выполнить только владелец приложения
@commands.is_owner()
async def ping(ctx, amount=1):
    # Создаём информационное сообщение
    emPing = discord.Embed(title='⚠ • ВНИМАНИЕ!', description='Получен ответ.', colour=0x90D400)
    # Отправляем информационное сообщение и удаляем его через 13 секунд
    await ctx.send(embed=emPing, delete_after=13)
    # Отправляем сообщение - Обычное
    # await ctx.send(f'` **{ctx.author.name}** ` Pong! ({client.latency * 1000}ms)', delete_after=13)


@client.command(aliases=['пинг'], brief='Проверить состояние приложения.', pass_context=True)
# Команду может выполнить только владелец приложения
@commands.is_owner()
async def ping(ctx, amount=1):
    # Удаляем сообщение, отправленное пользователем
    await ctx.channel.purge(limit=amount)

    # Создаём информационное сообщение
    emPing = discord.Embed(title='⚠ • ВНИМАНИЕ!', description='Получен ответ.', colour=0x90D400)
    # Отправляем информационное сообщение и удаляем его через 13 секунд
    await ctx.send(embed=emPing, delete_after=13)
    # Отправляем сообщение - Обычное
    # await ctx.send(f'` **{ctx.author.name}** ` Pong! ({client.latency * 1000}ms)', delete_after=13)


# ------------- КОММАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ // КОНЕЦ


# ------------- КОММАНДА ПОМОЩИ
@slash.slash(name="help", description="Показать информацию о командах используемых приложением.", guild_ids=config.guild_ids)
# Команду может выполнить только владелец приложения
@commands.is_owner()
async def help(ctx, amount=1):
    # Создаём информационное сообщение
    emHelp = discord.Embed(title='ПОМОЩЬ', description='```Некоторые из ниже указанных команд могут не работать или для их использования могут требоваться определённые разрешения.```', colour=0x2F3136)
    emHelp.add_field(name='Список комманд', value='`ping` - Проверить состояние приложения.\n`help` - Показать информацию о командах используемых приложением.\n`information` - Показать информацию о приложение.\n`clear` - Удалить сто последних сообщений на канале.\n`bluadd` - Записать пользователя в чёрный список.\n`bluremove` - Стереть пользователя из чёрного списка.\n`serverslist` - Показать список серверов, к которым подключено приложение.\n`serversleave` - Отключить приложение от указанного сервера.\n`setup` - Создать канала для приёма и передачи сообщений.')
    emHelp.add_field(name='Дополнительная информация', value='Дополнительную информацию о приложение можно запросить командой `information`', inline=False)
    # Отправляем информационное сообщение и удаляем его через 13 секунд
    await ctx.send(embed=emHelp, delete_after=60)


# ------------- КОММАНДА ПОМОЩИ // КОНЕЦ


# ------------- КОМАНДА ОТОБРАЖЕНИЯ ИФОРМАЦИИ О ПРИЛОЖЕНИЕ
@slash.slash(name="information", description="Показать информацию о приложение.", guild_ids=config.guild_ids)
async def information(ctx, amount=1):
    print("".join(guild.name + '\n' for guild in client.guilds))
    # Создаём сообщение
    emInformation = discord.Embed(title='ИНФОРМАЦИЯ',
                                  description='Приложение создана для обмена текстовыми и файловыми сообщениями между серверами по игре [Elite Dangerous](https://www.elitedangerous.com/). В первую очередь приложение направлено помочь эскадронам с закрытыми серверами, обмениваться сообщениями с другими серверами и для тех серверов и пользователи которых предпочитают находится только на своём сервере по [Elite Dangerous](https://www.elitedangerous.com/). Для остальных же данное приложение может быть не так востребовано, но так как приложение не привязано к какому либо серверу, его можно использовать для серверов другой тематики.\n\nЕсли вы владеете одним из серверов по [Elite Dangerous](https://www.elitedangerous.com/) или связанной тематике и хотите подключить приложение к себе на сервер, воспользуйтесь данной [ссылкой](https://discordapp.com/oauth2/authorize?&client_id=826410895634333718&scope=bot&permissions=0), либо можете на основе исходного кода данного приложения сделать свою сеть обмена сообщениями например по торговле или другой игре.',
                                  colour=0x2F3136)
    emInformation.add_field(name='Разработчики ', value='• <@420130693696323585>\n• <@665018860587450388>')
    emInformation.add_field(name='Благодарности', value='• <@478527700710195203>')
    # emInformation.add_field(name='Список серверов', value="".join(guild.name + '\n' for guild in client.guilds))
    emInformation.set_footer(text=client.user.name)
    # Отправляем сообщение и удаляем его через 60 секунд
    await ctx.send(embed=emInformation, delete_after=60)


@client.command(aliases=['информация', 'инфо', 'авторы'], brief='Показать информацию о приложение.', pass_context=True)
async def information(ctx, amount=1):
    # Удаляем сообщение отправленное пользователем
    await ctx.channel.purge(limit=amount)
    print("".join(guild.name + '\n' for guild in client.guilds))
    # Создаём сообщение
    emInformation = discord.Embed(title='ИНФОРМАЦИЯ',
                                  description='Приложение создано для обмена текстовыми и файловыми сообщениями между серверами по игре [Elite Dangerous](https://www.elitedangerous.com/). В первую очередь приложение направлено на помощь эскадронам с закрытыми серверами обмениваться сообщениями с другими серверами и для тех серверов, пользователи которых предпочитают находиться только на своём сервере по [Elite Dangerous](https://www.elitedangerous.com/). Для остальных же данное приложение может быть не так востребовано, но так как приложение не привязано к какому-либо серверу, его можно использовать для серверов другой тематики.\n\nЕсли вы владеете одним из серверов по [Elite Dangerous](https://www.elitedangerous.com/) или связанной тематике и хотите подключить приложение к себе на сервер, воспользуйтесь данной [ссылкой](https://discordapp.com/oauth2/authorize?&client_id=826410895634333718&scope=bot&permissions=0), либо можете на основе исходного кода данного приложения сделать свою сеть обмена сообщениями например по торговле или другой игре.',
                                  colour=0x2F3136)
    emInformation.add_field(name='Разработчики ', value='• <@420130693696323585>\n• <@665018860587450388>')
    emInformation.add_field(name='Благодарности', value='• <@478527700710195203>')
    # emInformation.add_field(name='Список серверов', value="".join(guild.name + '\n' for guild in client.guilds))
    emInformation.set_footer(text=client.user.name)
    # Отправляем сообщение и удаляем его через 60 секунд
    await ctx.send(embed=emInformation, delete_after=60)


# ------------- КОМАНДА ОТОБРАЖЕНИЯ ИФОРМАЦИИ О ПРИЛОЖЕНИЕ // КОНЕЦ


# ------------- КОМАНДА УДАЛЕНИЯ СООБЩЕНИЙ НА КАНАЛЕ
@client.command(aliases=['очистить'], brief='Удалить сто последних сообщений на канале.', pass_context=True)
# Команду может выполнить только пользователяь с ролью администратор
@has_permissions(administrator=True)
async def clear(ctx, amount=100):
    # Удаляем сто последних сообщений на канале
    await ctx.channel.purge(limit=amount)


# ------------- КОМАНДА УДАЛЕНИЯ СООБЩЕНИЙ НА КАНАЛЕ // КОНЕЦ


# ------------- КОМАНДА ЗАПИСИ ПОЛЬЗОВАТЕЛЯ В ЧЁРНЫЙ СПИСОК
@client.command(aliases=['добавить'], brief='Записать пользователя в чёрный список.', pass_context=True)
# Команду может выполнить только владельце приложения
@commands.is_owner()
async def bluadd(ctx, amount=1):
    userid_to_ban = ctx.message.content.split(' ')[1]
    await ctx.message.delete()
    try:
        userid_to_ban = int(userid_to_ban)
    except ValueError:
        await ctx.channel.send('Для блокировки пользователя необходимо указать ID пользователя')
        return
    await client.sql_conn.execute('insert into black_list (userid) values (?);', [userid_to_ban])
    await client.sql_conn.commit()

    # Создаём информационное сообщение
    emBlackListAdd = discord.Embed(title='⚠ • ВНИМАНИЕ!', description='Пользователь с ID ' + str(userid_to_ban) +
                                                                      ' записан в чёрный список.', color=0xd40000)
    # Отправляем информационное сообщение и удаляем его через 13 секунд
    await ctx.send(embed=emBlackListAdd, delete_after=13)
    # Отправляем сообщение - Обычное
    # await ctx.channel.send(f'` ⚠ • ВНИМАНИЕ! ` Пользователь с ID {userid_to_ban} внесён в чёрный список.')


# ------------- КОМАНДА ЗАПИСИ ПОЛЬЗОВАТЕЛЯ В ЧЁРНЫЙ СПИСОК // КОНЕЦ


# ------------- КОМАНДА УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ ИЗ ЧЁРНОГО СПИСКА
# ------------- КОМАНДА УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ ИЗ ЧЁРНОГО СПИСКА // КОНЕЦ


# ------------- КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ
@client.command(aliases=['сервера'], brief='Показать список серверов, к которым подключено приложение.',
                pass_context=True)
# Команду может выполнить только владельце приложения
@commands.is_owner()
async def servers_list(ctx, amount=1):
    # Удаляем сообщение отправленное пользователем
    await ctx.channel.purge(limit=amount)
    print("".join(guild.name + '\n' for guild in client.guilds))
    # Создаём сообщение
    emServers = discord.Embed(title='СПИСОК СЕРВЕРОВ',
                              description='Список серверов, к которым подключено приложение.',
                              colour=0x2F3136)

    emServers.add_field(
        name='Список серверов',
        value="".join(guild.name + f' (ID:{guild.id})\n' for guild in client.guilds))
    emServers.set_footer(text=' ' + client.user.name + ' ')
    # Отправляем сообщение и удаляем его через 60 секунд
    await ctx.send(embed=emServers, delete_after=60)


# ------------- КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ // КОНЕЦ


# ------------- КОМАНДА ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ ОТ СЕРВЕРА
@client.command(pass_context=True)
# Команду может выполнить только владельце приложения
@commands.is_owner()
async def server_leave(ctx, id_to_kick: int):
    if guild_to_leave := client.get_guild(id_to_kick) is None:
        await ctx.send('No guild with such ID')
        return
    await guild_to_leave.leave()


# ------------- КОМАНДА ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ ОТ СЕРВЕРА // КОНЕЦ


# ------------- КОМАНДА СОЗДАНИЯ КАНАЛА ДЛЯ ПРИЁМА И ОТПРАВКИ СООБЩЕНИЙ
@client.command(aliases=['установка', 'подключить'], brief='Создать канала для приёма и передачи сообщений.',
                pass_context=True)
# Команду может выполнить только пользователяь с ролью администратор
@has_permissions(administrator=True)
async def setup(ctx, amount=1):
    # Удаляем сообщение отправленное пользователем
    await ctx.channel.purge(limit=amount)
    # Создаём канал
    guild = ctx.message.guild
    await guild.create_text_channel(name='wormhole')

# ------------- КОМАНДА СОЗДАНИЯ КАНАЛА ДЛЯ ПРИЁМА И ОТПРАВКИ СООБЩЕНИЙ // КОНЕЦ


# Генирируемый токен при создание приложения на discordapp.com необходимый для подключенияю к серверу. //
# Прописывается в config.py
client.run(config.token)


# ------------- СОЗДАЁМ ПРИЛОЖЕНИЕ И НАЗЫВАЕМ ЕГО CLIENT  // КОНЕЦ
