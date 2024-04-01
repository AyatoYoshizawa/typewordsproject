from django import forms

class LessonConfigForm(forms.Form):
    max_lesson_number = forms.IntegerField(
        label='出題数',
        label_suffix='',
        initial=None,
        min_value=1,
        max_value=None, 
        widget=forms.NumberInput(attrs={
            'class': 'form-control bg-dark text-light',
            'style': 'width: 150px;',
        },
        )
    )
    # initialとmax_valueは後でindex_viewで指定する

class AnswerForm(forms.Form):
    inputted_ans = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'autofocus': 'autofocus',
            'class': 'form-control form-control-lg bg-soft-dark',
            'placeholder': '回答を入力してください',
            'autocomplete': 'off',
        }),
        label='',
    )
    word_id = forms.IntegerField(widget=forms.HiddenInput)