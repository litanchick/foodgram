import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from api.models import Ingredients, Units

FILE_NAME = 'ingredients.csv'
DATA_FORMAT = {
    'measurement_unit': 'measurement_unit_id',
    'ingredient_name': 'name',
}


class Command(BaseCommand):
    help = 'Импортирует данные из файла csv в БД Ингредиентов.'

    def handle(self, *args, **kwargs):
        self.stdout.write(f'Выгружаем данные из файла: {FILE_NAME}')
        with open(
            f'{settings.BASE_DIR}/data/{FILE_NAME}', 'r', encoding='utf8'
        ) as datafile:
            if not datafile:
                raise CommandError(
                    f'В указанном месте нет файла {FILE_NAME}'
                )
            data = csv.DictReader(datafile)
            list_ingredients = []
            for cursor in data:
                args = dict(**cursor)
                unit, flag = Units.objects.get_or_create(
                    name=args['measurement_unit']
                )
                args['measurement_unit'] = unit
                list_ingredients.append(Ingredients(**args))
            Ingredients.objects.bulk_create(
                list_ingredients, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(
                f'{FILE_NAME[:-4]} - {len(list_ingredients)} шт.'
            ))
        self.stdout.write(
            'Загрузка данных окончена.'
        )
