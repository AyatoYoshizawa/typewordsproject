from django.contrib.auth.models import User
from django.db import models

class WordList(models.Model):
    list_name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

class Word(models.Model):
    english = models.CharField(max_length=100)
    japanese = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    word_list_id = models.ForeignKey(WordList, on_delete=models.CASCADE)
    times_asked = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)

class Lesson(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson_number = models.IntegerField()
    word_id = models.ForeignKey(Word, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100, null=True)
    result = models.IntegerField(null=True)