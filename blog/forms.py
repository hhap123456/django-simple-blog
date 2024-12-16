from django.template.defaultfilters import title

from .models import Comment, Post
from django import forms

class TicketForm(forms.Form):
    SUBJECT_CHOICES = (
        ('پیشنهاد','پیشنهاد'),
        ('انتقاد', 'انتقاد'),
        ('گزارش', 'گزارش'),

    )
    massage = forms.CharField(widget=forms.Textarea, required=True)
    name = forms.CharField(max_length=250, required=True, widget=forms.TextInput(attrs={'placeholder':"نام",
                                                                                        'style':'height:50%;width:100a%;',
                                                                                        'class':'name',
                                                                                        }))
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
        widgets = {
            'body':forms.TextInput(attrs={'placeholder':'متن',
                                          'class':'cm-body',
                                          }),
            'name': forms.TextInput(attrs={'placeholder':'نام',
                                           'class': 'cm-body',
                                           }),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if name:
            if len(name) <3:
                raise forms.ValidationError("نام کوتاه است")
            else:
                return name


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'description','slug', 'reading_time',)

    def clean_title(self):
        title = self.cleaned_data['title']
        if title:
            if len(title) <3:
                raise forms.ValidationError("عنوان کوتاه است")
            else:
                return title

    def clean_reading_time(self):
        time = self.cleaned_data['reading_time']
        if time:
            if time > 0:
                return time
        else:
            raise forms.ValidationError("زمان مطالعه نمیتواند خالی باشد")

    def clean_description(self):
        description = self.cleaned_data['description']
        if description:
            if len(description) < 10:
                raise forms.ValidationError("توضیحات کوتاه است")
            else:
                return description

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        if slug:
            if len(slug) <4:
                raise forms.ValidationError("اسلاگ کوتاه است")
            else:
                return slug
