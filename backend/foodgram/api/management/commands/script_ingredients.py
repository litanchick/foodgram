import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from models import Ingredients


FILE_NAME = 'ingredients.csv'
MODEL = Ingredients
DATA_FORMAT = {'measurement_unit': 'measurement_unit_id'}


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
            value = []
            for cursor in data:
                args = dict(**cursor)
                if DATA_FORMAT:
                    for before, after in DATA_FORMAT.items():
                        args[after] = args.pop(before)
                value.append(MODEL(**args))
            MODEL.objects.bulk_create(
                value, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(
                f'{FILE_NAME[:-4]} - {len(value)} шт.'
            ))
        self.stdout.write(
            'Загрузка данных окончена.'
        )
