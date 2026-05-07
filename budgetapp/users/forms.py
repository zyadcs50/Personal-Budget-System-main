from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Expense, BudgetCycle, Profile



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['first_name', 'last_name' ,'username', 'email', 'password1', 'password2']



class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount']
        

class BudgetCycleForm(forms.ModelForm):
    class Meta:
        model = BudgetCycle
        fields = ['total_amount', 'start_date', 'end_date']
        
        widgets = {
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            for field in self.fields.values():
                field.widget.attrs.update({
                    'class': 'form-control'
                })


class ProfileForm(forms.ModelForm):
    

    class Meta:
        model = Profile
        fields = ['image']