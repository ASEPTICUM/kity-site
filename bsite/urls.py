from django.urls import path
from bsite import views
from .decorators import check_recaptcha

urlpatterns = [
    path('', views.MainExchangeView.as_view(), name='index'),
    path('exchanges/top_up_balance/', views.TopUpBalanceView.as_view(), name="top_up_balance"),
    path('exchanges/withdrawal_balance/', views.WithdrawalView.as_view(), name="withdrawal_balance"),
    path('exchange/<str:str_id>', views.exchange, name='exchange'),
    path('confirm/<str:str_id>', views.other_index, name='confirm'),
    path('confirm_exchange/<str:str_id>', views.other_exchange, name='other_exchange'),
    path('questions/', views.questions, name='questions'),
    path('about_project/', views.about_project, name="about_project"),
    path('user/request/', views.request_view, name='request'),
    path('user/login/', views.user_login, name='login'),
    path('user/logout/', views.user_logout, name='logout'),
    path('user/activate/<str:uid>/<str:token>/', views.user_activate, name='user_activate'),
    path('user/register/', views.user_register, name='register'),
    path('user/register/confirm', views.user_register_confirm, name='register_confirm'),
    path('user/recover_password/', views.recover_password, name='recover_password'),
    path('user/profile/', views.user_profile, name='profile'),
    path('user/tg-confirm/<str:str>', views.user_tg_confirm, name='user_tg_confirm'),

    path('email_confirmed_page/', views.email_confirmed_page, name="email_confirmed"),

    path('amlkqc/', views.amlkqc, name='amlkqc'),
    path('reviews/', views.reviews, name='reviews'),
    path('tos/', views.tos, name='tos'),
    path('page/<str:title>/', views.page, name='page'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('password/reset/confirm/<str:uid>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
]



