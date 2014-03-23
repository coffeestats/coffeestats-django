from django import forms
from django.utils.translation import ugettext as _

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from .models import (
    Action,
    Caffeine,
    User,
)


class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required fields, plus a
    repeated password.

    """
    password1 = forms.CharField(label=_('Password'),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password (again)'),
                                widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_password2(self):
        """
        Check that the two password entries match.

        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Passwords don't match"))
        return password2

    def save(self, commit=True):
        """
        Save the provided password in hashed format.

        """
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on the user, but
    replaces the password field with admin's password hash display field.

    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'location',
                  'timezone', 'is_superuser', 'is_staff', 'is_active')

    def clean_password(self):
        return self.initial['password']


class CaffeineUserAdmin(UserAdmin):
    """
    Custom admin page for users.
    """
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'location')}),
        (_('Permissions'), {
            'fields': ('is_superuser', 'is_staff', 'is_active', 'public')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}),
    )
    search_fields = ('username', 'email')
    ordering = ('username', 'email')
    filter_horizontal = ()


admin.site.register(Action)
admin.site.register(Caffeine)
admin.site.register(User, CaffeineUserAdmin)
