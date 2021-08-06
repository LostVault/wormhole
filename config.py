# ОСНОВНЫЕ
from os import environ

# Токен для авторизации тестового приложения:
token = environ['WORMHOLE_TOKEN_DISCORD']

# Название глобального канал:
globalchannel = environ['WORMHOLE_GLOBALCHANNEL']
# os.environ will raise a KeyError exception if there is
# no variable with such name in environment, so no checks required

# Префикс команд:
prefix = '!'

# Тип окружения, в котором производится запуск, подробности в README.md
environment_type = environ['WORMHOLE_ENVIRONMENT'].lower()
assert environment_type in ['test', 'prod'], f"Wrong environment type: {environment_type}, must be 'test' or 'prod'"

# Краткое описание приложения:
client_short_description = "Приложение для обмена текстовыми и файловыми сообщениями между серверами по игре Elite Dangerous"

# Полное описание приложения:
client_full_description = 'Приложение создано для обмена текстовыми и файловыми сообщениями между серверами по игре [Elite ' \
                   'Dangerous](https://www.elitedangerous.com/). В первую очередь приложение направлено помочь ' \
                   'эскадронам с закрытыми серверами, обмениваться сообщениями с другими серверами и для тех серверов '\
                   'и пользователи которых предпочитают находится только на своём сервере по [Elite Dangerous](' \
                   'https://www.elitedangerous.com/). Для остальных же данное приложение может быть не так ' \
                   'востребовано, но так как приложение не привязано к какому либо серверу, его можно использовать ' \
                   'для серверов другой тематики.\n\nЕсли вы владеете одним из серверов по [Elite Dangerous](' \
                   'https://www.elitedangerous.com/) или связанной тематике и хотите подключить приложение к себе на ' \
                   'сервер, воспользуйтесь данной [ссылкой]({invite_link}), либо можете на основе исходного кода ' \
                   'данного приложения сделать свою сеть обмена сообщениями например по торговле или другой игре '


# ОСНОВНЫЕ // КОНЕЦ
