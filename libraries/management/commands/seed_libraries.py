from django.core.management.base import BaseCommand
from libraries.models import Library

LIB_CODES = [
    111179,  # 남가좌새롬도서관
    111051,  # 이진아기념도서관
    111252,  # 홍은도담도서관
    111086,  # 마포구립 서강도서관
    711596,  # 마포나루 스페이스
    111514,  # 마포소금나루도서관
    111467,  # 마포중앙도서관
    111257,  # 해오름 작은도서관
]

class Command(BaseCommand):
    help = "Seed initial library codes into the Library table"

    def handle(self, *args, **kwargs):
        for code in LIB_CODES:
            obj, created = Library.objects.get_or_create(lib_code=code)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Library with code {code}"))
            else:
                self.stdout.write(f"Library with code {code} already exists")
