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

# ID сервера - для регистрации команд с косой чертой (slash) на севере:
guild_ids = [866758975345393734]
# Если не указывать ID то команда будет регистрировать глоадбное, что занимает около одного часа


## ОСНОВЫНЕ // КОНЕЦ


