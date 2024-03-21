from django.contrib.auth.models import User
from django.db import models

class Words_Translations(models.Model):
    english = models.CharField(max_length=100)
    japanese = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_translations')

class Lesson(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons')
    num_of_lesson = models.IntegerField()
    word_translation = models.ForeignKey(Words_Translations, on_delete=models.CASCADE, related_name='lessons')
    answer = models.CharField(max_length=10, null=True)
    result = models.IntegerField(null=True)