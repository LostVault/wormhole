# ------------- ИМПОРТ МОДУЛЕЙ

# import os
# import sys
# import json
import discord  # Импортируем основной модуль
from discord.ext import commands  # Импортируем команды из модуля discord.ext
from discord.ext.commands import has_permissions
# import asyncio                                      # Испортируем модуль для работы с асинхронными командами
import logging  # Импортируем моудль логирования
import aiosqlite
# import random                                     # Импортируем модуль генерирования случайных чисел
# import datetime                                   # Импортируем модуль времени

import config  # Импортируем настройки приложения

# ------------- ИМПОРТ МОДУЛЕЙ // КОНЕЦ

# Создаём приложение и называем его client

client = commands.Bot(description="Test bot", command_prefix=commands.when_mentioned_or(config.prefix), case_insensitive=True, help_command=None)


# Выводим данные подключения в консоль
logging.basicConfig(level=logging.INFO)


# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ
@client.event
async def on_ready():
    client.sql_conn = await aiosqlite.connect('Wormhole.sqlite')
    await client.sql_conn.execute('create table if not exists black_list (userid integer not null, add_timestamp text default '
                           'current_timestamp, reason text, banner_id integer);')

    # await client.close()
    print('\n-••••••••••••••••••••••••••••••-')
    # Показывает имя приложения указанное на discordapp.com
    print(' APP Name: {0.user} '.format(client))
    # Показывает ID приложения указанное на discordapp.com
    print(' Client ID: {0.user.id} '.format(client))
    print(' Link for connection: https://discordapp.com/oauth2/authorize?&client_id={0.user.id}&scope=bot&permissions=0'.format(client))
    print(' Hello world!')
    print('-••••••••••••••••••••••••••••••-')
    # Выводит список приложений к которым подключео приложение
    print('Servers connected to:')
    for guild in client.guilds:
        print(guild.name)
    print('-••••••••••••••••••••••••••••••-\n')
    # Изменяем статус приложения
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Elite Dangerous'))

    # Отправляем сообщение в общий канал
    for guild in client.guilds:
        if channel := discord.utils.get(guild.text_channels, name=config.globalchannel):
            await channel.send('` ⚠ • ВНИМАНИЕ! ` Приложение запущено.')


# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ // КОНЕЦ


# ------------- ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА
@client.event
async def on_message(message):
    # Дублирует сообщения в консоль приложения
    print('Server {0.guild} / Chanel #{0.channel} / {0.author}: {0.content}'.format(message))

    # Пропускает комманды для регистрации
    await client.process_commands(message)

    channel = discord.utils.get(message.guild.text_channels, name=config.globalchannel)

    # Игнорируем сообщения отправленные другими приложениеми
    if message.author.bot:
        return

    # Игнорируем сообщения отправленные этим приложением
    if message.author.id == client.user.id:
        return

    # Игнорируем сообщения отправленные на других каналах
    if message.channel.id != channel.id:
        return

    # Игнорируем сообщения с упоминанием
    if message.mentions or message.mention_everyone:
        await message.delete()
        await channel.send(
            '` ⚠ • ВНИМАНИЕ! ` Сообщения с упоминанием всех активных и неактивных пользователей не пропускаются в общий чат.'.format(
                message), delete_after=13)
        return

    # Игнорируем сообщения, отправленные пользователем из чёрного списка
    if (await (await client.sql_conn.execute(
            'select count(*) from black_list where userid = ?;', [message.author.id])).fetchone())[0] == 1:
        await message.delete()
        await channel.send(
            '` ⚠ • ВНИМАНИЕ! ` Пользователи нахоядщиеся в списке **Black Overlord List** не могут отправлять собщения на другие сервера.'.format(
                message), delete_after=13)
        return

    # Игнорируем сообщения с символом @
    if "@" in message.content:
        await message.delete()
        await channel.send('` ⚠ • ВНИМАНИЕ! ` Упс! Что-то пошло не так.'.format(message), delete_after=13)
        return

    # Удаляем сообщение отправленное пользователем
    try:
        await message.delete()
    except:
        pass

    for guild in client.guilds:
        if channel := discord.utils.get(guild.text_channels, name=config.globalchannel):
            try:
                # Создаём сообщение
                emGlobalMessage = discord.Embed(description=''+ message.author.mention +' — '+ message.content +'', colour=discord.Colour(16711684))
                emGlobalMessage.set_footer(icon_url=message.guild.icon_url, text=message.guild.name)
                # Отправляем сообщение
                await channel.send(embed=emGlobalMessage)
                # Отправляем сообщение
                # await channel.send(' ` {0.guild.name} ` — **` {0.author.name} `**: {0.content}'.format(message))
            except discord.Forbidden:
                print(f"System: Невозможно отправить сообщение на сервер {guild.name}: Недостаточно прав")
            except discord.HTTPException as e:
                print(f"System: Невозможно отправить сообщение на сервер {guild.name}: {e}")

# ------------- ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА // КОНЕЦ


