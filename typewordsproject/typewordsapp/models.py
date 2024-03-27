from django.contrib.auth.models import User
from django.db import models

class WordList(models.Model):
    list_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='list')

class Word(models.Model):
    english = models.CharField(max_length=100)
    japanese = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_translations')
    word_list_id = models.ForeignKey(WordList, on_delete=models.CASCADE, related_name='list')

class Lesson(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lessons')
    lesson_number = models.IntegerField()
    word_id = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='lessons')
    answer = models.CharField(max_length=100, null=True)
    result = models.IntegerField(null=True)