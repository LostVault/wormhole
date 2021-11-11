# -*- coding: utf-8 -*-
# ------------- ИМПОРТ МОДУЛЕЙ
import asyncio  # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ
import logging  # Импортируем модуль логирования
import time
import typing

import aiosqlite  # Импортируем модуль работы с базами SQLite
import discord  # Импортируем основной модуль
from discord.ext import commands  # Импортируем команды из модуля discord.ext
from discord_slash import SlashCommand  # Импортируем модуль команд с косой чертой (slash)
from discord_slash.utils.manage_commands import create_option

import config  # Импортируем настройки приложения
import signal  # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ

sql_conn: aiosqlite.Connection # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ
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

# Словарь для применения cooldown'a
cooldown: dict[int, int] = dict()


def handle_cooldown(user_id: int) -> typing.Union[bool, int]:
    """Принимает айдишник пользователя на вход и возвращает True если кд для пользователя кончился и кол-во секунд
    до конца кд, если не кончился
    Также обновляет кд для указанного пользователя
    TODO: при длительной эксплуатации, размер cooldown может достичь больших размеров

    :param user_id: ID пользователя для определения состояния кд и возможности отправки сообщения на основе кд
    :return: Может ли пользователь отправить сообщение
    """

    global cooldown
    # Значением в cooldown является время в unix формате, когда пользователю можно будет отправить следующее сообщение

    if user_id in cooldown:
        if time.time() > cooldown[user_id]:
            # кд для пользователя кончился
            cooldown[user_id] = int(time.time()) + config.cooldown  # Обновление КД для пользователя
            return True

        else:
            # кд не кончился
            return int(cooldown[user_id] - time.time())

    else:
        # Пользователя нет в КД списке, добавим туда и разрешим отправку сейчас
        cooldown[user_id] = int(time.time()) + config.cooldown
        return True


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


# ------------- TODO: Указать комментарий, описывающий данный блок кода ᓚᘏᗢ
async def fetch_or_get_user(userid: int, suppress=True):
    user = client.get_user(userid)
    if user is None:
        try:
            user = await client.fetch_user(userid)

        except discord.NotFound:
            if not suppress:
                raise
            user = None

    return user


async def get_owners() -> list:
    owners = list()
    appinfo = await client.application_info()

    if appinfo.team is not None:
        for team_member in appinfo.team.members:
            owners.append(team_member.id)
    else:
        owners.append(appinfo.owner.id)  # team is also user, yes o_0

    owners = owners + config.additional_owners
    logger.debug('Owners: ' + ' '.join(str(owner) for owner in owners))
    return owners


async def raise_for_owner(ctx):
    if ctx.author.id not in await get_owners():
        raise discord.ext.commands.NotOwner


# ------------- ᓚᘏᗢ


# ------------- TODO: Указать комментарий описывающий данный блок кода ᓚᘏᗢ
def guild_ids_for_slash():
    if config.environment_type == 'prod':
        return None
    else:
        return [guild.id for guild in client.guilds]


# ------------- ᓚᘏᗢ


# ------------- СОЗДАЁМ ШАБЛОН С ССЫЛКОЙ ДЛЯ ПОДКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ К СЕРВЕРУ
def get_invite_link(bot_id):
    return f'https://discord.com/oauth2/authorize?client_id={bot_id}&scope=bot%20applications.commands'  # noqa: E501


# ------------- СОЗДАЁМ ШАБЛОН С ССЫЛКОЙ ДЛЯ ПОДКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ К СЕРВЕРУ // КОНЕЦ


# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ PYTHON
@client.event
async def on_ready():
    global sql_conn
    sql_conn = await aiosqlite.connect(config.db_file_name)
    await sql_conn.execute('create table if not exists black_list (userid integer not null unique, '
                           'add_timestamp text default current_timestamp, reason text, banner_id integer);')

    # Console Log // Выводим данные приложения в консоль Python
    logger.info(f'APP Username: {client.user} ')
    logger.info(f'Using token {config.token[0:2]}...{config.token[-3:-1]}')
    logger.info(f'Current env type: {config.environment_type}')
    logger.info(f'Using global channel: {config.globalchannel}')
    logger.info('APP Client ID: {0.user.id} '.format(client))
    # Console Log // Выводим ссылку для подключения приложения к серверу в консоль Python
    logger.info(f'Link for connection: {get_invite_link(client.user.id)}')

    # Console Log // Выводим список серверов к которым подключено приложение в консоль Python
    logger.info('Servers connected to: ' + ''.join('"' + guild.name + '"; ' for guild in client.guilds))

    # Изменяем статус приложения
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Elite Dangerous'))

    # Создаём информационное сообщение
    emStatusOn = discord.Embed(title='⚠ • ВНИМАНИЕ!', description='```Приложение запущено.```', color=0x90D400)
    emStatusOn.set_image(url="https://media.discordapp.net/attachments/682731260719661079/682731350922493952/ED1.gif")
    emStatusOn.set_footer(text=client.user.name)
    # Отправляем информационное сообщение и удаляем его через 13 секунд
    await send_to_servers(embed=emStatusOn, delete_after=13)


# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ PYTHON // КОНЕЦ


# ------------- ОПОВЕЩЕНИЕ О ПОДКЛЮЧЕНИЕ/ОТКЛЮЧЕНИЕ ПРИЛОЖЕНИЯ К СЕРВЕРУ
@client.event
async def on_guild_join(guild):
    logger.info(f'Joining to "{guild.name}" guild')
    # Создаём информационное сообщение
    emAppJoinNewServer = discord.Embed(title='⚠ • ВНИМАНИЕ!', description=f'```Приложение было подключено к новому '
                                                                          f'серверу "{guild.name}"!```',
                                       color=0x90D400)
    emAppJoinNewServer.set_thumbnail(url=guild.icon_url)
    emAppJoinNewServer.set_footer(text=client.user.name)
    # Отправляем информационное сообщение и удаляем его через 60 секунд
    await send_to_servers(embed=emAppJoinNewServer)


@client.event
async def on_guild_remove(guild):
    logger.info(f'Leaving "{guild.name}"')
    # Создаём информационное сообщение TODO: Возможно нужно изменить сообщение на ```Приложение отключено от сервера
    #  "{guild.name}" и больше не учавствовать в обмене сообщениями с ним.```
    emAppDisconnectServer = discord.Embed(title='❌ • ВНИМАНИЕ!', description=f'```Сервер "{guild.name}" был отключён '
                                                                             f'от системы обмена сообщениями.```',
                                          color=0xd40000)
    emAppDisconnectServer.set_footer(text=client.user.name)
    # Отправляем информационное сообщение и удаляем его через 60 секунд
    await send_to_servers(embed=emAppDisconnectServer)


# ------------- ОПОВЕЩЕНИЕ О ПОДКЛЮЧЕНИЕ/ОТКЛЮЧЕНИЕ ПРИЛОЖЕНИЯ К СЕРВЕРУ // КОНЕЦ


