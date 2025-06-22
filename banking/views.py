from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from accounts.models import CustomUser
from .models import Account, Transaction, Loan
from .forms import FundTransferForm, DepositWithdrawForm, LoanRequestForm
# IMPORTANT: We are now importing our new, correct decorators
from .decorators import customer_and_approved_required, manager_required
from django.utils import timezone


@login_required
def dashboard(request):
    current_user = CustomUser.objects.get(pk=request.user.pk)
    
    # NEW: Check if account is frozen right after login
    if hasattr(current_user, 'account') and current_user.account.is_frozen:
        messages.error(request, "Your account is frozen. You cannot access the dashboard. Please contact support.")
        return redirect('logout') # Log them out immediately
    
    if current_user.is_staff:
        return redirect('manager_dashboard')
    if not current_user.is_approved:
        return render(request, 'banking/pending_approval.html')
    return redirect('customer_dashboard')

# --- CUSTOMER VIEWS ---
# Notice every view below uses the new, correct decorator.

@login_required
@customer_and_approved_required
def customer_dashboard(request):
    account = get_object_or_404(Account, user=request.user)
    transactions = account.transactions.all()[:10]
    context = {'account': account, 'transactions': transactions}
    return render(request, 'banking/customer_dashboard.html', context)


@login_required
@customer_and_approved_required
@transaction.atomic
def transfer_fund(request):
    sender_account = get_object_or_404(Account, user=request.user)
    
    # First, check if the sender's own account is frozen.
    if sender_account.is_frozen:
        messages.error(request, 'Your account is frozen. You cannot perform transactions.')
        return redirect('customer_dashboard')
        
    if request.method == 'POST':
        form = FundTransferForm(request.POST)
        if form.is_valid():
            # Get the clean data from the form
            amount = form.cleaned_data['amount']
            recipient_account_number = form.cleaned_data['recipient_account_number']

            # --- Start of Validation Checks ---
            
            # Check for sufficient funds
            if sender_account.balance < amount:
                messages.error(request, 'Insufficient funds.')
            
            # Check that user is not sending to themselves
            elif sender_account.account_number == recipient_account_number:
                messages.error(request, 'You cannot transfer funds to your own account.')
            
            else:
                # If initial checks pass, try to find the recipient
                try:
                    recipient_account = Account.objects.get(account_number=recipient_account_number)

                    # NEW: Check if the RECIPIENT's account is frozen
                    if recipient_account.is_frozen:
                        messages.error(request, "This recipient's account is frozen and cannot receive funds.")
                    
                    else:
                        # --- SUCCESS: All checks passed. Perform the transaction. ---
                        
                        # Debit sender
                        sender_account.balance -= amount
                        sender_account.save()
                        Transaction.objects.create(
                            account=sender_account, transaction_type='TRANSFER', amount=-amount,
                            description=f"Sent to {recipient_account.user.get_full_name()} ({recipient_account.account_number})"
                        )
                        
                        # Credit recipient
                        recipient_account.balance += amount
                        recipient_account.save()
                        Transaction.objects.create(
                            account=recipient_account, transaction_type='TRANSFER', amount=amount,
                            description=f"Received from {sender_account.user.get_full_name()} ({sender_account.account_number})"
                        )
                        
                        messages.success(request, f'Successfully transferred ${amount} to account {recipient_account_number}.')
                        return redirect('customer_dashboard')

                except Account.DoesNotExist:
                    messages.error(request, "The recipient account number does not exist.")
            
            # If any validation check failed, re-render the form page to show the error message.
            # We don't need an explicit 'return' here, as it will fall through to the final return.

    else:
        # This handles the initial GET request to the page
        form = FundTransferForm()
        
    return render(request, 'banking/transaction_form.html', {'form': form, 'title': 'Transfer Funds'})


@login_required
@customer_and_approved_required
def deposit_money(request):
    account = get_object_or_404(Account, user=request.user)
    if request.method == 'POST':
        form = DepositWithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            account.balance += amount
            account.save()
            Transaction.objects.create(
                account=account, transaction_type='DEPOSIT', amount=amount, description="Cash Deposit"
            )
            messages.success(request, f'${amount} has been deposited to your account.')
            return redirect('customer_dashboard')
    else:
        form = DepositWithdrawForm()
    return render(request, 'banking/transaction_form.html', {'form': form, 'title': 'Deposit Money'})


