from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('word/', views.ListWordView.as_view(), name='list-word'),
    path('word/create', views.CreateWordView.as_view(), name='create-word'),
    path('word/<int:pk>/delete', views.DeleteWordView.as_view(), name='delete-word'),
    path('word/<int:pk>/update', views.UpdateWordView.as_view(), name='update-word'),
    path('typewords/', views.type_words_view, name='type-words'),
    path('result/', views.result_view, name='result'),
    path('start/', views.start_view, name='start'),
    path('list/', views.ListListView.as_view(), name='list-list'),
    path('list/create', views.CreateListView.as_view(), name='create-list'),
    path('list/<int:pk>/update', views.UpdateListView.as_view(), name='update-list'),
    path('list/<int:pk>/delete', views.DeleteListView.as_view(), name='delete-list')
]