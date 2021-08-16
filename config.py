# ------------- ОСНОВНЫЕ
from os import environ  # TODO: Указать кооментарий оисывающий данную строку ᓚᘏᗢ

"""
Для запуска приложения необходимо задать три переменные окружения:

1. `WORMHOLE_TOKEN_DISCORD` - токен для бота, полученный с 
    [Discord портала для разработчиков](https://discord.com/developers/applications)
2. `WORMHOLE_GLOBALCHANNEL` - имя канала, который будет забриджован. Это название едино для всех серверов.
3. `WORMHOLE_ENVIRONMENT` - тип окружения, в котором происходит запуск, может быть либо `test`, либо `prod` для
    тестового и продового окружения соответственно. Различия в функционировании в зависимости от окружения:
    
    1. В тестовом окружении для слэш-команд происходит их регистрация на всех серверах, но не глобально, так как 
        глобальная регистрация может занять до нескольких часов, что не очень удобно при отладке.
    2. Подход регистрации команд не глобально имеет один минус - при добавлении бота на новые сервер, что бы команды
        зарегистрировались, нужно перезапустить бота, поэтому в проде используется глобальная регистрация команд. 
"""

# Токен для авторизации тестового приложения:
token = environ['WORMHOLE_TOKEN_DISCORD']

# Название глобального канал:
# os.environ will raise a KeyError exception if there is
# no variable with such name in environment, so no checks required
globalchannel = environ['WORMHOLE_GLOBALCHANNEL']

# Тип окружения, в котором производится запуск
environment_type = environ['WORMHOLE_ENVIRONMENT'].lower()
assert environment_type in ['test', 'prod'], f"Wrong environment type: {environment_type}, must be 'test' or 'prod'"

# Имя файла база данных
db_file_name = 'Wormhole.sqlite'

# Описания глобального канала которое создаётся по команде Setup
channel_setup_description = '**Vox Galactica** - Wormhole / Глобальный чат серверов по Elite Dangerous'

# Список пользователей по ID которым будут выданы разрешения владельца
# Список даёт возможность использовать команды модерации
additional_owners: list = [
    478527700710195203,  # Politruk#6666
    258253761779204097,  # Sir Vizmiar#7731
]


# ------------- ОСНОВНЫЕ // КОНЕЦ


# ------------- СООБЩЕНИЯ

# Краткое описание приложения:
client_short_description = '''
Приложение для обмена текстовыми и файловыми сообщениями между серверами по игре Elite Dangerous
'''

# Полное описание приложения:
client_full_description = '''
Приложение создано для обмена текстовыми и файловыми сообщениями между серверами по игре [Elite Dangerous](https://www.elitedangerous.com/). В первую очередь приложение направлено помочь эскадронам с закрытыми серверами, обмениваться сообщениями с другими серверами и для тех серверов и пользователи которых предпочитают находится только на своём сервере по [Elite Dangerous](https://www.elitedangerous.com/). Для остальных же данное приложение может быть не так востребовано, но так как приложение не привязано к какому либо серверу, его можно использовать для серверов другой тематики.\n\nЕсли вы владеете одним из серверов по [Elite Dangerous](https://www.elitedangerous.com/) или связанной тематике и хотите подключить приложение к себе на сервер, воспользуйтесь данной [ссылкой]({invite_link}), либо можете на основе исходного кода данного приложения сделать свою сеть обмена сообщениями например по торговле или другой игре. Техническая поддержка: https://discord.gg/HFqmXPvMxC
'''

# Правила общения на глобальном канале:
globalchannel_rules = '''
```Запрещено притеснять, оскорблять или издеваться над участниками глобального чата.```
```Запрещено использовать чрезмерное количества сообщений, изображений, эмодзи, команд.```
```Запрещено поднимать темы касающиеся политики или религии. Эти сложные темы приводят к неоднозначным и оскорбительным сообщениям.```
```Запрещено распространять пиратский, сексуальный, NSFW или контент иного подозрительного содержания.```
```Запрещено распространять любую информацию личного характера. Защитите свою конфиденциальность и конфиденциальность других.```
```Запрещена реклама любого характера. Сюда входят нежелательные ссылки на социальные сети, серверы, сообщества и службы в чате или прямых сообщениях.```
```Рекомендуется не использоваться сообщения с матерными словами или использоваться мат в редких и исключительных случаях.```
'''


# ------------- СООБЩЕНИЯ // КОНЕЦ
