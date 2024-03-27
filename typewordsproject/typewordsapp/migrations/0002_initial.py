# Generated by Django 4.2.5 on 2024-03-27 10:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('typewordsapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='List',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='list', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Words_Translations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('english', models.CharField(max_length=100)),
                ('japanese', models.CharField(max_length=100)),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='list', to='typewordsapp.list')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='word_translations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_of_lesson', models.IntegerField()),
                ('answer', models.CharField(max_length=10, null=True)),
                ('result', models.IntegerField(null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to=settings.AUTH_USER_MODEL)),
                ('word_translation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='typewordsapp.words_translations')),
            ],
        ),
    ]