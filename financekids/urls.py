from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from core import views
from core.forms import FinanceKidsPasswordResetForm, FinanceKidsSetPasswordForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('aprendizaje/<int:tema>/', views.aprendizaje, name='aprendizaje'),
    path('completar/<int:tema>/', views.completar_tema, name='completar_tema'),
    path('juego1/', views.juego1, name='juego1'),
    path('preguntas1/', views.preguntas1, name='preguntas1'),
    path('juego2/', views.juego2, name='juego2'),
    path('preguntas2/', views.preguntas2, name='preguntas2'),
    path('construccion/', views.construccion, name='construccion'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='core/password_reset.html',
        email_template_name='core/password_reset_email.html',
        success_url='/password_reset/done/',
        form_class=FinanceKidsPasswordResetForm,
    ), name='password_reset'),

    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html',
        success_url='/reset/done/',
        form_class=FinanceKidsSetPasswordForm,
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html'
    ), name='password_reset_complete'),
]