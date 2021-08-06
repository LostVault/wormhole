# ОСНОВНЫЕ
from os import environ

# Токен для авторизации тестового приложения:
token = environ['WORMHOLE_TOKEN_0']

# Название глобального канал:
globalchannel = environ['WORMHOLE_GLOBALCHANNEL']
# os.environ will raise a KeyError exception if there is
# no variable with such name in environment, so no checks required

# Префикс команд:
prefix = '!'

# тип окружения, в котором производится запуск, подробности в README.md
environment_type = environ['WORMHOLE_ENVIRONMENT'].lower()
assert environment_type in ['test', 'prod'], f"Wrong environment type: {environment_type}, must be 'test' or 'prod'"

# ОСНОВНЫЕ // КОНЕЦ
