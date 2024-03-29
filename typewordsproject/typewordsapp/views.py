from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import *

from pprint import pprint

from .forms import AnswerForm
from django.db.models.functions import Random

from django.db import transaction

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.DEBUG)

def index_view(request):
    return render(request, 'typewordsapp/index.html')

# type_words_viewに関する関数
def start_lesson(user):
    word_list = Word.objects.order_by(Random()).all()[:10]
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

def get_next_lesson(num):
    return Lesson.objects.filter(result=None, num_of_lesson=num).first()

def get_word_by_id(lesson) -> Word:
    return Word.objects.filter(id=lesson.word_translation.id).first()

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
        word = Word.objects.filter(id=lesson.word_translation.id).first()
        item_list.append({
            'lesson' : lesson,
            'word' : word,
        })
    context = {
        'item_list' : item_list,
    }
    return render(request, 'typewordsapp/result.html', context)

# WordListテーブルのCRUD
class WordListListView(LoginRequiredMixin, ListView):
    template_name = 'typewordsapp/word_list_list.html'
    model = WordList

    # 自分が作成したデータのみを取得
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(created_by=self.request.user.id)
        return queryset

class WordListCreateView(LoginRequiredMixin, CreateView):
    template_name = 'typewordsapp/word_list_create.html'
    model = WordList
    fields = ('list_name',)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['list_name'].widget.attrs['autofocus'] = True
        return form

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('list-list')

class WordListUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'typewordsapp/word_list_update.html'
    model = WordList
    fields = ('list_name',)
    pk_url_kwarg = 'word_list_pk'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['list_name'].widget.attrs['autofocus'] = True
        return form

    # 一覧に戻るリンクでパスパラメータword_list_pkを指定するためにコンテキストとしてword_list_pkを渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        word_list_pk = self.request.session.get('word_list_pk')
        context['word_list_pk'] = word_list_pk
        return context

    def get_success_url(self):
        word_list_pk = self.request.session.get('word_list_pk')
        return reverse_lazy('word-list', kwargs={'word_list_pk': word_list_pk})
    
class WordListDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'typewordsapp/word_list_confirm_delete.html'
    model = WordList
    fields = ('list_name',)
    success_url = reverse_lazy('list-list')

# WordテーブルのCRUD
class WordListView(LoginRequiredMixin, ListView):
    template_name = 'typewordsapp/word_list.html'
    model = Word

    # URLのパスパラメータ(現在選択している単語リストのID)をセッションのword_list_pkに保存
    def get(self, request, *args, **kwargs):
        word_list_pk = int(kwargs.get('word_list_pk'))
        self.request.session['word_list_pk'] = word_list_pk
        return super().get(request, *args, **kwargs)

    # Wordテーブルから、word_list_idフィールドがセッションのword_list_pkと一致するWordレコードを取得
    def get_queryset(self):
        queryset = super().get_queryset()
        word_list_pk = self.request.session.get('word_list_pk')
        queryset = queryset.filter(word_list_id=word_list_pk, created_by=self.request.user.id)
        return queryset
    
    # 現在選択している単語リストのWordListレコードをセッションのword_list_idでフィルターをかけて1件取得
    # 単語リストの名前を上に表示する為
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        word_list_pk = self.request.session.get('word_list_pk')
        selected_word_list =  WordList.objects.filter(pk=word_list_pk).first()
        context['selected_word_list'] = selected_word_list
        return context

class WordCreateView(LoginRequiredMixin, CreateView):
    template_name = 'typewordsapp/word_create.html'
    model = Word
    fields = ('english', 'japanese',)

    # created_byとword_list_idフィールドを自動で入力
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        word_list_pk = self.request.session.get('word_list_pk')
        word_list_instance = WordList.objects.get(pk=word_list_pk)
        form.instance.word_list_id = word_list_instance
        response = super().form_valid(form)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        word_list_pk = self.request.session.get('word_list_pk')
        context['word_list_pk'] = word_list_pk
        return context
    
    def get_success_url(self):
        word_list_pk = self.request.session.get('word_list_pk')
        return reverse_lazy('word-create', kwargs={'word_list_pk': word_list_pk})
    
class WordUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'typewordsapp/Word_update.html'
    model = Word
    fields = ('english', 'japanese',)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        word_list_pk = self.request.session.get('word_list_pk')
        context['word_list_pk'] = word_list_pk
        return context

    def get_success_url(self):
        word_list_pk = self.request.session.get('word_list_pk')
        return reverse_lazy('word-list', kwargs={'word_list_pk': word_list_pk})

class WordDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'typewordsapp/Word_confirm_delete.html'
    model = Word
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        word_list_pk = self.request.session.get('word_list_pk')
        context['word_list_pk'] = word_list_pk
        return context
    
    def get_success_url(self):
        word_list_pk = self.request.session.get('word_list_pk')
        return reverse_lazy('word-list', kwargs={'word_list_pk': word_list_pk})