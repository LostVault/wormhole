## ОСНОВНЫЕ
from os import environ

# Токен для авторизации тестового приложения:
token = environ['WORMHOLE_TOKEN_0']

# Название глобального канал:
globalchannel = environ['WORMHOLE_GLOBALCHANNEL']
# os.environ will raise a KeyError exception if there is
# no variable with such name in environment, so no checks required

# Преффикс комманд:
prefix = '!'

## ОСНОВЫНЕ // КОНЕЦ
