# -*- coding: utf-8 -*-

# region #########################################
#
#            ╦ ╦╔═╗╔═╗╔╦╗╦ ╦╔═╗╦  ╔═╗
#            ║║║║ ║╠╦╝║║║╠═╣║ ║║  ╠═
#            ╚╩╝╚═╝╩╚═╩ ╩╩ ╩╚═╝╚═╝╚═╝
#
##################################################
#
#                     ПАМЯТКА
#
# СВОРАЧИВАНИЕ КОДА
# Разверрнуть всё   [Ctrl] + [Shift] + [➕]
# Свернуть всё      [Ctrl] + [Shift] + [➖]
#
#
# Заккоментировать. Расскоментировать [Ctrl] + [.]
#
# endregion #######################################


# region •••••••••••••••• ИМПОРТ БИБЛИОТЕК
import discord  # Импортируем библиотеку работы с Discord API (Application Programming Interface)
from discord import app_commands  # Импортируем библиотеку команд с косой чертой
# from discord import Webhook, AsyncWebhookAdapter # Импортируем библиотеку для работы с Webhook


import time  # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ
import typing  # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ
import logging  # Импортируем библиотеку для работы с журналом (log)
# import aiohttp  # TODO: Указать комментарий, описывающий данную строку ᓚᘏᗢ
import aiosqlite  # Импортируем библиотеку для работы с базами SQLite
# import tempfile
# from pathlib import Path
# from os import listdir

# endregion ••••••••••••• ИМПОРТ БИБЛИОТЕК // КОНЕЦ


# region •••••••••••••••• ИМПОРТ МОДУЛЕЙ
import config  # Импортируем модуль с настройками приложения


# endregion ••••••••••••• ИМПОРТ МОДУЛЕЙ // КОНЕЦ



# •••••• 😈 •••••• СОЗДАЁМ ПРИЛОЖЕНИЕ И НАЗЫВАЕМ ЕГО CLIENT


# region •••••••••••••••• ПРОВЕРЯЕМ В КАКОМ ОКРУЖЕНИЕ ЗАПУЩЕНО ПРИЛОЖЕНИЕ
MY_GUILD = discord.Object(id=978692915092152391)  # replace with your guild id


# endregion ••••••••••••• ПРОВЕРЯЕМ В КАКОМ ОКРУЖЕНИЕ ЗАПУЩЕНО ПРИЛОЖЕНИЕ // КОНЕЦ


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # CommandTree - это специальный тип, который содержит все состояния команд приложения, необходимые для его работы.
        # Это отдельный класс, потому что он позволяет включить все дополнительные состояния.
        # Всякий раз, когда вы хотите работать с командами приложения, ваше дерево используется для их хранения и работы с ними.
        # Примечание: При использовании commands.Bot вместо discord.Client, вместо этого бот будет поддерживать свое собственное дерево.
        self.tree = app_commands.CommandTree(self)

    # Синхронизируем команды с серверами к которым подключено приложение
    # Вместо того, чтобы указывать ID сервера для каждой команды, вместо этого мы копируем наши глобальные команды.
    # Поступая таким образом, нам не нужно ждать до часа, пока они не будут показаны конечному пользователю.
    async def setup_hook(self):
        # Синхронизируем глобальные команды с серверами
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()

# Назначить требуемые намерения для приложения
# Подрбнобно о намериниях на странице https://discordpy.readthedocs.io/en/latest/intents.html
intents.guilds = True
intents.message_content = True  # 'message_content' требуется для получения содержимого сообщений
intents.guild_messages = True

client = MyClient(intents=intents)


# region •••••••••••••••• СОЗДАЁМ ШАБЛОН С ССЫЛКОЙ ДЛЯ ПОДКЛЮЧЕНИЯ К СЕРВЕРУ
def get_invite_link(bot_id):
    return f'https://discord.com/oauth2/authorize?client_id={bot_id}&scope=bot%20applications.commands'


# endregion ••••••••••••• СОЗДАЁМ ШАБЛОН С ССЫЛКОЙ ДЛЯ ПОДКЛЮЧЕНИЯ К СЕРВЕРУ


# region •••••••••••••••• СОЗДАЁМ И НАСТРАИВАЕМ РЕГИСТРАЦИЮ СОБЫТИЙ
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Регистрируем все события ниже уровня информации
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(process)d:%(thread)d: %(module)s:%(lineno)d: %(message)s')


# endregion ••••••••••••• СОЗДАЁМ И НАСТРАИВАЕМ РЕГИСТРАЦИЮ СОБЫТИЙ // КОНЕЦ


