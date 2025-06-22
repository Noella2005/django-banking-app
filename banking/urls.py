from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Customer URLs
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('transfer/', views.transfer_fund, name='transfer_fund'),
    path('deposit/', views.deposit_money, name='deposit_money'),
    path('withdraw/', views.withdraw_money, name='withdraw_money'),
    path('history/', views.transaction_history, name='transaction_history'),
    path('loan/request/', views.request_loan, name='request_loan'),

    # Manager URLs
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('manager/customers/', views.customer_management, name='customer_management'),
    path('manager/customers/<int:user_id>/', views.customer_details, name='customer_details'),
    path('manager/approvals/', views.pending_approvals, name='pending_approvals'),
    path('manager/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('manager/freeze/<int:account_id>/', views.toggle_freeze_account, name='toggle_freeze_account'),
    path('manager/loans/', views.loan_requests_list, name='loan_requests_list'),
    path('manager/loans/<int:loan_id>/<str:action>/', views.process_loan, name='process_loan'),
]