# -*- coding: utf-8 -*-

# region •••••••••••••••• ИМПОРТ МОДУЛЕЙ
import discord  # Импортируем библиотеку работы с Discord API (Application Programming Interface)
from discord.commands import Option  # Импортируем библиотеку опций для глобальных комманд
from discord.commands import permissions  # Импортируем библиотеку разрешений для глобальных комманд

# ••••••••••••••••

import time  # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ
import typing  # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ
import logging  # Импортируем модуль логирования
import asyncio  # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ
import aiosqlite  # Импортируем модуль работы с базами SQLite

# ••••••••••••••••

import config  # Импортируем настройки приложения
import signal  # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ

sql_conn: aiosqlite.Connection # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ


# endregion ••••••••••••• ИМПОРТ МОДУЛЕЙ // КОНЕЦ

# •••••• 😈 •••••• СОЗДАЁМ ПРИЛОЖЕНИЕ И НАЗЫВАЕМ ЕГО CLIENT
client = discord.Bot(description=config.app_short_description, command_prefix=None, help_command=None)


# region •••••••••••••••• ПРОВЕРЯЕМ В КАКОМ ОКРУЖЕНИЕ ЗАПУЩЕНО ПРИЛОЖЕНИЕ
def guild_ids_for_slash():
    if config.environment_type == 'prod':
        return None
    else:
        return [guild.id for guild in client.guilds]


# endregion ••••••••••••• ПРОВЕРЯЕМ В КАКОМ ОКРУЖЕНИЕ ЗАПУЩЕНО ПРИЛОЖЕНИЕ // КОНЕЦ

# region •••••••••••••••• ПРОВЕРЯЕМ ПОЛЬЗОВАТЕЛЯ НА COOLDOWNN
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
        if int(time.time()) > cooldown[user_id]:
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

# endregion ••••••••••••• ПРОВЕРЯЕМ ПОЛЬЗОВАТЕЛЯ НА COOLDOWNN // КОНЕЦ

# ••••••••••••••••


# region •••••••••••••••• СОЗДАЁМ ШАБЛОН С ССЫЛКОЙ ДЛЯ ПОДКЛЮЧЕНИЯ К СЕРВЕРУ
def get_invite_link(bot_id):
    return f'https://discord.com/oauth2/authorize?client_id={bot_id}&scope=bot%20applications.commands'


# endregion ••••••••••••• СОЗДАЁМ ШАБЛОН С ССЫЛКОЙ ДЛЯ ПОДКЛЮЧЕНИЯ К СЕРВЕРУ


# region •••••••••••••••• СОЗДАЁМ ШАБЛОН ДЛЯ ПЕРЕСЫЛКИ СООБЩЕНИЯ НА ВСЕ СЕРВЕРА
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


# endregion ••••••••••••• СОЗДАЁМ ШАБЛОН ДЛЯ ПЕРЕСЫЛКИ СООБЩЕНИЯ НА ВСЕ СЕРВЕРА // КОНЕЦ


# ••••••••••••••••


# region •••••••••••••••• ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ
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
    await client.change_presence(status=discord.Status.online, activity=discord.Game(config.app_status_game))

    # Создаём информационное сообщение
    emStatusOn = discord.Embed(title='⚠ • ВНИМАНИЕ!', description='```Приложение запущено.```', color=0x90D400)
    emStatusOn.set_image(url="https://media.discordapp.net/attachments/682731260719661079/682731350922493952/ED1.gif")
    emStatusOn.set_footer(text=client.user.name)
    # Отправляем информационное сообщение и удаляем его через 13 секунд
    await send_to_servers(embed=emStatusOn, delete_after=13)


# endregion ••••••••••••• ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ // КОНЕЦ


# region •••••••••••••••• ВЫВОДИМ СОБЫТИЯ ПРИЛОЖЕНИЯ В КОНСОЛЬ
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(process)d:%(thread)d: %(module)s:%(lineno)d: %(message)s')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# endregion ••••••••••••• РЕГИСТРИРУЕМ СОБЫТИЯ ПРИЛОЖЕНИЯ В КОНСОЛЬ // КОНЕЦ


# ••••••••••••••••


