from django import forms

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