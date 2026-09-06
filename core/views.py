from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from core.forms import RegistroForm
from game.models import UserProfile


def _get_user_profile(user):
    profile, _ = UserProfile.objects.get_or_create(usuario=user)
    return profile


def _resolve_auth_username(identifier):
    if not identifier or '@' not in identifier:
        return identifier

    profile = UserProfile.objects.select_related('usuario').filter(
        email_tutor__iexact=identifier
    ).first()
    return profile.usuario.username if profile is not None else identifier


def _email_validation_rate_limited(request):
    limit = 10
    window_seconds = 60
    session_key = 'email_validation_attempts'
    now = timezone.now().timestamp()
    attempts = [
        timestamp
        for timestamp in request.session.get(session_key, [])
        if now - timestamp < window_seconds
    ]
    if len(attempts) >= limit:
        request.session[session_key] = attempts
        return True

    attempts.append(now)
    request.session[session_key] = attempts
    return False


@require_http_methods(['GET', 'POST'])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        identifier = (request.POST.get('identifier') or request.POST.get('username') or '').strip()
        password = request.POST.get('password')
        user = authenticate(
            request,
            username=_resolve_auth_username(identifier),
            password=password,
        )

        if user is not None:
            login(request, user)
            return redirect('index')
        return render(
            request,
            'core/login.html',
            {
                'error': 'Usuario o contraseña incorrectos.',
                'login_identifier': identifier,
            },
        )

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
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            return redirect('login')
        return render(request, 'core/registro.html', {'form': form})

    return render(request, 'core/registro.html', {'form': RegistroForm()})


@require_http_methods(['GET'])
def validar_email_tutor(request):
    if _email_validation_rate_limited(request):
        return JsonResponse(
            {'available': False, 'message': 'Valida nuevamente en unos segundos.'},
            status=429,
        )

    email = request.GET.get('email', '').strip().lower()
    if not email:
        return JsonResponse({'available': False, 'message': 'Ingresa un correo electrónico.'})

    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'available': False, 'message': 'Ingresa un correo electrónico válido.'})

    exists = UserProfile.objects.filter(email_tutor__iexact=email).exists()
    return JsonResponse(
        {
            'available': not exists,
            'message': 'Correo disponible.' if not exists else 'Este correo ya está registrado.',
        }
    )


@require_http_methods(['GET', 'POST'])
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def aprendizaje(request, tema):
    tema_actual = _get_user_profile(request.user).ultimo_tema_desbloqueado

    if tema > tema_actual:
        return render(request, 'core/bloqueado.html', {'tema': tema})
    return render(request, f'core/aprendizaje{tema}.html')


@login_required
@require_POST
def completar_tema(request, tema):
    profile = _get_user_profile(request.user)
    tema_actual = profile.ultimo_tema_desbloqueado

    if tema == tema_actual:
        profile.ultimo_tema_desbloqueado = tema + 1
        profile.save(update_fields=['ultimo_tema_desbloqueado'])

    siguiente_tema = tema + 1
    max_temas = 10
    if siguiente_tema > max_temas:
        return redirect('index')

    ultimo_tema_disponible = 3
    if siguiente_tema > ultimo_tema_disponible:
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
