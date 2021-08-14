# -*- coding: utf-8 -*-
# ------------- ИМПОРТ МОДУЛЕЙ
import asyncio  # Какая-то непонятная штука ᓚᘏᗢ
import logging  # Импортируем модуль логирования

import aiosqlite  # Импортируем модуль работы с базами SQLite
import discord  # Импортируем основной модуль
from discord.ext import commands  # Импортируем команды из модуля discord.ext
from discord_slash import SlashCommand, SlashContext  # Импортируем модуль команд с косой чертой (slash)
from discord_slash.utils.manage_commands import create_choice, create_option

import config  # Импортируем настройки приложения
import signal  # Какая-то непонятная штука ᓚᘏᗢ

# ------------- ИМПОРТ МОДУЛЕЙ // КОНЕЦ


# ------------- СОЗДАЁМ ПРИЛОЖЕНИЕ И НАЗЫВАЕМ ЕГО CLIENT
client = commands.Bot(description=config.client_short_description, command_prefix=None, help_command=None)

# ------------- СОЗДАЁМ ОБРАБОТКУ КОМАНДЫ С КОСОЙ ЧЕРТОЙ ЧЕРЕЗ СОЗДАННОЕ ПРИЛОЖЕНИЕ
slash = SlashCommand(client, sync_commands=True)

# ------------- СОЗДАЁМ ОБРАБОТКУ КОМАНДЫ С КОСОЙ ЧЕРТОЙ ЧЕРЕЗ СОЗДАННОЕ ПРИЛОЖЕНИЕ // КОНЕЦ


# ------------- РЕГИСТРИРУЕМ СОБЫТИЯ ПРИЛОЖЕНИЯ
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(process)d:%(thread)d: %(module)s:%(lineno)d: %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ------------- РЕГИСТРИРУЕМ СОБЫТИЯ ПРИЛОЖЕНИЯ // КОНЕЦ


# ------------- СОЗДАЁМ ШАБЛОН ДЛЯ ПЕРЕСЫЛКИ СООБЩЕНИЯ НА ВСЕ СЕРВЕРА
async def send_to_servers(*args, **kwargs):
    """
    send message to all connected servers to config.globalchannel channel, arguments as for channel.send()
    :param args:
    :param kwargs:
    :return:
    """
    logger.debug(f"Sending to servers {args} {kwargs}")
    for guild in client.guilds:
        if channel := discord.utils.get(guild.text_channels, name=config.globalchannel):
            try:
                await channel.send(*args, **kwargs)
            except discord.Forbidden as e:
                logger.warning(f"Failed to send message to {guild.name}: discord.Forbidden\n{e}")
            except discord.HTTPException as e:
                logger.warning(f"Failed to send message to {guild.name}: discord.HTTPException\n{e}")
            except Exception as e:
                logger.warning(f"Failed to send message to {guild.name}: {e}")


# ------------- СОЗДАЁМ ШАБЛОН ДЛЯ ПЕРЕСЫЛКИ СООБЩЕНИЯ НА ВСЕ СЕРВЕРА // КОНЕЦ


# ------------- КАКАЯ-ТО НЕПОНЯТНАЯ ШТУКА ᓚᘏᗢ
def guild_ids_for_slash():
    if config.environment_type == 'prod':
        return None
    else:
        return [guild.id for guild in client.guilds]


# ------------- КАКАЯ-ТО НЕПОНЯТНАЯ ШТУКА ᓚᘏᗢ // КОНЕЦ


# ------------- СОЗДАЁМ ШАБЛОН С ССЫЛКОЙ ДЛЯ ПОДКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ К СЕРВЕРУ
def get_invite_link(bot_id):
    return f'https://discord.com/oauth2/authorize?client_id={bot_id}&scope=bot%20applications.commands'  # noqa: E501


# ------------- СОЗДАЁМ ШАБЛОН С ССЫЛКОЙ ДЛЯ ПОДКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ К СЕРВЕРУ // КОНЕЦ


# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ PYTHON
@client.event
async def on_ready():
    client.sql_conn = await aiosqlite.connect(config.db_file_name)
    await client.sql_conn.execute('create table if not exists black_list (userid integer not null unique, '
                                  'add_timestamp text default current_timestamp, reason text, banner_id integer);')

    # Console Log // Выводим данные приложения в консоль Python
    logger.info(f'APP Username: {client.user} ')
    logger.info(f'Using token {config.token[0:2]}...{config.token[-3:-1]}')
    logger.info(f'Current env type: {config.environment_type}')
    logger.info(f'Using global channel {config.globalchannel}')
    logger.info('APP Client ID: {0.user.id} '.format(client))
    # Console Log // Выводим ссылку для подключения приложения к серверу в консоль Python
    logger.info(f'Link for connection: {get_invite_link(client.user.id)}')

    # Console Log // Выводим список серверов к которым подключено приложение в консоль Python
    logger.info('Servers connected to: ' + ''.join('"' + guild.name + '"; ' for guild in client.guilds))

    # Изменяем статус приложения
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Elite Dangerous'))

    # Отправляем сообщение в общий канал
    emStatusOn = discord.Embed(title='⚠ • ВНИМАНИЕ!', description='Приложение запущено', colour=0x90D400)
    emStatusOn.set_image(
        url="https://media.discordapp.net/attachments/682731260719661079/682731350922493952/ED1.gif")
    await send_to_servers(embed=emStatusOn, delete_after=13)


# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ PYTHON // КОНЕЦ