# region •••••••••••••••• TODO: Указать комментарий, описывающий данный блок кода ᓚᘏᗢ
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


# endregion ••••••••••••• ᓚᘏᗢ


# region •••••••••••••••• ОПОВЕЩЕНИЕ О ПОДКЛЮЧЕНИЕ/ОТКЛЮЧЕНИЕ ПРИЛОЖЕНИЯ К СЕРВЕРУ
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


# endregion ••••••••••••• ОПОВЕЩЕНИЕ О ПОДКЛЮЧЕНИЕ/ОТКЛЮЧЕНИЕ ПРИЛОЖЕНИЯ К СЕРВЕРУ // КОНЕЦ


# region •••••••••••••••• ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА
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

    # Игнорируем сообщения, отправленные не в глобальном канале канал
    if message.channel.name != config.globalchannel:
        return

    # Игнорируем сообщения, отправленные другими приложениями
    if message.author.bot:
        return

    # Игнорируем сообщения с упоминанием
    if message.mentions or message.mention_everyone:
        # Удаляем сообщение пользователя
        await message.delete()
        # Создаём информационное сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!', description='```Сообщения с упоминанием всех активных и неактивных пользователей, не пропускаются в глобальный чат.```', color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=embed, delete_after=13)
        return

    # Игнорируем сообщения с символом "@"
    if "@" in message.content:
        # Удаляем сообщение пользователя
        await message.delete()
        # Создаём информационное сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!', description='```Сообщения с символом "@" не пропускаются в глобальный чат.```', color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=embed, delete_after=13)
        return

    # Игнорируем сообщения, отправленные пользователем из чёрного списка
    if (await (await sql_conn.execute('select count(*) from black_list where userid = ?;', [message.author.id])).fetchone())[0] == 1:
        # Удаляем сообщение пользователя
        await message.delete()
        # Создаём информационное сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!', description='```Сообщение пользователей из чёрного списка, не пропускаются в глобальный чат.\nВам по прежнему доступно использование команд приложения.```', color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=embed, delete_after=13)
        return

    # Проверяйем минимальное количество символов разрешённое к отправке
    if len(message.clean_content) < config.shortmessages:
        # Удаляем сообщение пользователя
        await message.delete()
        # Создаём информационное сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!', description=f'```Сообщения длиной менее {config.shortmessages} символов не пропускаются в глобальный чат.```', color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=embed, delete_after=13)
        return

    # Проверяйем время с последнего сообщения отправленное пользователем
    kd_status = handle_cooldown(message.author.id)
    # if isinstance(kd_status, int):
    if type(kd_status) is int:
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!', description=f'```С последнего сообщения прошло слишком мало времени, попробуйте отправить сообщение повторно через {kd_status} секунд.```', color=0xd40000)
        # Удаляем сообщение пользователя
        await message.delete()
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=embed, delete_after=13)
        return

    # Игнорируем сообщения с ссылками не из белого списка
    splitted_message: list = message.content.lower().split(' ')
    for message_fragment in splitted_message:
        if 'http://' in message_fragment or 'https://' in message_fragment:
            # probably link
            splited_link = message_fragment.split('/')
            domain = splited_link[2]
            if domain in config.whitelistlinks:
                pass

            else:
                # Удаляем сообщение пользователя
                await message.delete()
                # Создаём информационное сообщение
                emFilterWhiteLinks = discord.Embed(title='❌ • ВНИМАНИЕ!', description='```Сообщения с ссылками на сайты не из белого списка не пропускаются в глобальный чат.```', color=0xd40000)
                # Отправляем информационное сообщение и удаляем его через 13 секунд
                await message.channel.send(embed=emFilterWhiteLinks, delete_after=13)
                return

    # Создаём сообщение в глобальный канал
    emGlobalMessage = discord.Embed(description=f" **{message.author.name}**: {message.content}", colour=0x2F3136)
    emGlobalMessage.set_footer(text=f"Сервер: {message.guild.name} // ID пользователя: {message.author.id}")

    # Проверяем расширение файлов
    for attachment in message.attachments:
        if attachment.filename.endswith(('bmp', 'jpeg', 'jpg', 'png', 'gif')):
            emGlobalMessage.set_image(url=attachment.url)
        else:
            # Удаляем сообщение пользователя
            await message.delete()
            # Создаём информационное сообщение
            emFilterFormatFiles = discord.Embed(title='❌ • ВНИМАНИЕ!', description='```Файлы с расширениями *.bmp, *.jpeg, *.jpg, *.png, *.gif, не пропускаются в глобальный чат.```', color=0xd40000)
            # Отправляем информационное сообщение и удаляем его через 13 секунд
            await message.channel.send(embed=emFilterFormatFiles, delete_after=13)
            return

    # Удаляем сообщение, отправленное пользователем
    # await message.delete()

    # Отправляем сообщение
    await send_to_servers(f'> Сервер: `{message.guild.name}` // ID пользователя: `{message.author.id}`\n{message.content}')


