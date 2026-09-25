import logging
from urllib.parse import urlparse

from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, views as auth_views
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST
from core.forms import PasswordResetEmailDeliveryError, RegistroForm
from game.models import UserProfile

logger = logging.getLogger(__name__)


def _get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(usuario=user)
    return profile


class FinanceKidsPasswordResetView(auth_views.PasswordResetView):
    def get_extra_email_context(self):
        extra_email_context = dict(self.extra_email_context or {})
        public_base_url = getattr(settings, 'PUBLIC_BASE_URL', '')
        if public_base_url:
            parsed = urlparse(public_base_url)
            extra_email_context.update({
                'domain': parsed.netloc,
                'site_name': parsed.netloc,
                'protocol': parsed.scheme,
            })
        return extra_email_context

    def form_valid(self, form):
        original_extra_email_context = self.extra_email_context
        self.extra_email_context = self.get_extra_email_context()
        try:
            return super().form_valid(form)
        except PasswordResetEmailDeliveryError as exc:
            logger.warning(
                'Password reset email delivery failed for a submitted request: %s',
                exc.__cause__.__class__.__name__ if exc.__cause__ else exc.__class__.__name__,
            )
            return redirect(self.get_success_url())
        finally:
            self.extra_email_context = original_extra_email_context


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.email:
                try:
                    send_mail(
                        subject='Confirmación de inicio de sesión - FinanceKids',
                        message=(
                            f"Hola {user.get_full_name() or user.username},\n\n"
                            "Se ha iniciado sesión correctamente en FinanceKids.\n\n"
                            f"Usuario: {user.username}\n"
                            f"Fecha y hora: {timezone.localtime(timezone.now()).strftime('%d/%m/%Y %H:%M:%S')}\n"
                            f"IP: {request.META.get('REMOTE_ADDR', 'Desconocida')}\n\n"
                            "Si no fuiste tú, cambia tu contraseña inmediatamente."
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                except Exception:
                    messages.error(request, 'El inicio de sesión fue correcto, pero no se pudo enviar la confirmación por correo.')

            return redirect('index')
        return render(request, 'core/login.html', {'error': 'Usuario o contraseña incorrectos'})

    return render(request, 'core/login.html')


@login_required
def index(request):
    profile = _get_user_profile(request.user)
    progreso_actual = profile.ultimo_tema_desbloqueado
    progreso = {request.user.username: progreso_actual}
    return render(
        request,
        'core/index.html',
        {
            'progreso_actual': progreso_actual,
            'progreso': progreso,
        },
    )


@require_http_methods(['GET', 'POST'])
def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            return redirect('login')
        return render(request, 'core/registro.html', {'form': form})

    return render(request, 'core/registro.html', {'form': RegistroForm()})


@require_http_methods(['GET', 'POST'])
def logout_view(request):
    if request.method == 'GET':
        return render(request, 'core/logout_confirm.html')
    logout(request)
    return redirect('login')


@login_required
def aprendizaje(request, tema):
    if tema < 1 or tema > 3:
        raise Http404('Tema no encontrado')

    tema_actual = _get_user_profile(request.user).ultimo_tema_desbloqueado

    if tema > tema_actual:
        return render(request, "core/bloqueado.html", {"tema": tema})
    return render(request, f"core/aprendizaje{tema}.html")


@login_required
@require_POST
def completar_tema(request, tema):
    respuestas_correctas = {
        1: ('1', '1', '2'),
        2: ('1', '1'),
    }
    if tema not in respuestas_correctas:
        raise Http404('Tema no encontrado')

    profile = _get_user_profile(request.user)
    tema_actual = profile.ultimo_tema_desbloqueado

    # Solo avanzar si se completa exactamente el tema actual (evita saltar temas)
    respuestas = tuple(request.POST.get(f'respuesta_{indice}', '') for indice in range(1, len(respuestas_correctas[tema]) + 1))
    if tema != tema_actual or respuestas != respuestas_correctas[tema]:
        messages.error(request, 'Debes responder correctamente todas las preguntas antes de avanzar.')
        return redirect('preguntas1' if tema == 1 else 'preguntas2')

    profile.ultimo_tema_desbloqueado = tema + 1
    profile.save(update_fields=['ultimo_tema_desbloqueado'])

    siguiente_tema = tema + 1
    MAX_TEMAS = 10
    if siguiente_tema > MAX_TEMAS:
        return redirect('index')

    # Temas 4 en adelante aún en construcción
    ULTIMO_TEMA_DISPONIBLE = 3
    if siguiente_tema > ULTIMO_TEMA_DISPONIBLE:
        return redirect('construccion')

    return redirect('aprendizaje', tema=siguiente_tema)

@login_required
def juego1(request):
    return render(request, 'core/juego1.html')


@login_required
def preguntas1(request):
    return render(request, 'core/preguntas1.html')


@login_required
def juego2(request):
    return render(request, 'core/juego2.html')


@login_required
def preguntas2(request):
    return render(request, 'core/preguntas2.html')


@login_required
def construccion(request):
    return render(request, 'core/construccion.html')