@login_required
@customer_and_approved_required
def withdraw_money(request):
    account = get_object_or_404(Account, user=request.user)
    if request.method == 'POST':
        form = DepositWithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if account.balance < amount:
                messages.error(request, 'Insufficient funds.')
            else:
                account.balance -= amount
                account.save()
                Transaction.objects.create(
                    account=account, transaction_type='WITHDRAWAL', amount=-amount, description="Cash Withdrawal"
                )
                messages.success(request, f'You have successfully withdrawn ${amount}.')
                return redirect('customer_dashboard')
    else:
        form = DepositWithdrawForm()
    return render(request, 'banking/transaction_form.html', {'form': form, 'title': 'Withdraw Money'})


@login_required
@customer_and_approved_required
def transaction_history(request):
    account = get_object_or_404(Account, user=request.user)
    transactions = account.transactions.all()
    return render(request, 'banking/transaction_history.html', {'transactions': transactions})


# --- MANAGER VIEWS --- (These remain unchanged and use the manager_required decorator)

@login_required
@manager_required
def manager_dashboard(request):
    context = {
        'pending_users': CustomUser.objects.filter(is_staff=False, is_approved=False).count(),
        'active_customers': CustomUser.objects.filter(is_staff=False, is_approved=True).count(),
        'total_transactions': Transaction.objects.count(),
        'pending_loans_count': Loan.objects.filter(status='PENDING').count(),
    }
    return render(request, 'banking/manager_dashboard.html', context)


@login_required
@manager_required
def customer_management(request):
    customers = CustomUser.objects.filter(is_staff=False, is_approved=True)
    return render(request, 'banking/customer_management.html', {'customers': customers})


@login_required
@manager_required
def customer_details(request, user_id):
    customer = get_object_or_404(CustomUser, id=user_id, is_staff=False)
    return render(request, 'banking/customer_details.html', {'customer': customer})


@login_required
@manager_required
def pending_approvals(request):
    users = CustomUser.objects.filter(is_staff=False, is_approved=False)
    return render(request, 'banking/pending_approvals.html', {'users': users})


@login_required
@manager_required
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f'User {user.username} has been approved and their account is now active.')
    return redirect('pending_approvals')


@login_required
@manager_required
def toggle_freeze_account(request, account_id):
    account = get_object_or_404(Account, id=account_id)
    account.is_frozen = not account.is_frozen
    account.save()
    status = "frozen" if account.is_frozen else "unfrozen"
    messages.success(request, f'Account {account.account_number} has been {status}.')
    return redirect('customer_details', user_id=account.user.id)

# --- CUSTOMER LOAN VIEW ---
@login_required
@customer_and_approved_required
def request_loan(request):
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.user = request.user
            loan.save()
            messages.success(request, 'Your loan request has been submitted successfully.')
            return redirect('customer_dashboard')
    else:
        form = LoanRequestForm()
    return render(request, 'banking/loan_request_form.html', {'form': form, 'title': 'Request a Loan'})

# --- MANAGER LOAN VIEWS ---
@login_required
@manager_required
def loan_requests_list(request):
    pending_loans = Loan.objects.filter(status='PENDING').order_by('requested_at')
    return render(request, 'banking/loan_requests_list.html', {'loans': pending_loans})

@login_required
@manager_required
@transaction.atomic
def process_loan(request, loan_id, action):
    loan = get_object_or_404(Loan, id=loan_id)
    
    # First, check if the loan has already been processed.
    if loan.status != 'PENDING':
        messages.error(request, 'This loan has already been processed.')
        return redirect('loan_requests_list')

    # Get the user's account to check its status
    user_account = loan.user.account

    if user_account.is_frozen:
        messages.error(request, f"Action failed: {loan.user.username}'s account is frozen. Please unfreeze the account before processing a loan.")
        return redirect('loan_requests_list')

    # If the account is NOT frozen, we can proceed.
    if action == 'approve':
        loan.status = 'APPROVED'
        
        # Deposit the loan amount into the user's account
        user_account.balance += loan.amount
        user_account.save()
        
        # Create a transaction record
        Transaction.objects.create(
            account=user_account,
            transaction_type='DEPOSIT',
            amount=loan.amount,
            description=f"Loan approved: {loan.reason[:50]}"
        )
        messages.success(request, f'Loan for {loan.user.username} has been approved and funds have been deposited.')
        
    elif action == 'deny':
        loan.status = 'DENIED'
        messages.warning(request, f'Loan for {loan.user.username} has been denied.')
    
    # Mark the loan as processed with the current time
    loan.processed_at = timezone.now()
    loan.save()
    
    return redirect('loan_requests_list')