# endregion ••••••••••••• ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА // КОНЕЦ


# ••••••••••••••••


# region •••••••••••••••• КОМАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ
@client.slash_command(guild_ids=guild_ids_for_slash(), default_permission=False, name='ping', description='Проверить состояние приложения')
# Команду может выполнить только владелец приложения
@permissions.is_owner()
async def ping(ctx):
    # Создаём сообщение
    embed = discord.Embed(title='ВНИМАНИЕ!', description=f'Задержка {round(client.latency * 100, 1)} ms', colour=0x90D400)
    # Отправляем скрытое сообщение
    await ctx.respond(embed=embed, ephemeral=True)

# endregion ••••••••••••• КОМАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ // КОНЕЦ


# region •••••••••••••••• КОМАНДА ОТОБРАЖЕНИЯ ИНФОРМАЦИИ О ПРИЛОЖЕНИИ
@client.slash_command(guild_ids=guild_ids_for_slash(), default_permission=True, name='information', description='Показать информацию о приложение.')
async def information(ctx):
    # Создаём сообщение
    embed = discord.Embed(title='ИНФОРМАЦИЯ', description=f'```{config.app_full_description}```', colour=0x2F3136)
    embed.set_thumbnail(url=f'{client.user.avatar.url}')
    embed.set_footer(icon_url=f'{ctx.author.avatar.url}', text=f'Информация запрошена: {ctx.author.name}')
    invite_app = discord.utils.oauth_url(client_id=client.user.id, permissions=discord.Permissions(),scopes=("bot", "applications.commands"))
    # Создаём кнопки
    button = discord.ui.View()
    button.add_item(discord.ui.Button(label='Сервер поддержки', url=config.app_support_server_invite, style=discord.ButtonStyle.url))
    button.add_item(discord.ui.Button(label='Добавить на сервер', url=invite_app, style=discord.ButtonStyle.url))
    button.add_item(discord.ui.Button(label='GitHub', url=config.app_github_url, style=discord.ButtonStyle.url))
    # Отправляем сообщение и удаляем его через 60 секунд
    await ctx.respond(embed=embed, view=button, delete_after=60)


# endregion ••••••••••••• КОМАНДА ОТОБРАЖЕНИЯ ИФОРМАЦИИ О ПРИЛОЖЕНИЕ // КОНЕЦ


# region •••••••••••••••• КОМАНДА ВЫВОДА ПРАВИЛ ГЛОБАЛЬНОГО КАНАЛА
@client.slash_command(guild_ids=guild_ids_for_slash(), default_permission=True, name='rules', description='Показать правила использования глобального канала.')
async def rules_cmd(ctx):
    emRules = discord.Embed(title='ПРАВИЛА', description=config.globalchannel_rules, colour=0x2F3136)
    await ctx.send(embed=emRules, delete_after=60)


# endregion ••••••••••••• КОМАНДА ВЫВОДА ПРАВИЛ ГЛОБАЛЬНОГО КАНАЛА // КОНЕЦ


# region •••••••••••••••• КОМАНДА СОЗДАНИЯ КАНАЛА ДЛЯ ПРИЁМА И ОТПРАВКИ СООБЩЕНИЙ
@client.slash_command(guild_ids=guild_ids_for_slash(), default_permission=True, name='setup', description='Создать канала для приёма и передачи сообщений.')
# Команду может выполнить только пользователь, с ролью администратор

