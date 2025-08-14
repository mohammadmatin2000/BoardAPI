from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
# ======================================================================================================================
# مدل اصلی بازی
class Game(models.Model):
    STATUS_CHOICES = [
        ('P', 'در حال بازی'),  # بازی در حال انجام
        ('W', 'برد'),  # بازی با برد بازیکن تمام شده
        ('D', 'مساوی'),  # بازی مساوی شده
    ]
    player = models.ForeignKey(User, on_delete=models.CASCADE)  # بازیکن اصلی
    board_state = models.JSONField(default=list)  # وضعیت فعلی تخته (ماتریس یا لیست)
    turn = models.CharField(max_length=1, default='P')  # نوبت کی هست
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')  # وضعیت بازی
    created_date = models.DateTimeField(auto_now_add=True)  # زمان ایجاد بازی
    updated_date = models.DateTimeField(auto_now=True)      # آخرین بروزرسانی
# ======================================================================================================================
# مدل حرکات
class Move(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='moves')  # بازی مربوطه
    player = models.CharField(max_length=10)  # مشخص می‌کنه حرکت مربوط به 'human' یا 'AI' هست
    position = models.JSONField()  # موقعیت یا مختصات حرکت
    created_date = models.DateTimeField(auto_now_add=True)  # زمان انجام حرکت
    updated_date = models.DateTimeField(auto_now=True)
# ======================================================================================================================