import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, "data")


class Command(BaseCommand):
    """Заполняем бд ингредиентами."""
    help = 'Импортируем данные из файла ingredients.csv'

    def add_arguments(self, parser):
        parser.add_argument('filename', default='ingredients.csv', nargs='?',
                            type=str)

    def handle(self, *args, **options):
        try:
            ingredients_list = []
            with open(os.path.join(DATA_ROOT, options['filename']), 'r',
                      encoding='utf-8') as file:
                data = csv.reader(file)
                next(data)
                for row in data:
                    name, measurement_unit = row
                    ingredients_list.append(
                        Ingredient(
                            name=name,
                            measurement_unit=measurement_unit
                        )
                    )
            Ingredient.objects.bulk_create(ingredients_list)
            self.stdout.write(self.style.SUCCESS('Ингредиенты добавлены'))
        except ValueError:
            print('Значение неопределенно')
        except Exception:
            print('Возникла непредвиденная ситуация')
