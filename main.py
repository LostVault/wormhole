# ------------- ИМПОРТ МОДУЛЕЙ

# import os
# import sys
# import json
import discord                                      # Импортируем основной модуль
from discord.ext import commands                    # Импортируем команды из модуля discord.ext
from discord.ext.commands import has_permissions
# import asyncio                                      # Испортируем модуль для работы с асинхронными командами
import logging                                      # Импортируем моудль логирования
# import random                                     # Импортируем модуль генерирования случайных чисел
# import datetime                                   # Импортируем модуль времени

import config                                       # Импортируем настройки приложения
# ------------- ИМПОРТ МОДУЛЕЙ // КОНЕЦ

blackoverlordlist = ["665018860587450388", "777300091621998632"]


# Создаём приложение и называем его client
client = commands.Bot(description="Test bot", command_prefix=commands.when_mentioned_or(config.prefix), help_command=None)


# Выводим данные подключения в консоль
logging.basicConfig(level=logging.INFO)


# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ
@client.event
async def on_ready():
    print('\n-••••••••••••••••••••••••••••••-')
    print(' APP Name: {0.user} '.format(client))  # Показывает имя приложения указанное на discordapp.com
    print(' Client ID: {0.user.id} '.format(client))  # Показывает ID приложения указанное на discordapp.com
    print(' Link for connection: https://discordapp.com/oauth2/authorize?&client_id={0.user.id}&scope=bot&permissions=0'.format(client))
    print(' Hello world!')
    print('-••••••••••••••••••••••••••••••-')
    print('Servers connected to:')
    for guild in client.guilds:
        print(guild.name)
    print('-••••••••••••••••••••••••••••••-\n')

    # Изменяем статус приложения
    await client.change_presence(status=discord.Status.online, activity=discord.Game('Elite Dangerous'))
# ------------- ВЫВОДИМ ДАННЫЕ ПРИЛОЖЕНИЯ ПРИ ПОДКЛЮЧЕНИЕ В КОНСОЛЬ // КОНЕЦ


# ------------- ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА
@client.event
async def on_message(message):

    # Пропускает комманды для регистрации
    await client.process_commands(message)

    # Дублирует сообщения в консоль приложения
    print('Chanel #{0.channel} / {0.author}: {0.content}'.format(message))

    channel = discord.utils.get(message.guild.text_channels, name=config.globalchannel)

    # Игнорируем сообщения отправленные на других каналах
    if message.channel.id != channel.id:
        return

    # Игнорируем сообщения с упоминанием
    if message.mentions or message.mention_everyone:
        # --
        try:
            await message.delete()
        except:
            pass
        # --
        await channel.send('` ⚠ • ВНИМАНИЕ! ` Сообщения с упоминанием всех активных и неактивных пользователей не пропускаются в общий чат.'.format(message), delete_after=13)
        return

    # Игнорируем сообщения отправленные приложением
    if message.author.id == client.user.id:
        return

    #    if message.author.id == blackoverlordlist:
    #        await channel.send('` ⚠ • ВНИМАНИЕ! ` Пользователи нахоядщиеся в списке Black Overlord List не могут отправлять собщения на другие сервера.'.format(message), delete_after=13)
    #        return

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
                await channel.send(' ` {0.guild.name} ` — **` {0.author.name} `**: {0.content}'.format(message))
            except discord.Forbidden:
                print(f"Невозможно отправить сообщение на сервер {guild.name}: Недостаточно прав")
            except discord.HTTPException as e:
                print(f"Невозможно отправить сообщение на сервер {guild.name}: {e}")
# ------------- ВЫВОДИМ СООБЩЕНИЯ ПОЛЬЗОВАТЕЛЕЙ В КОНСОЛЬ ПРИЛОЖЕНИЯ И ПЕРЕНАПРАВЛЯЕМ НА ДРУГИЕ СЕРВЕРА // КОНЕЦ


# ------------- ОБРАБАТЫВАВЕМ ОШБИКИ КОММАНД
@client.event
async def on_command_error(ctx, error, amount=1):
    if isinstance(error, commands.CommandNotFound):
        # Удаляем сообщение отправленное пользователем
        await ctx.channel.purge(limit=amount)
        # Создаём сообщение
        embedcommandnotfound = discord.Embed(title='ВНИМАНИЕ!', description='' + ctx.author.mention + ', к сожалению команды **' + ctx.message.content + '** не существует.', color=0xd40000)
        embedcommandnotfound.set_footer(icon_url=ctx.author.avatar_url,text='Vox Galactica // Сообщение удалится через 13 секудн.')
        # Отправляем сообщение и удаляем его через 13 секунд
        await ctx.send(embed=embedcommandnotfound, delete_after=13)
    if isinstance(error, commands.MissingPermissions):
        # Удаляем сообщение отправленное пользователем
        await ctx.channel.purge(limit=amount)
        # Создаём сообщение
        embedcommandMissingPermissions = discord.Embed(title='ВНИМАНИЕ!', description='' + ctx.author.mention + ', к сожалению у вас нету прав на комманду **' + ctx.message.content + '', color=0xd40000)
        embedcommandMissingPermissions.set_footer(icon_url=ctx.author.avatar_url,text='Vox Galactica // Сообщение удалится через 13 секудн.')
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
    await ctx.send(f'` **{ctx.author.name}** ` Pong! ({client.latency*1000}ms)', delete_after=13)
# ------------- КОММАНДА ПРОВЕРКА ПРИЛОЖЕНИЯ // КОНЕЦ


# ------------- КОМАНДА ВЫВОДА СПИСКА СЕРВЕРОВ
@client.command(aliases=['сервера'], brief='Проверка состояния приложения', pass_context=True)
# Команду может выполнить только владельце приложения
@commands.is_owner()
async def servers(ctx, amount=1):
    activeservers = client.guilds
    for guild in activeservers:
        await ctx.send(guild.name)
        print(guild.name)
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
    # Отправляем сообщение и удаляем его через 13 секунд
    for guild in client.guilds:
        if channel := discord.utils.get(guild.text_channels, name=config.globalchannel):
            await channel.send('` ⚠ • ВНИМАНИЕ! ` Приложение отключено.')
    # Отключаем приложение
    print('\n-••••••••••••••••••••••••••••••-')
    print(' Goodbye World!')
    print('-••••••••••••••••••••••••••••••-\n')
    quit()
# ------------- ОТКЛЮЧЕНИЕ ПРИЛОЖЕНИЯ ПО КОМАНДЕ// КОНЕЦ


# Генирируемый токен при создание приложения на discordapp.com необходимый для подключенияю к серверу. // Прописывается в config.py
client.run(config.token)