async def setup(ctx):
    if isinstance(ctx.author, discord.User):  # проверка, не в лс ли идёт команда
        await ctx.send('Использование этой команды допускается только на серверах, не в личных сообщениях',
                       delete_after=13)
        return

    if ctx.author.guild_permissions.administrator:  # проверка наличия админских прав на сервере у выполняющего
        guild = ctx.guild
        if discord.utils.get(guild.text_channels, name=config.globalchannel) is None:  # проверка на наличие нужного канала
            # Выдаём права нужные для работы приложения
            # TODO: manage_channels=True, manage_permissions=True - Требуеют права администратора на сервере
            overwrites = {
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True, embed_links=True, attach_files=True)
            }
            # Создаём канал на сервере
            await guild.create_text_channel(name=config.globalchannel, topic=config.setup_globalchannel_description, overwrites=overwrites, slowmode_delay=config.setup_globalchannel_cooldown, reason='Создание канала для Wormhole.')
            await ctx.send(
                f'Канал {config.globalchannel} успешно создан и будет использоваться для пересылки сообщений',
                delete_after=13)
        else:
            await ctx.send(f'У вас уже есть подходящий канал: {config.globalchannel}', delete_after=13)
    else:
        await ctx.send('Для выполнения этой команды вам необходимо обладать правами администратора на этом сервере',
                       delete_after=13)


# endregion ••••••••••••• КОМАНДА СОЗДАНИЯ КАНАЛА ДЛЯ ПРИЁМА И ОТПРАВКИ СООБЩЕНИЙ // КОНЕЦ


# ••••••••••••••••

# region •••••••••••••••• СОЗДАЁМ ГРУППУ КОМАНД USER ДЛЯ КОМАНД С КОСОЙ ЧЕРТОЙ
user = client.create_group("user", "Команды для работы с пользователями.")


# endregion ••••••••••••• СОЗДАЁМ ГРУППУ КОМАНД SERVER ДЛЯ КОМАНД С КОСОЙ ЧЕРТОЙ // КОНЕЦ


# region •••••••••••••••• КОМАНДА БЛОКИРОВКИ ПОЛЬЗОВАТЕЛЯ В ГЛОБАЛЬНОМ КАНАЛЕ
@user.command(guild_ids=guild_ids_for_slash(), default_permission=False, name='block', description='Заблокировать пользователя в глобальном канале.')
# @permissions.is_user(USER_ID)
async def user_block(ctx, user, reason=None):
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


# endregion ••••••••••••• КОМАНДА БЛОКИРОВКИ ПОЛЬЗОВАТЕЛЯ В ГЛОБАЛЬНОМ КАНАЛЕ // КОНЕЦ


# region •••••••••••••••• КОМАНДА РАЗБЛОКИРОВКИ ПОЛЬЗОВАТЕЛЯ В ГЛОБАЛЬНОМ КАНАЛЕ
@user.command(guild_ids=guild_ids_for_slash(), default_permission=False, name='remove', description='Разблокировать пользователя в глобальном канале.')
# @permissions.is_user(USER_ID)
async def user_remove(ctx, user):
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


# endregion ••••••••••••• КОМАНДА РАЗБЛОКИРОВКИ ПОЛЬЗОВАТЕЛЯ В ГЛОБАЛЬНОМ КАНАЛЕ // КОНЕЦ


# region •••••••••••••••• КОМАНДА ОТОБРАЖЕНИЯ ЧЁРНОГО СПИСОКА
@user.command(guild_ids=guild_ids_for_slash(), default_permission=False, name='blacklist', description='Показать список пользователей заблокированных в глобальном канале.')
# @permissions.is_user(USER_ID)
# Показ содержимого чёрного списка
# TODO: Нормальное форматирование таблицы
async def user_blacklist(ctx):
    full_list = await sql_conn.execute('select userid, add_timestamp, reason, banner_id from black_list')
    table = ['username  userid    add_timestamp   reason  banner_id']
    for user in (await full_list.fetchall()):
        username = await fetch_or_get_user(int(user[0]))
        if isinstance(username, discord.User):
            username = username.name

        table.append(str(username) + '   ' + '   '.join([str(item).center(5, ' ') for item in user]))
    table = "```" + '\n'.join(table) + "```"
    await ctx.send(table, delete_after=13)


