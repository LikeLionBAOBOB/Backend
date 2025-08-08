from django.db import models


# abstractuser 상속 받지 않고 그냥 모델 두 개로.... -> 가능할지...?
# class User(models.Model):
#     username = models.CharField(max_length=150, unique=True, null=True, blank=True)
#     phone = models.CharField(max_length=20, unique=True, null=True, blank=True)

#     def __str__(self):
#         return self.username


# class Manager(models.Model):
#     username = models.CharField(max_length=150, unique=True, null=True, blank=True)
#     email = models.EmailField(unique=True, null=True, blank=True)
#     password = models.CharField(max_length=128)

#     def __str__(self):
#         return self.username