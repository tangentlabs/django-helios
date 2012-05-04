from django import forms
from django.utils.translation import ugettext_lazy as _
from helios.forms.widgets import MultipleTextInput


class MultipleCharField(forms.CharField):
    hidden_widget = forms.MultipleHiddenInput
    widget = MultipleTextInput
    default_error_messages = {
        'invalid_list': _(u'Enter a list of values.'),
        }

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise forms.ValidationError(self.error_messages['invalid_list'])
        return value

    def validate(self, value):
        super(MultipleCharField, self).validate(value)
        if self.required and not value:
            raise forms.ValidationError(self.error_messages['required'])