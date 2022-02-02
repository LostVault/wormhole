# Python
FROM python:3.10.0-slim-buster

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y git

# Задаём рабочий каталог
RUN mkdir -p /workdir
WORKDIR /workdir

# Копируем файлы в рабочий каталог
COPY requirements.txt requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем файлы в рабочий каталог
COPY . .

# Выполняем команду
CMD [ "python3", "main.py"]