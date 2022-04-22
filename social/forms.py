from django import forms
from .models import Post, Comment, UserProfile
from crispy_forms.helper import FormHelper
from django.forms.widgets import HiddenInput
from crispy_forms.bootstrap import AppendedText, PrependedText, FormActions
from crispy_forms.layout import (
    Layout,
    Submit,
    Row,
    Column,
    Div,
    HTML,
    Field,
    Hidden,
    Button,
    ButtonHolder,
)


class PostForm(forms.ModelForm):
    images = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple': True,
        })
    )

    class Meta:
        model = Post
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"placeholder": "Tell us something today....", "rows": 5, "label": ""})
        }

    def __init__(self, *args, disabled_field=True, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # self.fields["images"].widget = HiddenInput()
        self.helper = FormHelper()
        self.helper.form_id = "createPostForm"
        self.fields["content"].label = ""
        self.fields["images"].label = ""
        self.helper.layout = Layout(
            Field("content"),
            Field("images"),
            # Submit("post-create", "Post")
        )


class UpdatePostForm(forms.ModelForm):
    images = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'multiple': True,
        })
    )

    class Meta:
        model = Post
        fields = ["content", "images"]
        widgets = {
            "content": forms.Textarea(attrs={"placeholder": "Tell us something today....", "rows": 5, "label": ""})
        }

    def __init__(self, *args, disabled_field=True, **kwargs):
        super(UpdatePostForm, self).__init__(*args, **kwargs)
        # self.fields["images"].widget = HiddenInput()
        self.helper = FormHelper()
        self.helper.form_id = "createPostForm"
        self.fields["content"].label = ""
        self.fields["images"].label = ""
        self.helper.layout = Layout(
            Field("content"),
            Field("images"),
            # Submit("post-create", "Post")
        )


class CommentPostForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ("avatar", "bio", "work_at", "location", "full_name",)
        widgets = {
            "bio": forms.Textarea(attrs={"placeholder": "Tell us about yourself....", "rows": 4, "label": "Biography:"})
        }

    def __init__(self, *args, disabled_field=True, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        # self.fields["images"].widget = HiddenInput()
        self.helper = FormHelper()
        self.helper.form_id = "UserProfileForm"
        self.helper.form_class = "d-none"
