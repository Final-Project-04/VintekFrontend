from django import forms

class PaymentMethodForm(forms.Form):
    PAYMENT_CHOICES = (
        ('paypal', 'PayPal'),
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
    )

    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES)



class CreditCardPaymentForm(forms.Form):
    card_number = forms.CharField(max_length=16)
    card_holder = forms.CharField(max_length=255)
    expiry_month = forms.IntegerField(min_value=1, max_value=12)
    expiry_year = forms.IntegerField(min_value=2022)
    cvv = forms.CharField(max_length=3)

class PaypalPaymentForm(forms.Form):
    paypal_email = forms.EmailField()

class BankTransferPaymentForm(forms.Form):
    bank_name = forms.CharField(max_length=255)
    account_number = forms.CharField(max_length=255)
    sort_code = forms.CharField(max_length=255)