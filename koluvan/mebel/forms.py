from django import forms
from django.core.validators import RegexValidator


class RequestCallBackForm(forms.Form):
    name = forms.CharField(
        min_length=2,
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ваше имя'
        }),
        error_messages={
            'min_length': 'Имя должно быть длиной более 1 буквы',
            'max_length': 'Имя должно быть длиной не более 50 букв',
            'required': 'Заполните пожалуйста поле имени',
        }
    )

    phone = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'tel'
        }),
        error_messages={
            'required': 'Введите номер телефона',
        },
        validators=[
            RegexValidator(
                regex=r'^\+7\s?\(\d{3}\)\s?\d{3}-\d{2}-\d{2}$',
                message="Введите номер в формате: '+7 (XXX) XXX-XX-XX'"
            )
        ]
    )

    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Ваши пожелания или вопросы',
            'rows': 3
        })
    )

    category = forms.CharField(  # Используем CharField вместо ChoiceField
        label='Интересующая категория',
        required=False,
        error_messages={
            'required': 'Пожалуйста, выберите категорию'
        }
    )

    def clean_phone(self):
        phone = self.cleaned_data['phone']

        # Удаляем все символы, кроме цифр
        clean_phone = ''.join(filter(str.isdigit, phone))

        # Проверяем длину (11 цифр с учетом +7)
        if len(clean_phone) != 11:
            raise forms.ValidationError("Номер должен содержать 11 цифр")

        # Проверяем, что номер начинается с 7 или 8
        if not clean_phone.startswith(('7', '8')):
            raise forms.ValidationError("Неверный код страны")

        # Форматируем номер в стандартный вид
        return '+7' + clean_phone[1:]