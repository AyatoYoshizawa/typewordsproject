from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('word/<int:word_list_pk>', views.WordListView.as_view(), name='word-list'),
    path('word/<int:word_list_pk>>create', views.WordCreateView.as_view(), name='word-create'),
    path('word/<int:word_pk>/delete', views.WordDeleteView.as_view(), name='word-delete'),
    path('word/<int:word_pk>/update', views.WordUpdateView.as_view(), name='word-update'),
    path('typewords/', views.type_words_view, name='type-words'),
    path('result/', views.result_view, name='result'),
    path('start/', views.start_view, name='start'),
    path('list/', views.WordListListView.as_view(), name='word-list-list'),
    path('list/create', views.WordListCreateView.as_view(), name='word-list-create'),
    path('list/<int:word_list_pk>/update', views.WordListUpdateView.as_view(), name='word-list-update'),
    path('list/<int:word_list_pk>/delete', views.WordListDeleteView.as_view(), name='word-list-delete')
]