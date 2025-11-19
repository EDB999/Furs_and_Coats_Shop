import random
from django.core.management.base import BaseCommand
from Furs_and_Coats_App.models import Category, Product


def generate_description(name, material, color):
    descriptions = [
        f"Роскошная {name.lower()} из {material.lower()}. "
        f"Цвет: {color}. Идеально подходит для холодной зимы. "
        f"Высокое качество пошива и материалов.",

        f"Элегантная {name.lower()} премиум-класса. "
        f"Материал: {material}. Цвет: {color}. "
        f"Отличное сочетание стиля и комфорта.",

        f"Стильная {name.lower()} для настоящих ценителей. "
        f"Изготовлена из {material.lower()}. Цвет: {color}. "
        f"Гарантия качества и неповторимого образа.",
    ]
    return random.choice(descriptions)


class Command(BaseCommand):
    help = 'Заполняет базу данных 100 товарами верхней одежды'

    def handle(self, *args, **options):
        # Создаем категории
        fur_coats_category, created = Category.objects.get_or_create(
            name='Шубы'
        )
        coats_category, created = Category.objects.get_or_create(
            name='Пальто'
        )

        # Данные для генерации товаров
        FUR_NAMES = [
            'Шуба норковая классическая', 'Шуба норковая длинная',
            'Шуба норковая короткая', 'Шуба норковая приталенная',
            'Шуба песцовая роскошная', 'Шуба песцовая белая',
            'Шуба чернобурка элегантная', 'Шуба лисья рыжая',
            'Шуба енотовая теплая', 'Шуба мутон стильная',
            'Шуба каракульча эксклюзивная', 'Шуба соболиная премиум'
        ]

        COAT_NAMES = [
            'Пальто шерстяное классическое', 'Пальто шерстяное демисезонное',
            'Пальто кашемировое элегантное', 'Пальто кашемировое приталенное',
            'Пальто драповое теплое', 'Пальто драповое зимнее',
            'Пальто двубортное стильное', 'Пальто прямого кроя',
            'Пальто с капюшоном', 'Пальто с поясом'
        ]

        MATERIALS = {
            'шубы': ['Натуральная норка', 'Песец', 'Чернобурка', 'Лисица', 'Енот', 'Мутон', 'Каракуль', 'Соболь'],
            'пальто': ['Шерсть', 'Кашемир', 'Драп', 'Кашемир-шерсть', 'Альпака', 'Ангора']
        }

        COLORS = [
            'Черный', 'Белый', 'Коричневый', 'Шоколадный', 'Карамельный',
            'Серый', 'Бежевый', 'Рыжий', 'Темно-синий', 'Кремовый'
        ]

        SIZES = ['42', '44', '46', '48', '50', '52', '54']

        products_to_create = []

        for i in range(100):
            # Чередуем шубы и пальто
            if i % 2 == 0:
                category = fur_coats_category
                name = random.choice(FUR_NAMES)
                material = random.choice(MATERIALS['шубы'])
                price_range = (20000, 500000)
            else:
                category = coats_category
                name = random.choice(COAT_NAMES)
                material = random.choice(MATERIALS['пальто'])
                price_range = (7000, 300000)

            color = random.choice(COLORS)

            # Создаем продукт
            product = Product(
                name=f"{name} {color}",
                description=generate_description(name, material, color),
                price=random.randint(price_range[0], price_range[1]),
                category=category,
                material=material,
                size=random.choice(SIZES),
                color=color,
                in_stock=True,
                image='products/default.jpg'
            )
            products_to_create.append(product)

        # Массовое создание продуктов
        Product.objects.bulk_create(products_to_create)

        self.stdout.write(
            self.style.SUCCESS(
                f'Успешно создано 100 товаров: {len([p for p in products_to_create if p.category == fur_coats_category])} шуб и '
                f'{len([p for p in products_to_create if p.category == coats_category])} пальто. Все товары в наличии!'
            )
        )

