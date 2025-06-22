from django import forms
from .models import Account, Loan

class FundTransferForm(forms.Form):
    recipient_account_number = forms.CharField(label='Recipient Account Number', max_length=10)
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

    def clean_recipient_account_number(self):
        account_number = self.cleaned_data['recipient_account_number']
        if not Account.objects.filter(account_number=account_number).exists():
            raise forms.ValidationError("Recipient account does not exist.")
        return account_number

class DepositWithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=0.01)

class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['amount', 'reason']