# ------------- ОБРАБАТЫВАВЕМ ОШБИКИ КОММАНД
@client.event
async def on_command_error(ctx, error, amount=1):
    if isinstance(error, commands.CommandNotFound):
        # Удаляем сообщение отправленное пользователем
        await ctx.channel.purge(limit=amount)
        # Создаём сообщение
        embedcommandnotfound = discord.Embed(title='ВНИМАНИЕ!', description='' + ctx.author.mention + ', к сожалению команды **'+ ctx.message.content +'** не существует.', color=0xd40000)
        embedcommandnotfound.set_footer(icon_url=ctx.author.avatar_url,text='Vox Galactica // Сообщение удалится через 13 секудн.')
        # Отправляем сообщение и удаляем его через 13 секунд
        await ctx.send(embed=embedcommandnotfound, delete_after=13)
    if isinstance(error, commands.MissingPermissions):
        # Удаляем сообщение отправленное пользователем
        await ctx.channel.purge(limit=amount)
        # Создаём сообщение
        embedcommandMissingPermissions = discord.Embed(title='ВНИМАНИЕ!',
                                                       description='' + ctx.author.mention + ', к сожалению у вас нету прав на комманду **' + ctx.message.content + '',
                                                       color=0xd40000)
        embedcommandMissingPermissions.set_footer(icon_url=ctx.author.avatar_url,
                                                  text='Vox Galactica // Сообщение удалится через 13 секудн.')
        # Отправляем сообщение и удаляем его через 13 секунд
        await ctx.send(embed=embedcommandMissingPermissions, delete_after=13)


# ------------- ОБРАБАТЫВАВЕМ ОШБИКИ КОММАНД // КОНЕЦ


# ------------- КОММАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ
@client.command(aliases=['пинг'], brief='Проверка состояния приложения', pass_context=True)
# Команду может выполнить только владельце приложения
@commands.is_owner()
async def ping(ctx, amount=1):
    # Удаляем сообщение отправленное пользователем
    await ctx.channel.purge(limit=amount)
    # Отправляем сообщение и удаляем его через 13 секунд
    await ctx.send(f'` **{ctx.author.name}** ` Pong! ({client.latency * 1000}ms)', delete_after=13)


# ------------- КОММАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ // КОНЕЦ


# ------------- КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ
@client.command(aliases=['сервера'], brief='Проверка состояния приложения', pass_context=True)
# Команду может выполнить только владельце приложения
@commands.is_owner()
async def servers(ctx, amount=1):
    activeservers = client.guilds
    for guild in activeservers:
        await ctx.send(guild.name)

# ------------- КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ // КОНЕЦ


# ------------- КОМАНДА УДАЛЕНИЯ СООБЩЕНИЙ НА КАНАЛЕ
@client.command(aliases=['очистить'], brief='Удаление ста последних сообщений на канале', pass_context=True)
# Разрешаем выполнение команды только пользователям с ролью администратор
@has_permissions(administrator=True)
async def clear(ctx, amount=100):
    # Удаляем сто последних сообщений на канале
    await ctx.channel.purge(limit=amount)


# ------------- КОМАНДА УДАЛЕНИЯ СООБЩЕНИЙ НА КАНАЛЕ // КОНЕЦ


# ------------- ОТКЛЮЧЕНИЕ ПРИЛОЖЕНИЯ ПО КОМАНДЕ
@client.command(aliases=['выключить'], brief='Выключение приложения по команде', pass_context=True)
# Команду может выполнить только владельце приложения
@commands.is_owner()
async def shutdown(ctx, amount=1):
    # Удаляем сообщение отправленное пользователем
    try:
        await ctx.channel.purge(limit=amount)
    except:
        pass
    # Отправляем сообщение в общий канал
    for guild in client.guilds:
        if channel := discord.utils.get(guild.text_channels, name=config.globalchannel):
            await channel.send('` ⚠ • ВНИМАНИЕ! ` Приложение остановлено.')
    # Отключаем приложение
    print('\n-••••••••••••••••••••••••••••••-')
    print(' Goodbye World!')
    print('-••••••••••••••••••••••••••••••-\n')
    quit()


@client.command(pass_context=True)
# @commands.is_owner()
async def ban(ctx, amount=1):
    userid_to_ban = ctx.message.content.split(' ')[1]
    await ctx.message.delete()
    try:
        userid_to_ban = int(userid_to_ban)
    except ValueError:
        await ctx.channel.send('Для бана необходимо указать ID пользователя')
        return
    await client.sql_conn.execute('insert into black_list (userid) values (?);', [userid_to_ban])
    await client.sql_conn.commit()
    await ctx.channel.send(f'Пользователь с ID {userid_to_ban} внесён в чёрный список')

# ------------- ОТКЛЮЧЕНИЕ ПРИЛОЖЕНИЯ ПО КОМАНДЕ// КОНЕЦ


# ------------- КОМАНДА ОТОБРАЖЕНИЯ ИФОРМАЦИИ О ПРИЛОЖЕНИЕ
@client.command(aliases=['информация', 'инфо', 'авторы'], brief='Проверка состояния приложения', pass_context=True)
# Команду может выполнить только владельце приложения
@commands.is_owner()
async def information(ctx, amount=1):
    # Удаляем сообщение отправленное пользователем
    await ctx.channel.purge(limit=amount)
    for guild in client.guilds:
        # Создаём сообщение
        emInformation = discord.Embed(title='Информация', description='Приложение создано для передачи текстовых сообщений между серверами связанными с игрой *Elite Dangerous*.', colour=discord.Colour(16711684))
        emInformation.add_field(name='Разработчики ', value='• <@420130693696323585>\n• <@665018860587450388>')
        emInformation.add_field(name='Благодарности', value='• <@478527700710195203>')
        emInformation.add_field(name='Список серверов', value='' + guild.name + '')
        emInformation.set_footer(text=' '+ client.user.name +' ')
        # Отправляем сообщение и удаляем его через 13 секунд
        await ctx.send(embed=emInformation, delete_after=60)
# ------------- КОМАНДА ОТОБРАЖЕНИЯ ИФОРМАЦИИ О ПРИЛОЖЕНИЕ // КОНЕЦ


# Генирируемый токен при создание приложения на discordapp.com необходимый для подключенияю к серверу. // Прописывается в config.py
client.run(config.token)
