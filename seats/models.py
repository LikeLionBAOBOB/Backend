from django.db import models


class Seat(models.Model):
    library = models.ForeignKey('libraries.Library', on_delete=models.CASCADE, related_name='seats')
    seat_number = models.IntegerField(null=False)  # 좌석 번호

    def __str__(self):
        return f"{self.library.title} - 좌석 {self.seat_number}"
