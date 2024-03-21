from django import forms

class AnswerForm(forms.Form):
    inputted_ans = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'autofocus': 'autofocus'}))
    word_id = forms.IntegerField(widget=forms.HiddenInput)