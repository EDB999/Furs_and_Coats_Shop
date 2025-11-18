from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Check database connection'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()[0]
            print(f"✅ Django подключен к базе: {db_name}")

            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = cursor.fetchall()
            print("Таблицы в базе:")
            for table in tables:
                print(f" - {table[0]}")