# endregion ••••••••••••• КОМАНДА ОТОБРАЖЕНИЯ ЧЁРНОГО СПИСОКА // КОНЕЦ


# ••••••••••••••••


# region •••••••••••••••• СОЗДАЁМ ГРУППУ КОМАНД SERVER ДЛЯ КОМАНД С КОСОЙ ЧЕРТОЙ
server = client.create_group("server", "Команды для работы с серверами.")


# endregion ••••••••••••• СОЗДАЁМ ГРУППУ КОМАНД SERVER ДЛЯ КОМАНД С КОСОЙ ЧЕРТОЙ // КОНЕЦ


# region •••••••••••••••• КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ
@server.command(guild_ids=guild_ids_for_slash(), default_permission=False, name='list', description='Вывести список серверов, к которым подключено приложение.')
# Команду может выполнить только владелец приложения
@permissions.is_owner()
async def server_list(ctx):
    # Создаём сообщение
    embed = discord.Embed(title='СПИСОК СЕРВЕРОВ', description='```Список серверов, к которым подключено приложение.```', colour=0x2F3136)
    embed.add_field(name='СПИСОК СЕРВЕРОВ:', value=''.join(guild.name + f' (ID:{guild.id})\n' for guild in client.guilds))
    # Отправляем скрытое сообщение
    await ctx.respond(embed=embed, ephemeral=True)


# endregion ••••••••••••• КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ // КОНЕЦ


# region •••••••••••••••• КОМАНДА ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ ОТ СЕРВЕРА
@server.command(guild_ids=guild_ids_for_slash(), default_permission=False, name='leave', description='Отключить приложение от сервера.')
# Команду может выполнить только владелец приложения
@permissions.is_owner()
async def server_leave(
    ctx: discord.ApplicationContext,
    id: Option(str, 'Укажжите ID сервера')):

    if (guild_to_leave := client.get_guild(int(id))) is None:
        # Создаём сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!', description=f'```Сервер с указанным ID ({id}) не найден```', color=0xd40000)
        # Отправляем скрытое сообщение
        await ctx.respond(embed=embed, ephemeral=True)
        return

    await guild_to_leave.leave()
    # Создаём сообщение
    embed = discord.Embed(title='❌ • ВНИМАНИЕ!', description=f'```Сервер с указанным ID ({id}) успешно покинут```', colour=0x2F3136)
    # Отправляем скрытое сообщение
    await ctx.respond(embed=embed, ephemeral=True)


# endregion ••••••••••••• КОМАНДА ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ ОТ СЕРВЕРА // КОНЕЦ


# ••••••••••••••••


# region •••••••••••••••• СОЗДАЁМ ГРУППУ КОМАНД MODERATOR ДЛЯ КОМАНД С КОСОЙ ЧЕРТОЙ
moderator = client.create_group("moderator", "Команды связанные с серверами.")


# endregion ••••••••••••• СОЗДАЁМ ГРУППУ КОМАНД MODERATOR ДЛЯ КОМАНД С КОСОЙ ЧЕРТОЙ // КОНЕЦ


# region •••••••••••••••• КОМАНДА ВЫВОДА СПИСКА МОДЕРАТОРОВ
@moderator.command(guild_ids=guild_ids_for_slash(), default_permission=False, name='list', description='Вывести список модераторов глобального канала.')
# Команду может выполнить только владелец приложения
@permissions.is_owner()
async def moderator_list(ctx):
    moderators = str()
    for moderator_id in await get_owners():
        moderator_user = await fetch_or_get_user(moderator_id, suppress=False)
        moderators = f'{moderators}{moderator_user.name}#{moderator_user.discriminator} <@{moderator_user.id}>\n'

    emModers = discord.Embed(
        title='Модераторы',
        description=moderators,
    )
    await ctx.send(embed=emModers, delete_after=60)


# endregion ••••••••••••• КОМАНДА ВЫВОДА СПИСКА МОДЕРАТОРОВ // КОНЕЦ


client.run(config.token)


# •••••• 🦆 •••••• СОЗДАЁМ ПРИЛОЖЕНИЕ И НАЗЫВАЕМ ЕГО CLIENT  // КОНЕЦ