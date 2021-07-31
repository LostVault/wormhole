# Wormhole
Приложение создана для обмена текстовыми и файловыми сообщениями между серверами по игре [Elite Dangerous](https://www.elitedangerous.com/). В первую очередь приложение направлено помочь эскадронам с закрытыми серверами, обмениваться сообщениями с другими серверами и для тех серверов и пользователи которых предпочитают находится только на своём сервере по [Elite Dangerous](https://www.elitedangerous.com/). Для остальных же данное приложение может быть не так востребовано, но так как приложение не привязано к какому либо серверу, его можно использовать для серверов другой тематики.

Если вы владеете одним из серверов по [Elite Dangerous](https://www.elitedangerous.com/) или связанной тематике и хотите подключить приложение к себе на сервер, воспользуйтесь ссылкой ниже, либо можете на основе исходного кода данного приложения сделать свою сеть обмена сообщениями например по торговле или другой игре.

- [Подключиь приложение на сервер](https://discordapp.com/oauth2/authorize?&client_id=826410895634333718&scope=bot&permissions=0)

## Команды
- Для владельца приложения
    - ping — Проверка состояния приложения
    - shutdown — Выключение приложения по команде
    - add — Внести пользователя в чёрный список
    - remove — Вынести пользователя из чёрного списка
    - servers — Показпть список серверов к которым подключенро приложение
    - leave_server — Отключить приложение от указанного сервера

- Для администратора сервера
    - clear — Удаление ста последних сообщений на канале
    - install — Создание канала для приёма и передачи сообщений 

- Для всех пользователей
    - information — Показать информацию о приложение

## Возможности

- База данных
- Отправка сообщений
- Отправка изображений
- Система Анти-Спам
- Система Анти-Флуд
    - Ограничение на отправку одного сообщения в минуту
- Чёрный список серверов
- Чёрный список пользователей
    - Добавление и удаление пользователя по команде
- Белый список сайтов
- Фильтр сообщений
    - Команды не выводятся в общий чат
- Команды управления приложением
    - Настройка приложения по команде
        - Создание канала
            - Добавление ID в список разрешённых 
            - Предварительная настройка канала 
    - Списко серверов
    - Отключение приложения от определённого сервера

## Запуск
Для запуска приложения необходимо задать две переменные окружения:
1. `WORMHOLE_TOKEN_0` - токен для бота, полученный с [Discord портала для разработчиков](https://discord.com/developers/applications)
2. `WORMHOLE_GLOBALCHANNEL` - название канала, которые будет забриджован. Это название едино для всех серверов.
## Запуск на Heroku
- Авторизуемся и создаём приложение на официальном [сайте](https://discord.com/developers/applications) Discord
