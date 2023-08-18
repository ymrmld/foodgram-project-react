# Foodgram
## для тех, кто явно не равнодушен к еде

Этот проект способен как поднять хорошее настроение, а также увеличить аппетит! Делитесь рецептами своих шедевров сколько угодно!

Проект Foodgram находится по адресу: https://pkittys.sytes.net/

## **Стэк технологий**

* [Python 3.9](https://www.python.org/downloads/)
* [Django 3.2.3](https://www.djangoproject.com/download/)
* [djangorestframework 3.12.4](https://pypi.org/project/djangorestframework/#files)
* [djoser 2.1.0](https://pypi.org/project/djoser/#files)
* [gunicorn 20.1.0](https://pypi.org/project/gunicorn/20.1.0/)
* [psycopg2-binary 2.9.6](https://pypi.org/project/psycopg2-binary/#files)
* [pytest-django 4.4.0](https://pypi.org/project/pytest-django/)
* [pytest-pythonpath 0.7.3](https://pypi.org/project/pytest-pythonpath/)
* [pytest 6.2.4](https://pypi.org/project/pytest/)
* [PyYAML 6.0](https://pypi.org/project/PyYAML/)

## Локальный запуск проекта

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/ymrmld/kittygram_final.git
cd kittygram_final
```

Cоздать и активировать виртуальное окружение, установить зависимости(команды для MacOS):

```bash
python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install --upgrade pip
    pip install -r backend/requirements.txt
```

Установите docker compose на свой компьютер.

Запустите проект через docker-compose:

```bash
docker compose -f docker-compose.yml up --build -d
```

Выполнить миграции:

```bash
docker compose -f docker-compose.yml exec backend python manage.py migrate
```

Выполнить импорт данных:

```bash
docker compose -f docker-compose.yml exec backend python manage.py importdata
```

Соберите статику и скопируйте ее:

```bash
docker compose -f docker-compose.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend cp -r /app/collect_static/. /static_backend/static_backend/

```

Создайте супер пользователя:

```bash
docker compose -f docker-compose.yml exec backend python manage.py createsuperuser

```

## .env

В корне проекта создайте файл .env и пропишите в него свои данные.

Пример:

```apache
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram
DB_HOST=db
DB_PORT=5432
DJANGO_KEY='ваш код безопасности Django'
```

Код Django можно получить:

```bash
sudo docker compose -f docker-compose.production.yml exec backend python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

```
