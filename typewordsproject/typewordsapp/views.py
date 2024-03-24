from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Words_Translations
from .models import Lesson

from pprint import pprint

from .forms import AnswerForm
from django.db.models.functions import Random

from django.db import transaction

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.DEBUG)
# Create your views here.
def index_view(request):
    return render(request, 'typewordsapp/index.html')

def get_next_lesson(num):
    return Lesson.objects.filter(result=None, num_of_lesson=num).first()

def get_word_by_id(lesson) -> Words_Translations:
    return Words_Translations.objects.filter(id=lesson.word_translation.id).first()

def start_lesson(user):
    word_list = Words_Translations.objects.order_by(Random()).all()[:10]
    lesson_objects = Lesson.objects.aggregate(max_value=models.Max('num_of_lesson'))
    if lesson_objects['max_value'] == None:
        num = 1
    else:
        num = lesson_objects['max_value'] + 1
    with transaction.atomic():
        for word in word_list:
            obj = Lesson.objects.create(user=user, num_of_lesson=num, word_translation=word)
            obj.save()
    logging.debug(num)
    return num

def render_question(request, num):
    current_lesson = get_next_lesson(num)
    current_word = get_word_by_id(current_lesson)

    initial_values = {
        'num' : current_lesson.num_of_lesson,
        'word_id': current_lesson.word_translation.id,
    }
    form = AnswerForm(initial=initial_values)

    context = {
        'current_lesson' : current_lesson,
        'current_word' : current_word,
        'form' : form,
    }
    return render(request, 'typewordsapp/type_words.html', context)

@login_required
def start_view(request):
    user = request.user
    request.session['num'] = start_lesson(user)
    logging.debug(f"START: {request.session['num']}")
    return redirect('type-words')
    
def type_words_view(request):
    if request.method == 'GET':
        num = request.session.get('num')
        logging.debug(num)
        return render_question(request, num)
       
    elif request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            num = request.session.get('num')
            word_id = form.cleaned_data['word_id']
            logging.debug(num)
            print(word_id)

            lesson = Lesson.objects.filter(num_of_lesson=num, word_translation_id=word_id).first()
            word = get_word_by_id(lesson)

            cleaned_inputted_ans = form.cleaned_data['inputted_ans']
            lesson.answer = cleaned_inputted_ans
            if word.english == cleaned_inputted_ans:
                lesson.result = 1
            else:
                lesson.result = 0
            lesson.save()

            next_lesson = get_next_lesson(num)
            if next_lesson:
                return redirect('type-words')
            else:
                return redirect('result')
    
def result_view(request):
    num = request.session.get('num')
    item_list = []
    lesson_list = Lesson.objects.filter(num_of_lesson=num)
    for lesson in lesson_list:
        word = Words_Translations.objects.filter(id=lesson.word_translation.id).first()
        item_list.append({
            'lesson' : lesson,
            'word' : word,
        })
    context = {
        'item_list' : item_list,
    }
    return render(request, 'typewordsapp/result.html', context)

class ListWordView(LoginRequiredMixin, ListView):
    template_name = 'typewordsapp/words_translations_list.html'
    model = Words_Translations

class CreateWordView(LoginRequiredMixin, CreateView):
    template_name = 'typewordsapp/words_translations_create.html'
    model = Words_Translations
    fields = ('english', 'japanese')

    def form_valid(self, form):
        response = super().form_valid(form)
        return response
    
    def get_success_url(self):
        return reverse('create-word')

class DeleteWordView(LoginRequiredMixin, DeleteView):
    template_name = 'typewordsapp/words_translations_confirm_delete.html'
    model = Words_Translations
    success_url = reverse_lazy('list-word')

class UpdateWordView(LoginRequiredMixin, UpdateView):
    template_name = 'typewordsapp/words_translations_update.html'
    model = Words_Translations
    fields = ('english', 'japanese')
    success_url = reverse_lazy('list-word')