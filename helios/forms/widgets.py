from django import forms


class MultipleTextInput(forms.MultipleHiddenInput):
    input_type = 'text'
    is_hidden = False