# region •••••••••••••••• РЕГИСТРИРУЕМ ИНФОРМАЦИЮ О ПРИЛОЖЕНИЕ В КОНСОЛЬ
@client.event
async def on_ready():
    global sql_conn
    sql_conn = await aiosqlite.connect(config.db_file_name)
    await sql_conn.execute('create table if not exists black_list (userid integer not null unique, '
                           'add_timestamp text default current_timestamp, reason text, banner_id integer);')

    # Регистрируем данные приложения в консоль Python
    logger.info(f'APP Username: {client.user} ')
    logger.info(f'Using token {config.token[0:2]}...{config.token[-3:-1]}')
    logger.info(f'Current env type: {config.environment_type}')
    logger.info(f'Using global channel: {config.globalchannel}')
    logger.info('APP Client ID: {0.user.id} '.format(client))

    # Регистрируем ссылку для подключения приложения к серверу в консоль
    logger.info(f'Link for connection: {get_invite_link(client.user.id)}')

    # Регистрируем список серверов к которым подключено приложение в консоль
    logger.info('Servers connected to: ' + ''.join('"' + guild.name + '"; ' for guild in client.guilds))

    # Изменяем статус приложения
    await client.change_presence(status=discord.Status.online, activity=discord.Game(config.app_status_game))


# endregion ••••••••••••• РЕГИСТРИРУЕМ ИНФОРМАЦИЮ О ПРИЛОЖЕНИЕ В КОНСОЛЬ // КОНЕЦ


# ••••••••••••••••••••••••••••••••
# •••••••••••••••• КОМАНДЫ - ОСНОВНЫЕ
# ••••••••••••••••••••••••••••••••


# region •••••••••••••••• КОМАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ
@client.tree.command(name="ping")
# Разрешает выполнять команду только администраторам серверов
@app_commands.default_permissions()
async def ping(interaction: discord.Interaction):
    #  Пишем описание команды
    """Проверить состояние приложения."""
    # Создаём встроенное сообщение
    embed = discord.Embed(title='ВНИМАНИЕ!', description=f'Задержка {round(client.latency * 100, 1)} мс',
                          colour=0x90D400)
    # Отправляем скрытое сообщение
    await interaction.response.send_message(embed=embed, ephemeral=True)


# endregion ••••••••••••• КОМАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ // КОНЕЦ


# region •••••••••••••••• КОМАНДА ОТОБРАЖЕНИЯ ИНФОРМАЦИИ О ПРИЛОЖЕНИИ
@client.tree.command(name="information")
async def information(interaction: discord.Interaction):
    #  Пишем описание команды
    """Показать информацию о приложение."""
    # Создаём сообщение
    embed = discord.Embed(title='ИНФОРМАЦИЯ', description=f'```{config.app_full_description}```', colour=0x2F3136)
    # Отправляем скрытое сообщение
    await interaction.response.send_message(embed=embed, ephemeral=True)


# endregion ••••••••••••• КОМАНДА ОТОБРАЖЕНИЯ ИФОРМАЦИИ О ПРИЛОЖЕНИЕ // КОНЕЦ


# region •••••••••••••••• КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ
@client.tree.command(name='bulka', description="desc test")
# Разрешает выполнять команду только администраторам серверов
# @app_commands.default_permissions()
async def test(interaction: discord.Interaction):
    #  Пишем описание команды
    """Вывести список серверов, к которым подключено приложение."""
    # Создаём сообщение
    embed = discord.Embed(title='СПИСОК СЕРВЕРОВ', description='```Список серверов, к которым подключено приложение.```', colour=0x2F3136)
    embed.add_field(name='СПИСОК СЕРВЕРОВ:', value=''.join(guild.name + f' `ID: {guild.id}`\n' for guild in client.guilds))
    # Отправляем скрытое сообщение
    await interaction.response.send_message(embed=embed, ephemeral=True)


# endregion ••••••••••••• КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ // КОНЕЦ


# region •••••••••••••••• КОМАНДА ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ ОТ СЕРВЕРА
@client.tree.command()
# Разрешает выполнять команду только администраторам серверов
@app_commands.default_permissions()
@app_commands.describe(id='Укажите ID сервера от которого требуется отключится')
async def server_leave(interaction: discord.Interaction, id: str):
    #  Пишем описание команды
    """Отключить приложение от сервера."""

    if (guild_to_leave := client.get_guild(int(id))) is None:
        # Создаём сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!', description=f'```Сервер с указанным ID ({id}) не найден```',
                              color=0xd40000)
        # Отправляем скрытое сообщение
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await guild_to_leave.leave()
    # Создаём сообщение
    embed = discord.Embed(title='✅ • ВНИМАНИЕ!', description=f'```Сервер с указанным ID ({id}) успешно покинут```',
                          colour=0x2F3136)
    # Отправляем скрытое сообщение
    await interaction.response.send_message(embed=embed, ephemeral=True)