# ------------- РЕГИСТРИРУЕМ ОШИБКИ КОМАНД С КОСОЙ ЧЕРТОЙ И СООБЩАЕМ ОБ ЭТОМ ПОЛЬЗОВАТЕЛЯМ
@client.event
async def on_slash_command_error(ctx, error):
    logger.warning(
        f"An error occurred: {ctx.guild} / {ctx.author} / command: {ctx.name}; Error: {error}", exc_info=error)
    if isinstance(error, discord.ext.commands.NotOwner):
        # Создаём информационное сообщение
        emSlashErrorNotOwner = discord.Embed(title='❌ • ВНИМАНИЕ!',
                                             description='```' + ctx.author.mention + ', выполнение этой команды '
                                                                                      'доступно только владельцу '
                                                                                      'приложения.```',
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
        # Создаём информационное сообщение
        emFilterGlobalChatEveryone = discord.Embed(title='❌ • ВНИМАНИЕ!', description='```Сообщения с упоминанием '
                                                                                      'всех активных и неактивных '
                                                                                      'пользователей, не пропускаются '
                                                                                      'в глобальный чат.```',
                                                   color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=emFilterGlobalChatEveryone, delete_after=13)
        return

    # Игнорируем сообщения с символом "@"
    if "@" in message.content:
        await message.delete()
        # Создаём информационное сообщение
        emFilterGlobalChatSymbol = discord.Embed(title='❌ • ВНИМАНИЕ!', description='```Сообщения с символом "@" не '
                                                                                    'пропускаются в глобальный '
                                                                                    'чат.```', color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=emFilterGlobalChatSymbol, delete_after=13)
        return

    # Игнорируем сообщения, отправленные пользователем из чёрного списка
    if (await (await sql_conn.execute(
            'select count(*) from black_list where userid = ?;', [message.author.id])).fetchone())[0] == 1:
        await message.delete()
        # Создаём информационное сообщение
        emFilterGlobalChatBlackList = discord.Embed(title='❌ • ВНИМАНИЕ!', description='```Сообщение пользователей из '
                                                                                       'чёрного списка, '
                                                                                       'не пропускаются в глобальный '
                                                                                       'чат.\n Вам по прежнему '
                                                                                       'доступно использование команд '
                                                                                       'приложения.```',
                                                    color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=emFilterGlobalChatBlackList, delete_after=13)
        return

    # Игнорируем сообщения меньше 3 символов
    # TODO: Возможно параметр сколько символом считать коротким сообщением можно вывести в Конфиг
    if len(message.clean_content) < 3:
        await message.delete()
        # Создаём информационное сообщение
        emFilterGlobalChatShortMessages = discord.Embed(title='❌ • ВНИМАНИЕ!',
                                                        description='```Сообщения длиной менее '
                                                                    '3 символов не пропускаются'
                                                                    ' в глобальный чат.```',
                                                        color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=emFilterGlobalChatShortMessages, delete_after=13)
        return

    kd_status = handle_cooldown(message.author.id)
    if isinstance(kd_status, int):
        kdWarnEmbed = discord.Embed(title='КД', text=f'Попробуйте через {kd_status}')
        await message.delete()
        await message.channel.send(embed=kdWarnEmbed, delete_after=13)
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
            # Создаём информационное сообщение
            emFilterGlobalChatFormatFiles = discord.Embed(title='❌ • ВНИМАНИЕ!', description='```Файлы с расширениями '
                                                                                             '*.bmp, *.jpeg, *.jpg, '
                                                                                             '*.png, *.gif, '
                                                                                             'не пропускаются в '
                                                                                             'глобальный чат.```',
                                                          color=0xd40000)
            # Отправляем информационное сообщение и удаляем его через 13 секунд
            await message.channel.send(embed=emFilterGlobalChatFormatFiles, delete_after=13)
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


# ------------- КОМАНДА ОТОБРАЖЕНИЯ ИНФОРМАЦИИ О ПРИЛОЖЕНИИ
@slash.slash(name="information",
             description="Показать информацию о приложение",
             guild_ids=guild_ids_for_slash())
async def information(ctx):
    # Создаём сообщение
    emInformation = discord.Embed(title='ИНФОРМАЦИЯ', description=config.client_full_description.format(
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
@slash.subcommand(
    base='blacklist',
    name='add',
    guild_ids=guild_ids_for_slash(),
    base_desc='Действия с чёрным списком',
    description='Внести пользователя в чёрный список приложения',
    options=[
        create_option(
            name='user',
            description='userid to ban',
            option_type=6,
            required=True),
        create_option(
            name='reason',
            description='reason to ban',
            option_type=3,
            required=False
        )])
async def blacklist_add(ctx, user, reason=None):
    await raise_for_owner(ctx)

    if isinstance(user, str):
        userid = int(user)
    else:
        userid = user.id  # Probably discord.Member or discord.User, anyway, will raise AttributeError if I'm wrong

    is_userid_banned = bool((await (await sql_conn.execute('select count(*) from black_list where userid = ?;',
                                                           [userid])).fetchone())[0])
    if is_userid_banned:
        await ctx.send('Этот пользователь уже есть в чёрном списке приложения', delete_after=13)
        return

    await sql_conn.execute('insert into black_list (userid, reason, banner_id)'
                           ' values (?, ?, ?);', [userid, reason, ctx.author.id])
    await sql_conn.commit()

    # Создаём информационное сообщение
    # TODO: Добавить имя пользователя по мимо его ID
    # TODO: Возможно это сообщение надо отправлять в глобальный чат
    emBlackListAdd = discord.Embed(title='⚠ • ВНИМАНИЕ!', description=f'```Пользователь с ID {userid} занесён в '
                                                                      f'чёрный список приложения```', color=0x90D400)
    # Отправляем информационное сообщение и удаляем его через 13 секунд
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
    full_list = await sql_conn.execute('select userid, add_timestamp, reason, banner_id from black_list')
    table = ['username  userid    add_timestamp   reason  banner_id']
    for user in (await full_list.fetchall()):
        username = await fetch_or_get_user(int(user[0]))
        if isinstance(username, discord.User):
            username = username.name

        table.append(str(username) + '   ' + '   '.join([str(item).center(5, ' ') for item in user]))
    table = "```" + '\n'.join(table) + "```"
    await ctx.send(table, delete_after=13)


# ------------- КОМАНДА ОТОБРАЖЕНИЯ ЧЁРНОГО СПИСОКА // КОНЕЦ


# ------------- КОМАНДА УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ ИЗ ЧЁРНОГО СПИСКА
@slash.subcommand(
    base='blacklist',
    name='remove',
    guild_ids=guild_ids_for_slash(),
    base_desc='Действия с чёрным списком',
    description='Удалить пользователя из чёрного списка приложения',
    options=[
        create_option(
            name='user',
            description='Упомянуть пользователя или указать его ID',
            option_type=6,
            required=True)
    ])
async def blacklist_remove(ctx, user):
    await raise_for_owner(ctx)

    if isinstance(user, str):
        userid = int(user)
    else:
        userid = user.id  # Probably discord.Member or discord.User, anyway, will raise AttributeError if I'm wrong

    is_userid_banned = bool((await (await sql_conn.execute('select count(*) from black_list where userid = ?;',
                                                           [userid])).fetchone())[0])
    if not is_userid_banned:
        # Создаём информационное сообщение
        # TODO: Добавить в сообщение имя пользователя и ID
        emBlackListRemoveNoUser = discord.Embed(title='⚠ • ВНИМАНИЕ!', description=f'```Этот пользователь не '
                                                                                   f'находится чёрном списке '
                                                                                   f'приложения.```', color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await ctx.send(embed=emBlackListRemoveNoUser, delete_after=13)
        return

    await sql_conn.execute('delete from black_list where userid = ?', [userid])
    await sql_conn.commit()
    # Создаём информационное сообщение
    # TODO: Добавить в сообщение имя пользователя и ID
    # TODO: Возможно это сообщение надо отправлять в глобальный чат
    emBlackListRemoveUser = discord.Embed(title='⚠ • ВНИМАНИЕ!', description=f'```Пользователь успешно удалён из '
                                                                             f'чёрного списка приложения.```',
                                          color=0x90D400)
    # Отправляем информационное сообщение и удаляем его через 13 секунд
    await ctx.send(embed=emBlackListRemoveUser, delete_after=13)


# ------------- КОМАНДА УДАЛЕНИЯ ПОЛЬЗОВАТЕЛЯ ИЗ ЧЁРНОГО СПИСКА // КОНЕЦ


# ------------- КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ
@slash.subcommand(
    base='servers',
    name='show',
    guild_ids=guild_ids_for_slash(),
    base_desc='Действия с серверами',
    description='Вывести список серверов, к которым подключено приложение'
)
async def servers_show(ctx):
    # Создаём сообщение
    emServers = discord.Embed(title='СПИСОК СЕРВЕРОВ', description='Список серверов, к которым подключено приложение. '
                                                                   'Данный список не относится к белому списку '
                                                                   'серверов которым разрешено обмениваться '
                                                                   'сообщениями.', colour=0x2F3136)
    emServers.add_field(name='Список серверов', value="".join(
        guild.name + f' (ID:{guild.id})\n' for guild in client.guilds)
                        )

    emServers.set_footer(text=' ' + client.user.name + ' ')
    # Отправляем сообщение и удаляем его через 60 секунд
    await ctx.send(embed=emServers, delete_after=60)


# ------------- КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ // КОНЕЦ


# ------------- КОМАНДА ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ ОТ СЕРВЕРА
@slash.subcommand(
    base='servers',
    name='leave',
    guild_ids=guild_ids_for_slash(),
    base_desc='Действия серверами',
    description='Отключить приложение от сервера'
)
# Команду может выполнить только владелец приложения
async def server_leave(ctx, id_to_leave: str):  # TODO: test it
    await raise_for_owner(ctx)

    if (guild_to_leave := await client.fetch_guild(int(id_to_leave))) is None:  # type: ignore
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
        if discord.utils.get(guild.text_channels, name=config.globalchannel) is None:  # проверка на наличие нужного канала
            # Выдаём права нужные для работы приложения (manage_channels=True, manage_permissions=True - Требуеют права администратора на сервере)
            overwrites = {
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, embed_links=True, attach_files=True)
            }

            await guild.create_text_channel(name=config.globalchannel, topic=config.setup_globalchannel_description, overwrites=overwrites, slowmode_delay=config.setup_globalchannel_cooldown, reason='Создание канала для Wormhole.')
            await ctx.send(
                f'Канал {config.globalchannel} успешно создан и будет использоваться для пересылки сообщений',
                delete_after=13)
        else:
            await ctx.send(f'У вас уже есть подходящий канал: {config.globalchannel}', delete_after=13)
    else:
        await ctx.send('Для выполнения этой команды вам необходимо обладать правами администратора на этом сервере',
                       delete_after=13)


# ------------- КОМАНДА СОЗДАНИЯ КАНАЛА ДЛЯ ПРИЁМА И ОТПРАВКИ СООБЩЕНИЙ // КОНЕЦ


# ------------- КОМАНДА ВЫВОДА ПРАВИЛ ГЛОБАЛЬНОГО КАНАЛА
@slash.slash(name="rules",
             description="Показать правила использования глобального канала",
             guild_ids=guild_ids_for_slash()
             )
async def rules_cmd(ctx):
    emRules = discord.Embed(title='ПРАВИЛА', description=config.globalchannel_rules, colour=0x2F3136)
    await ctx.send(embed=emRules, delete_after=60)


# ------------- КОМАНДА ВЫВОДА ПРАВИЛ ГЛОБАЛЬНОГО КАНАЛА // КОНЕЦ

@slash.slash(
    name='moderators',
    description='Показать модераторов глобального канала',
    guild_ids=guild_ids_for_slash()
)
async def rules_cmd(ctx):
    moderators = str()
    for moderator_id in await get_owners():
        moderator_user = await fetch_or_get_user(moderator_id, suppress=False)
        moderators = f'{moderators}{moderator_user.name}#{moderator_user.discriminator} <@{moderator_user.id}>\n'

    emModers = discord.Embed(
        title='Модераторы',
        description=moderators,
    )
    await ctx.send(embed=emModers, delete_after=60)


# ------------- TODO: Указать комментарий, описывающий данный блок кода ᓚᘏᗢ
async def shutdown_async():
    logger.info('Executing shutdown_async')
    # await send_to_servers(content='Выключение', delete_after=13)
    await client.change_presence(status=discord.Status.offline)
    await client.close()


def shutdown(sig, frame):
    logger.info(f'Shutting down by signal: {sig}')
    asyncio.create_task(shutdown_async())


signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

# ------------- ᓚᘏᗢ


# Генерируемый токен при создание приложения на странице https://discord.com/developers/applications, необходимый для
# подключения к серверу Прописывается в config.py
client.run(config.token)

# Console Log // Выводим сообщение об отключение приложения в консоль Python
logger.info('Exited. You can safely kill the process')

# ------------- СОЗДАЁМ ПРИЛОЖЕНИЕ И НАЗЫВАЕМ ЕГО CLIENT  // КОНЕЦ
