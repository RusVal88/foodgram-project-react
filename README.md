# Foodgram
## Продуктовый помощник»: 
### сайт для пользователей, на котором они могут создавать рецепты, добавлять чужие рецепты в избранное и список покупок, которые нужно купить для приготовления выбранных блюд, а также подписываться на публикации других авторов.

# Технологии:
- Python
- Django
- DRF
- SQLite3
- PostgeSQL

# Как запустить проект:
## Клонировать репозиторий и перейти в него в командной строке:
```
    git clone git@github.com:RusVal88/foodgram-project-react.git
```
```
    cd foodgram-project-react
```
## Cоздать и активировать виртуальное окружение:
```
    python3 -m venv env
```
```
    source venv/Scripts/activate
```
## Установить зависимости из файла requirements.txt:
```
    python3 -m pip install --upgrade pip
```
```
    pip install -r requirements.txt 
```
## Выполнить миграции:
```
    cd backend
```
```
    python3 manage.py migrate
```
## Заполнить базу данных данными:
```
    python manage.py loaddata data/ingredients.json
```
## Запуск Docker:
```
    sudo docker-compose up -d
```
## Выполнить миграции, создать суперпользователя и собрать статику.
```
    sudo docker-compose exec backend python manage.py migrate
```
```
    sudo docker-compose exec backend python manage.py createsuperuser
```
```
    sudo docker-compose exec backend python manage.py loaddata data/ingredients.json
```
```
    sudo docker-compose exec backend python manage.py collectstatic --no-input
```

## Тестовый аккаунт для админ-панели
```
    foodgramforyou.ddns.net

```
```
    email: ruslan.suhanoff@yandex.com
```
```
    password: ByD783kA
```
## Автор:
### Руслан Валишин
