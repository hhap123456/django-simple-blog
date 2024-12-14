from random import choices
from .models import Comment
from django import forms

class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد','پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش'),

    )
    massage = forms.CharField(widget=forms.Textarea, required=True)
    name = forms.CharField(max_length=250, required=True)
    email = forms.EmailField()
    phone = forms.CharField(max_length=11, required=True)
    subject = forms.ChoiceField(choices=SUBJECT_CHOICES)


    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if phone:
            if not phone.isnumeric():
                raise forms.ValidationError("شماره تلفن عددی نیست")
            elif len(phone) != 11:
                raise forms.ValidationError("شماره تلفن باید 11 رقم باشد")
            else:
                return phone

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'body')