# endregion ••••••••••••• КОМАНДА ОТКЛЮЧЕНИЯ ПРИЛОЖЕНИЯ ОТ СЕРВЕРА // КОНЕЦ


# ••••••••••••••••••••••••••••••••
# •••••••••••••••• КОМАНДЫ - ГЛОБАЛЬНЫЕ КАНАЛЫ
# ••••••••••••••••••••••••••••••••


# region •••••••••••••••• КОМАНДА ОТОБРАЖЕНИЯ ПРАВИЛ ГЛОБАЛЬНОГО КАНАЛА
@client.tree.command(name="rules")
async def rules_cmd(interaction: discord.Interaction):
    #  Пишем описание команды
    """Показать правила использования глобального канала."""
    # Создаём сообщение
    embed = discord.Embed(title='ПРАВИЛА', description=f'{config.globalchannel_rules}', colour=0x2F3136)
    # Отправляем скрытое сообщение
    await interaction.response.send_message(embed=embed, ephemeral=True)


# endregion ••••••••••••• КОМАНДА ОТОБРАЖЕНИЯ ПРАВИЛ ГЛОБАЛЬНОГО КАНАЛА // КОНЕЦ


# ••••••••••••••••••••••••••••••••
# •••••••••••••••• ГЛОАБЛЬНЫЕ КАНАЛЫ - ОТПРАВКА СООБЕЩНИЯ
# ••••••••••••••••••••••••••••••••


# region •••••••••••••••• ПРОВЕРЯЕМ СОБЩЕНИЕ НА COOLDOWNN
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


# region •••••••••••••••• СОЗДАЁМ ШАБЛОН ДЛЯ ПЕРЕСЫЛКИ СООБЩЕНИЯ НА ВСЕ СЕРВЕРА
async def send_Global_messages(*args, **kwargs):
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
                # Сравниваем по очереди сервера из списка серверов с сервером с которого отправлено сообщение
                # Если сервер не совпадает то отправляем в его глобальный чат сообщение, а в ином случае нет
                if channel.guild != message_guild:
                    await channel.send(*args, **kwargs)
            except discord.Forbidden as e:
                logger.warning(f"Не удалось отправить сообщение {guild.name}: discord.Forbidden\n{e}")
            except discord.HTTPException as e:
                logger.warning(f"Не удалось отправить сообщение {guild.name}: discord.HTTPException\n{e}")
            except Exception as e:
                logger.warning(f"Не удалось отправить сообщение {guild.name}: {e}")


# endregion ••••••••••••• СОЗДАЁМ ШАБЛОН ДЛЯ ПЕРЕСЫЛКИ СООБЩЕНИЯ НА ВСЕ СЕРВЕРА // КОНЕЦ


# region •••••••••••••••• СОЗДАЁМ ШАБЛОН ДЛЯ ПЕРЕСЫЛКИ WEBHOOK НА ВСЕ СЕРВЕРА
# async def send_Global_webhook(*args, **kwargs):

# endregion ••••••••••••• СОЗДАЁМ ШАБЛОН ДЛЯ ПЕРЕСЫЛКИ WEBHOOK НА ВСЕ СЕРВЕРА // КОНЕЦ


