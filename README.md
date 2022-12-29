# Foodgram
[![Foodgram workflow](https://github.com/SkyFlyer2/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/SkyFlyer2/foodgram-project-react/actions/workflows/main.yml)


Foodgram - онлайн-сервис для создания кулинарных рецептов. Позволяет публиковать рецепты, сохранять избранные, а также формировать список покупок для выбранных рецептов. Можно подписываться на авторов рецептов.


# Описание проекта

Foodgram - учебный проект курса "Python-разработчик" на Яндекс.Практикум. Реализована методика разработки CI/CD (Continuos Integration/Continuos Delivery).

## Ссылка на сайт
Сервис запущен по [адресу](http://158.160.4.20/).
Данные для входа:
пользователь:admin
почта: text@yandex.ru
пароль 123

пользователь: skyflyer1
почта: email@yandex.ru
welcome34


## Технологии
* Python 3.8
* Django 3.2
* Django REST Framework
* python-dotenv
* git
* PostreSQL
* Nginx
* gunicorn
* Docker
* DockerHub


## Порядок действий для развертывания и запуска сервиса:

Клонируйте репозиторий и перейдите в него в командной строке:

```
git clone https://github.com/SkyFlyer2/yamdb_final.git
```

Выполните вход на удаленный сервер
Установка docker:

```
sudo apt install docker.io
```

или

```
curl -fsSL https://get.docker.com -o get-docker.sh
DRY_RUN=1 sudo sh ./get-docker.sh
```

Установка docker-compose:
sudo apt-get install docker-compose-plugin

В файле infra/nginx.conf пропишите IP-адрес сервера:

```
server_name xxx.xxx.xxx.xxx;
```

Из каталога infra скопируйте на удаленный сервер файлы  docker-compose.yml и default.conf.

scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp -r nginx.conf <username>@<host>:/home/<username>/nginx/nginx.conf


Cоздайте файл ```.env```:

```bash 
touch .env
```

Заполните ```.env``` файл переменными окружения по примеру:
```bash 
echo SECRET_KEY=<уникальный токен> >> .env
echo DB_ENGINE=django.db.backends.postgresql >> .env
echo DB_NAME=<название базы данных postgre sql> l >> .env
echo POSTGRES_USER=<имя пользователя>  >> .env
echo POSTGRES_PASSWORD=<ваш пароль> >> .env
echo DB_HOST=db  >> .env
echo DB_PORT=5432  >> .env
```

Теперь можно установить и запустить приложение в контейнерах (контейнеры backend/frontend загружаются из DockerHub):
```bash 
sudo docker-compose up -d
```

Запуск миграций, создание суперюзера, сбор статики и заполнение БД:
```bash 
docker-compose exec backend python manage.py migrate

docker-compose exec backend python manage.py createsuperuser

docker-compose exec backend python manage.py collectstatic --no-input 

docker-compose exec backend python manage.py loaddata
```

Проект доступен по адресу `http://<IP адрес сервера>/`

Документация по API `http://<IP адрес сервера>/api/docs/`


**Примеры API-запросов**

* Запросы для всех пользователей

curl -H 'Accept: application/json' `http://<IP адрес сервера>/api/recipes/` - получить список рецептов

curl -H 'Accept: application/json' `http://<IP адрес сервера>/api/tags/categories/` - получить список тегов


**Аутентификация:**

* Создать учетную запись:

curl --header "Content-Type: application/json" --request POST --data '{"email":"email@email","username": "username","first_name": "Имя","last_name": "Фамилия","password": "пароль"}' `http://<IP адрес сервера>/api/users/`

* После создания учетной записи по следующему запросу можно получить токен для авторизации:

curl --header "Content-Type: application/json" --request POST --data '{"email":"email@email","password":"пароль"}' `http://<IP адрес сервера>/api/auth/token/login/`

**Доступные адреса проекта:**

    -  http://<IP адрес сервера>/ - главная страница;
    -  http://<IP адрес сервера>/admin/ - панель администрирования;
    -  http://<IP адрес сервера>/api/ - API проекта
    -  http://<IP адрес сервера>/api/docs/redoc.html - документация к API

## Автор

SkyFlyer, telegram: @skyflyer1