# ------------- РЕГИСТРИРУЕМ ОШИБКИ КОМАНД С КОСОЙ ЧЕРТОЙ И СООБЩАЕМ ОБ ЭТОМ ПОЛЬЗОВАТЕЛЯМ
@client.event
async def on_slash_command_error(ctx, error):
    logger.warning(
        f"An error occurred: {ctx.guild} / {ctx.author} / command: {ctx.name}; Error: {error}")
    if isinstance(error, discord.ext.commands.NotOwner):
        # Создаём информационное сообщение
        emSlashErrorNotOwner = discord.Embed(
            title='ВНИМАНИЕ!',
            description=ctx.author.mention + ', выполнение этой команды доступно только владельцу приложения',
            color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await ctx.send(embed=emSlashErrorNotOwner, delete_after=13)
        return

    await ctx.send(str(error), delete_after=13)


# ------------- РЕГИСТРИРУЕМ ОШИБКИ КОМАНД С КОСОЙ ЧЕРТОЙ И СООБЩАЕМ ОБ ЭТОМ ПОЛЬЗОВАТЕЛЯМ // КОНЕЦ


# ------------- ВЫВОДИМ ИСПОЛЬЗОВАНИЕ КОМАНД С КОСОЙ ЧЕРТОЙ В КОНСОЛЬ PYTHON
@client.event
async def on_slash_command(ctx):
    logger.info(f'Got slash command; {ctx.guild} / {ctx.author} / command: {ctx.name};'
                f' subcommand_name: {ctx.subcommand_name};'
                f' subcommand_group: {ctx.subcommand_group}; options: {ctx.data.get("options")}')


# ------------- ВЫВОДИМ ИСПОЛЬЗОВАНИЕ КОМАНД С КОСОЙ ЧЕРТОЙ В КОНСОЛЬ PYTHON // КОНЕЦ


# ------------- ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА
@client.event
async def on_message(message):
    # Игнорируем сообщения, отправленные этим приложением
    if message.author.id == client.user.id:
        return

    # Console Log // Выводим сообщения пользователей в консоль Python
    logger.info('Message: {0.guild} / #{0.channel} / {0.author}: {0.content}'.format(message))

    # Игнорируем сообщения в ЛС
    if isinstance(message.channel, discord.DMChannel):
        return

    # Игнорируем сообщения, отправленные не в забриджованный канал
    if message.channel.name != config.globalchannel:
        return

    # Игнорируем сообщения, отправленные другими приложениями
    if message.author.bot:
        return

    # Игнорируем сообщения с упоминанием
    if message.mentions or message.mention_everyone:
        await message.delete()
        await message.channel.send(
            'Сообщения, с упоминанием всех активных и неактивных пользователей, не пропускаются в '
            'общий чат', delete_after=13)
        return

    # Игнорируем сообщения с символом "@"
    if "@" in message.content:
        await message.delete()
        await message.channel.send('` ⚠ • ВНИМАНИЕ! ` Упс! Что-то пошло не так'.format(message), delete_after=13)
        return

    # Игнорируем сообщения, отправленные пользователем из чёрного списка
    if (await (await client.sql_conn.execute(
            'select count(*) from black_list where userid = ?;', [message.author.id])).fetchone())[0] == 1:
        await message.delete()
        await message.channel.send(
            'Сообщение пользователей из чёрного списка не допускаются к пересылке\n Вам по прежнему доступно '
            'использование команд приложения',
            delete_after=13)
        return

    # Создаём сообщение
    emGlobalMessage = discord.Embed(description=f" **{message.author.name}**: {message.content}", colour=0x2F3136)
    emGlobalMessage.set_footer(icon_url=message.guild.icon_url,
                               text=f"Сервер: {message.guild.name} // ID пользователя: {message.author.id}")
    
    # Проверяем расширение файлов
    for attachment in message.attachments:
        if attachment.filename.endswith(('bmp', 'jpeg', 'jpg', 'png', 'gif')):
            emGlobalMessage.set_image(url=attachment.url)
        else:
            await message.delete()
            await message.channel.send('К пересылке допускаются только файлы с расширениями `*.bmp`, `*.jpeg`, `*.jpg`, `*.png`, `*.gif`.',
                                       delete_after=13)
            return

    # Удаляем сообщение, отправленное пользователем
    await message.delete()

    # Отправляем сообщение
    await send_to_servers(embed=emGlobalMessage)


# ------------- ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА // КОНЕЦ


# ------------- КОМАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ
@slash.slash(name="ping",
             description="Проверить состояние приложения",
             guild_ids=guild_ids_for_slash())
async def ping(ctx):
    # Создаём информационное сообщение
    emPing = discord.Embed(
        title='⚠ • ВНИМАНИЕ!',
        description=f'Latency {round(client.latency * 100, 1)} ms',
        colour=0x90D400)
    # Отправляем информационное сообщение и удаляем его через 13 секунд
    await ctx.send(embed=emPing, delete_after=13)


# ------------- КОМАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ // КОНЕЦ


# ------------- КОМАНДА ПОМОЩИ
@slash.slash(name="help",
             description="Показать информацию о командах используемых приложением",
             guild_ids=guild_ids_for_slash())
async def help_(ctx):
    # Создаём информационное сообщение
    emHelp = discord.Embed(
        title='ПОМОЩЬ',
        description='```Некоторые из ниже указанных команд могут не работать или для их '
                    'использования могут требоваться определённые разрешения.```',
        colour=0x2F3136)
    emHelp.add_field(name='Список команд',
                     value='`ping` - Проверить состояние приложения.\n`help` - Показать информацию о командах '
                           'используемых приложением.\n`information` - Показать информацию о приложение.\n`clear` - '
                           'Удалить сто последних сообщений на канале.\n`bluadd` - Записать пользователя в чёрный '
                           'список.\n`bluremove` - Стереть пользователя из чёрного списка.\n`serverslist` - Показать '
                           'список серверов, к которым подключено приложение.\n`serversleave` - Отключить приложение '
                           'от указанного сервера.\n`setup` - Создать канала для приёма и передачи сообщений.')
    emHelp.add_field(name='Дополнительная информация',
                     value='Дополнительную информацию о приложение можно запросить командой `information`',
                     inline=False)
    # Отправляем информационное сообщение и удаляем его через 60 секунд
    await ctx.send(embed=emHelp, delete_after=60)


# ------------- КОММАНДА ПОМОЩИ // КОНЕЦ


# ------------- КОМАНДА ОТОБРАЖЕНИЯ ИНФОРМАЦИИ О ПРИЛОЖЕНИИ
@slash.slash(name="information",
             description="Показать информацию о приложение",
             guild_ids=guild_ids_for_slash())
async def information(ctx):
    # Создаём сообщение
    emInformation = discord.Embed(title='ИНФОРМАЦИЯ',
                                  description=config.client_full_description.format(
                                      invite_link=get_invite_link(client.user.id)),
                                  colour=0x2F3136)
    emInformation.add_field(name='Разработчики', value='• <@420130693696323585>\n• <@665018860587450388>')
    emInformation.add_field(name='Благодарности', value='• <@478527700710195203>')
    # emInformation.add_field(name='Список серверов', value="".join(guild.name + '\n' for guild in client.guilds))
    emInformation.set_footer(text=client.user.name)
    # Отправляем сообщение и удаляем его через 60 секунд
    await ctx.send(embed=emInformation, delete_after=60)


# ------------- КОМАНДА ОТОБРАЖЕНИЯ ИФОРМАЦИИ О ПРИЛОЖЕНИЕ // КОНЕЦ


# ------------- КОМАНДА ЗАПИСИ ПОЛЬЗОВАТЕЛЯ В ЧЁРНЫЙ СПИСОК
@commands.is_owner()
@slash.subcommand(
    base='blacklist',
    name='add',
    guild_ids=guild_ids_for_slash(),
    base_desc='Действия с чёрным списком',
    description='Внести пользователя в чёрный список приложения',
    options=[
        create_option(
            name='userid',
            description='userid to ban',
            option_type=6,
            required=True),
        create_option(
            name='reason',
            description='reason to ban',
            option_type=3,
            required=False
        )])
async def blacklist_add(ctx, userid, reason=None):
    is_userid_banned = bool((await (await client.sql_conn.execute('select count(*) from black_list where userid = ?;',
                                                                  [userid])).fetchone())[0])
    if is_userid_banned:
        await ctx.send('Этот пользователь уже есть в чёрном списке приложения', delete_after=13)
        return

    await client.sql_conn.execute('insert into black_list (userid, reason, banner_id)'
                                  ' values (?, ?, ?);', [userid, reason, ctx.author.id])
    await client.sql_conn.commit()

    # Создаём информационное сообщение
    emBlackListAdd = discord.Embed(
        title='⚠ • ВНИМАНИЕ!',
        description=f'Пользователь с ID {userid} занесён в чёрный список приложения',
        color=0xd40000)
    await ctx.send(embed=emBlackListAdd, delete_after=13)


# ------------- КОМАНДА ЗАПИСИ ПОЛЬЗОВАТЕЛЯ В ЧЁРНЫЙ СПИСОК // КОНЕЦ


# ------------- КОМАНДА ОТОБРАЖЕНИЯ ЧЁРНОГО СПИСОКА
# Показ содержимого чёрного списка
# TODO: Нормальное форматирование таблицы
@slash.subcommand(
    base='blacklist',
    name='show',
    guild_ids=guild_ids_for_slash(),
    base_desc='Действия с чёрным списком',
    description='Показать чёрный список'
)
async def blacklist_show(ctx):
    full_list = await client.sql_conn.execute('select userid, add_timestamp, reason, banner_id from black_list')
    table = ['userid    add_timestamp   reason  banner_id']
    for user in (await full_list.fetchall()):
        table.append('   '.join([str(item).center(5, ' ') for item in user]))
    table = "```" + '\n'.join(table) + "```"
    await ctx.send(table, delete_after=13)


# ------------- КОМАНДА ОТОБРАЖЕНИЯ ЧЁРНОГО СПИСОКА // КОНЕЦ


# ------------- КОМАНДА УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ ИЗ ЧЁРНОГО СПИСКА
@commands.is_owner()
@slash.subcommand(
    base='blacklist',
    name='remove',
    guild_ids=guild_ids_for_slash(),
    base_desc='Действия с чёрным списком',
    description='Удалить пользователя из чёрного списка приложения',
    options=[
        create_option(
            name='userid',
            description='userid to unban',
            option_type=6,
            required=True)
    ])
async def blacklist_remove(ctx, userid):
    is_userid_banned = bool((await (await client.sql_conn.execute('select count(*) from black_list where userid = ?;',
                                                                  [userid])).fetchone())[0])
    if not is_userid_banned:
        await ctx.send('Этот пользователь не находится чёрном списке приложения', delete_after=13)
        return

    await client.sql_conn.execute('delete from black_list where userid = ?', [userid])
    await client.sql_conn.commit()
    await ctx.send('Пользователь успешно удалён из чёрного списка', delete_after=13)


# ------------- КОМАНДА УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ ИЗ ЧЁРНОГО СПИСКА // КОНЕЦ


# ------------- КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ
# Команду может выполнить только владелец приложения
# @commands.is_owner()
@slash.slash(name="servers_list",
             description="Вывести список серверов, где присутствует бот",
             guild_ids=guild_ids_for_slash())
async def servers_list(ctx):
    # Создаём сообщение
    emServers = discord.Embed(title='СПИСОК СЕРВЕРОВ',
                              description='Список серверов, к которым подключено приложение',
                              colour=0x2F3136)
    emServers.add_field(
        name='Список серверов',
        value="".join(guild.name + f' (ID:{guild.id})\n' for guild in client.guilds))
    emServers.set_footer(text=' ' + client.user.name + ' ')
    # Отправляем сообщение и удаляем его через 60 секунд
    await ctx.send(embed=emServers, delete_after=60)


# ------------- КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ // КОНЕЦ


# ------------- КОМАНДА ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ ОТ СЕРВЕРА
@slash.slash(name="server_leave",
             description="Покинуть сервер",
             guild_ids=guild_ids_for_slash())
# Команду может выполнить только владелец приложения
@commands.is_owner()
async def server_leave(ctx, id_to_leave: str):  # TODO: test it
    if guild_to_leave := client.get_guild(int(id_to_leave)) is None:  # type: ignore
        await ctx.send('Сервер с указанным ID не найден', delete_after=13)
        return
    await guild_to_leave.leave()
    await ctx.send('Сервер с указанным ID успешно покинут', delete_after=13)


# ------------- КОМАНДА ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ ОТ СЕРВЕРА // КОНЕЦ


# ------------- КОМАНДА СОЗДАНИЯ КАНАЛА ДЛЯ ПРИЁМА И ОТПРАВКИ СООБЩЕНИЙ
@slash.slash(name="setup",
             description="Создать канала для приёма и передачи сообщений",
             guild_ids=guild_ids_for_slash())
# Команду может выполнить только пользователь, с ролью администратор
async def setup(ctx):
    if isinstance(ctx.author, discord.User):  # проверка, не в лс ли идёт команда
        await ctx.send('Использование этой команды допускается только на серверах, не в личных сообщениях',
                       delete_after=13)
        return

    if ctx.author.guild_permissions.administrator:  # проверка наличия админских прав на сервере у выполняющего
        guild = ctx.guild
        if discord.utils.get(guild.text_channels,
                             name=config.globalchannel) is None:  # проверка на наличие нужного канала
            await guild.create_text_channel(name=config.globalchannel)
            await ctx.send(
                f'Канал {config.globalchannel} успешно создан и будет использоваться для пересылки сообщений',
                delete_after=13)
        else:
            await ctx.send(f'У вас уже есть подходящий канал: {config.globalchannel}', delete_after=13)
    else:
        await ctx.send('Для выполнения этой команды вам необходимо обладать правами администратора на этом сервере',
                       delete_after=13)

        
# ------------- КОМАНДА СОЗДАНИЯ КАНАЛА ДЛЯ ПРИЁМА И ОТПРАВКИ СООБЩЕНИЙ // КОНЕЦ


# ------------- КАКАЯ-ТО НЕПОНЯТНАЯ ШТУКА ᓚᘏᗢ
async def shutdown_async():
    logger.info('Executing shutdown_async')
    await send_to_servers(content='Выключение', delete_after=13)
    await client.change_presence(status=discord.Status.offline)
    await client.close()


def shutdown(sig, frame):
    logger.info(f'Shutting down by signal: {sig}')
    asyncio.create_task(shutdown_async())


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)


# ------------- КАКАЯ-ТО НЕПОНЯТНАЯ ШТУКА ᓚᘏᗢ // КОНЕЦ


# Генерируемый токен при создание приложения на странице https://discord.com/developers/applications, необходимый для подключения к серверу
# Прописывается в config.py
client.run(config.token)

# Console Log // Выводим сообщение об отключение приложения в консоль Python
logger.info('Exited. You can safely kill the process')


# ------------- СОЗДАЁМ ПРИЛОЖЕНИЕ И НАЗЫВАЕМ ЕГО CLIENT  // КОНЕЦ