# region •••••••••••••••• ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА
@client.event
async def on_message(message):
    # Console Log // Выводим сообщения пользователей в консоль Python
    logger.info('Message: {0.guild} / #{0.channel} / {0.author}: {0.content}'.format(message))

    # Игнорируем сообщения, отправленные этим приложением
    if message.author.id == client.user.id:
        return

    # Игнорируем сообщения в ЛС
    if isinstance(message.channel, discord.DMChannel):
        return

    # Игнорируем сообщения, отправленные не в глобальном канале
    if message.channel.name != config.globalchannel:
        return

    # Игнорируем сообщения, отправленные другими приложениями
    if message.author.bot:
        return

    # Игнорируем сообщения с упоминанием
    if message.mentions or message.mention_everyone:
        # Помечаем сообщение реакцией как неотправленное
        await message.add_reaction("❌")
        # Создаём информационное сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!',
                              description='```Сообщения с упоминанием всех активных и неактивных пользователей, не пропускаются в глобальный чат.```',
                              color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=embed, delete_after=13)
        return

    # Игнорируем сообщения с символом "@"
    if "@" in message.content:
        # Помечаем сообщение реакцией как неотправленное
        await message.add_reaction("❌")
        # Создаём информационное сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!',
                              description='```Сообщения с символом "@" не пропускаются в глобальный чат.```',
                              color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=embed, delete_after=13)
        return

    # Игнорируем сообщения, отправленные пользователем из чёрного списка
    if (await (
    await sql_conn.execute('select count(*) from black_list where userid = ?;', [message.author.id])).fetchone())[
        0] == 1:
        # Помечаем сообщение реакцией как неотправленное
        await message.add_reaction("❌")
        # Создаём информационное сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!',
                              description='```Сообщение пользователей из чёрного списка, не пропускаются в глобальный чат.\nВам по прежнему доступно использование команд приложения.```',
                              color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=embed, delete_after=13)
        return

    # Проверяйем минимальное количество символов разрешённое к отправке
    if len(message.clean_content) < config.shortmessages:
        # Удаляем сообщение пользователя
        await message.add_reaction("❌")
        # Создаём информационное сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!',
                              description=f'```Сообщения длиной менее {config.shortmessages} символов не пропускаются в глобальный чат.```',
                              color=0xd40000)
        # Отправляем информационное сообщение и удаляем его через 13 секунд
        await message.channel.send(embed=embed, delete_after=13)
        return

    # Проверяйем время с последнего сообщения отправленное пользователем
    kd_status = handle_cooldown(message.author.id)
    # if isinstance(kd_status, int):
    if type(kd_status) is int:
        # Помечаем сообщение реакцией как неотправленное
        await message.add_reaction("❌")
        # Создаём информационное сообщение
        embed = discord.Embed(title='❌ • ВНИМАНИЕ!',
                              description=f'```С последнего сообщения прошло слишком мало времени, попробуйте отправить сообщение повторно через {kd_status} секунд.```',
                              color=0xd40000)
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
                # Помечаем сообщение реакцией как неотправленное
                await message.add_reaction("❌")
                # Создаём информационное сообщение
                embed = discord.Embed(title='❌ • ВНИМАНИЕ!',
                                      description='```Сообщения с ссылками на сайты не из белого списка не пропускаются в глобальный чат.```',
                                      color=0xd40000)
                # Отправляем информационное сообщение и удаляем его через 13 секунд
                await message.channel.send(embed=embed, delete_after=13)
                return

    # Проверяем расширение файлов
    for attachment in message.attachments:
        if attachment.filename.endswith(('bmp', 'jpeg', 'jpg', 'png', 'gif')):
            pass
        else:
            # Помечаем сообщение реакцией как неотправленное
            await message.add_reaction("❌")
            # Создаём информационное сообщение
            emFilterFormatFiles = discord.Embed(title='❌ • ВНИМАНИЕ!',
                                                description='```Только файлы с расширениями *.bmp, *.jpeg, *.jpg, *.png, *.gif, пропускаются в глобальный чат.```',
                                                color=0xd40000)
            # Отправляем информационное сообщение и удаляем его через 13 секунд
            await message.channel.send(embed=emFilterFormatFiles, delete_after=13)
            return

    # Создаём глобальную переменную с наименованием сервера с которого отправлено сообщение
    # Для проверки его в ШАБЛОНЕ ДЛЯ ПЕРЕСЫЛКИ СООБЩЕНИЯ НА ВСЕ СЕРВЕРА
    global message_guild
    message_guild = message.guild

    # Отправляем сообщение
    await send_Global_messages(f'> **{message.author.name}** // Сервер: `{message.guild.name}` // ID пользователя: `{message.author.id}`\n{message.content}', files=[await f.to_file() for f in message.attachments])
    # Помечаем сообщение реакцией как отправленное
    # TODO: Хотя оно наверное в любом случае отправится, надо сделать какую-то проверку ᓚᘏᗢ
    await message.add_reaction("✅")

    # if len(message.attachments) > 0:
    #     with tempfile.TemporaryDirectory() as tmpdirname:
    #         temp_dir = Path(tmpdirname)
    #         print('created temporary directory', tmpdirname)
    #         for f in message.attachments:
    #             await f.save(f"{temp_dir}/{attachment.filename}")
    #             for attachment in Path(temp_dir).glob('*'):
    #                 print(attachment)
    #             await send_to_servers(f'> Пользователя: `{message.author.name}` // Сервер: `{message.guild.name}` // ID пользователя: `{message.author.id}`\n{message.content}', files=[discord.File(attachment) for attachment in Path(temp_dir).glob('*')])
    # else:
    #     await send_to_servers(f'> Пользователя: `{message.author.name}` // Сервер: `{message.guild.name}` // ID пользователя: `{message.author.id}`\n{message.content}')


# endregion ••••••••••••• ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА // КОНЕЦ


client.run(config.token)

# •••••• 🦆 •••••• СОЗДАЁМ ПРИЛОЖЕНИЕ И НАЗЫВАЕМ ЕГО CLIENT // КОНЕЦ