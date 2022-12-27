import csv
import os.path

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Команда 'load_ingredients' загружает ингредиенты
    в базу из csv файла, который располагается в
    директории /data/
    """

    def handle(self, *args, **options):
        self.import_ingredients()
        print('Загрузка ингредиентов завершена.')

    def import_ingredients(self, file='ingredients.csv'):
        print(f'Загрузка {file}...')
        file_path = os.path.join('./data/', file)
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                status, created = Ingredient.objects.update_or_create(
                    name=row[0],
                    measurement_unit=row[1]
                )
