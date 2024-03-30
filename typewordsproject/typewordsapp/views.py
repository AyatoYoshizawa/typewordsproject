from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import *

from pprint import pprint

from .forms import *

from django.db import transaction
from django.db.models import Case, When, Value, F, ExpressionWrapper, FloatField, Max

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.DEBUG)

def start_lesson(request) -> None:
    # correct_ratio(正答率)フィールドの昇順で、指定した出題数の分だけ取得する
    tmp_word_queryset = Word.objects.filter(created_by=request.user.id)
    tmp_word_queryset = tmp_word_queryset.annotate(
        correct_ratio=Case(
            When(times_asked=0, then=Value(0)), # times_asked=0の場合はcorrect_ratio=0にする
            default=ExpressionWrapper(
                F('times_correct') / F('times_asked'),
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    )
    total_num_of_lessons = request.session.get('total_num_of_lessons')
    word_objects = tmp_word_queryset.order_by('correct_ratio')[:total_num_of_lessons]

    # lesson_numberフィールド内の最大値を求めて、Noneだったら1で初期化。
    # そうでなければインクリメントしてcurrent_lesson_numberに格納し、セッションに保存
    lesson_objects = Lesson.objects.aggregate(max_value=Max('lesson_number'))
    if lesson_objects['max_value'] == None:
        current_lesson_number = 1
    else:
        current_lesson_number = lesson_objects['max_value'] + 1    
    request.session['current_lesson_number'] = current_lesson_number

    # 取得してきたword_objectをもとにLessonレコードを作成
    with transaction.atomic():
        for word_object in word_objects:
            obj = Lesson.objects.create(
                created_by=request.user,
                lesson_number=current_lesson_number,
                word_id=word_object,
                )
            obj.save()

# トップページ
@login_required
def index_view(request):
    if request.method == 'POST':
        form = LessonConfigForm(request.POST)
        if form.is_valid():
            # 出題する数をフォームから受け取りセッションに保存
            total_num_of_lessons = form.cleaned_data['max_lesson_number']
            request.session['total_num_of_lessons'] = total_num_of_lessons

            # start_lessonでレコードを作成
            start_lesson(request)
            return redirect('type-words')
    else:
        # 出題可能数の上限を取得して、それをデフォルト値と上限値に設定
        form = LessonConfigForm()
        max_value = Word.objects.filter(created_by=request.user.id).count()
        form.fields['max_lesson_number'].max_value = max_value
        form.fields['max_lesson_number'].initial = max_value
        return render(request, 'typewordsapp/index.html', {'form': form})

# 現在のレッスン番号かつ未回答のもので一番最初にヒットしたレコードを1件返す
def get_next_lesson_object(current_lesson_number):
    return Lesson.objects.filter(result=None, lesson_number=current_lesson_number).first()

# 現在のLessonレコードのword_idをもとにWordレコードを1件返す
def get_word_by_id(current_lesson):
    return Word.objects.filter(id=current_lesson.word_id.id).first()

# 現在のlesson_numberとword_idをAnswerFormのフィールドの初期値に設定
def render_question(request, current_lesson_number):
    current_lesson = get_next_lesson_object(current_lesson_number)
    current_word = get_word_by_id(current_lesson)

    initial_values = {
        'current_lesson_number' : current_lesson.lesson_number,
        'word_id': current_lesson.word_id.id,
    }
    form = AnswerForm(initial=initial_values)

    context = {
        'current_lesson' : current_lesson,
        'current_word' : current_word,
        'form' : form,
    }
    return render(request, 'typewordsapp/type_words.html', context)

# 単語テストページ
def type_words_view(request):
    if request.method == 'GET':
        current_lesson_number = request.session.get('current_lesson_number')
        return render_question(request, current_lesson_number)
       
    elif request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            current_lesson_number = request.session.get('current_lesson_number')
            current_word_id = form.cleaned_data['word_id']

            current_lesson = Lesson.objects.filter(lesson_number=current_lesson_number, answer=None)
            current_word = get_word_by_id(current_lesson)

            cleaned_inputted_ans = form.cleaned_data['inputted_ans']
            current_lesson.answer = cleaned_inputted_ans
            if current_word.english == cleaned_inputted_ans:
                current_lesson.result = 1
            else:
                current_lesson.result = 0
            current_lesson.save()

            next_lesson = get_next_lesson_object(current_lesson_number)
            if next_lesson:
                return redirect('type-words')
            else:
                return redirect('result')
    
def result_view(request):
    current_lesson_number = request.session.get('current_lesson_number')
    item_list = []
    lesson_list = Lesson.objects.filter(lesson_number=current_lesson_number)
    for lesson in lesson_list:
        word = Word.objects.filter(id=lesson.word_id.id).first()
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