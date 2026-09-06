(function () {
    const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    function isValidEmail(value) {
        return EMAIL_RE.test(value.trim());
    }

    function isStrongPassword(value) {
        return value.length >= 8 && /[A-Z]/.test(value) && /\d/.test(value);
    }

    function isFutureDate(value) {
        if (!value) {
            return false;
        }
        const selected = new Date(`${value}T00:00:00`);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return selected > today;
    }

    function getErrorNode(input) {
        return document.querySelector(`[data-error-for="${input.id}"]`);
    }

    function setFieldState(input, message, options = {}) {
        const errorNode = getErrorNode(input);
        const showSuccess = options.success === true && !message;

        input.classList.toggle('is-invalid-live', Boolean(message));
        input.classList.toggle('is-valid-live', showSuccess);
        input.setAttribute('aria-invalid', message ? 'true' : 'false');

        if (!errorNode) {
            return !message;
        }

        if (message) {
            errorNode.textContent = message;
            errorNode.classList.add('is-visible');
            errorNode.classList.remove('is-success');
        } else if (showSuccess && options.successMessage) {
            errorNode.textContent = options.successMessage;
            errorNode.classList.add('is-visible', 'is-success');
        } else {
            errorNode.textContent = '';
            errorNode.classList.remove('is-visible', 'is-success');
        }

        return !message;
    }

    function togglePassword(inputId, iconId) {
        const input = document.getElementById(inputId);
        const icon = document.getElementById(iconId);
        if (!input || !icon) {
            return;
        }

        input.type = input.type === 'password' ? 'text' : 'password';
        icon.className = input.type === 'password' ? 'bi bi-eye-fill' : 'bi bi-eye-slash-fill';
    }

    function getPasswordLevel(value) {
        const levels = [
            { label: 'Seguridad: muy baja', width: '10%', color: '#D1D5DB' },
            { label: 'Seguridad: débil', width: '30%', color: '#ef4444' },
            { label: 'Seguridad: media', width: '55%', color: '#f97316' },
            { label: 'Seguridad: buena', width: '78%', color: '#1e96fc' },
            { label: 'Seguridad: fuerte 💪', width: '100%', color: '#00c97a' },
        ];
        let score = 0;
        if (!value) {
            return levels[0];
        }
        if (value.length >= 8) score += 1;
        if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score += 1;
        if (/\d/.test(value)) score += 1;
        if (/[^A-Za-z0-9]/.test(value)) score += 1;
        if (value.length >= 12) score += 1;
        return levels[Math.min(score, levels.length - 1)];
    }

    function paintStrength(input) {
        const fill = document.getElementById('strengthFill');
        const text = document.getElementById('strengthText');
        if (!fill || !text || !input) {
            return;
        }
        const level = getPasswordLevel(input.value);
        fill.style.width = level.width;
        fill.style.backgroundColor = level.color;
        text.textContent = level.label;
        text.style.color = level.color;
    }

    function validateLoginIdentifier(input) {
        const value = input.value.trim();
        if (!value) {
            return setFieldState(input, 'Ingresa tu correo electrónico o nombre de usuario.');
        }
        if (value.includes('@') && !isValidEmail(value)) {
            return setFieldState(input, 'Ingresa un correo electrónico válido.');
        }
        return setFieldState(input, '', { success: value.includes('@') });
    }

    async function validateTutorEmail(input, endpoint) {
        const value = input.value.trim().toLowerCase();
        if (!value) {
            return setFieldState(input, 'El email del tutor es obligatorio.');
        }
        if (!isValidEmail(value)) {
            return setFieldState(input, 'Ingresa un correo electrónico válido.');
        }
        if (!endpoint) {
            return setFieldState(input, '', { success: true, successMessage: 'Correo válido.' });
        }

        try {
            const response = await fetch(`${endpoint}?email=${encodeURIComponent(value)}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            });
            const data = await response.json();
            if (!data.available) {
                return setFieldState(input, data.message || 'Este correo ya está registrado.');
            }
            return setFieldState(input, '', { success: true, successMessage: data.message || 'Correo disponible.' });
        } catch (error) {
            return setFieldState(input, 'No pudimos validar el correo en este momento.');
        }
    }

    function validatePassword(input) {
        const value = input.value;
        if (!value) {
            return setFieldState(input, 'La contraseña es obligatoria.');
        }
        if (!isStrongPassword(value)) {
            return setFieldState(input, 'Usa mínimo 8 caracteres, una mayúscula y un número.');
        }
        return setFieldState(input, '', { success: true, successMessage: 'Contraseña válida.' });
    }

    function validatePasswordMatch(passwordInput, confirmInput) {
        const confirmValue = confirmInput.value;
        if (!confirmValue) {
            return setFieldState(confirmInput, 'Confirma tu contraseña.');
        }
        if (passwordInput.value !== confirmValue) {
            return setFieldState(confirmInput, 'Las contraseñas no coinciden.');
        }
        return setFieldState(confirmInput, '', { success: true, successMessage: 'Las contraseñas coinciden.' });
    }

    function validateBirthdate(input) {
        if (!input.value) {
            return setFieldState(input, '');
        }
        if (isFutureDate(input.value)) {
            return setFieldState(input, 'La fecha de nacimiento no puede estar en el futuro.');
        }
        return setFieldState(input, '', { success: true, successMessage: 'Fecha válida.' });
    }

    function initLoginValidation() {
        const form = document.getElementById('login-form');
        const identifier = document.getElementById('id_login_identifier');
        if (!form || !identifier) {
            return;
        }

        identifier.addEventListener('input', function () {
            validateLoginIdentifier(identifier);
        });
        identifier.addEventListener('blur', function () {
            validateLoginIdentifier(identifier);
        });

        form.addEventListener('submit', function (event) {
            if (!validateLoginIdentifier(identifier)) {
                event.preventDefault();
            }
        });
    }

    function initRegistroValidation() {
        const form = document.getElementById('registro-form');
        const email = document.getElementById('id_email_tutor');
        const password1 = document.getElementById('id_password1');
        const password2 = document.getElementById('id_password2');
        const birthdate = document.getElementById('id_fecha_nacimiento');
        if (!form || !email || !password1 || !password2 || !birthdate) {
            return;
        }

        const endpoint = form.dataset.emailCheckUrl;
        let emailRequest = 0;

        password1.addEventListener('input', function () {
            paintStrength(password1);
            validatePassword(password1);
            if (password2.value) {
                validatePasswordMatch(password1, password2);
            }
        });
        password2.addEventListener('input', function () {
            validatePasswordMatch(password1, password2);
        });
        birthdate.addEventListener('input', function () {
            validateBirthdate(birthdate);
        });

        async function runEmailValidation() {
            const requestId = emailRequest + 1;
            emailRequest = requestId;
            const valid = await validateTutorEmail(email, endpoint);
            return requestId === emailRequest ? valid : false;
        }

        email.addEventListener('input', function () {
            if (!email.value.trim()) {
                setFieldState(email, 'El email del tutor es obligatorio.');
                return;
            }
            if (!isValidEmail(email.value)) {
                setFieldState(email, 'Ingresa un correo electrónico válido.');
                return;
            }
            setFieldState(email, '', { success: true, successMessage: 'Validando disponibilidad...' });
        });
        email.addEventListener('blur', function () {
            runEmailValidation();
        });

        form.addEventListener('submit', async function (event) {
            event.preventDefault();
            const checks = [
                validatePassword(password1),
                validatePasswordMatch(password1, password2),
                validateBirthdate(birthdate),
                await runEmailValidation(),
            ];
            if (checks.every(Boolean)) {
                form.submit();
            }
        });

        paintStrength(password1);
    }

    window.FinanceKidsValidation = {
        initLoginValidation,
        initRegistroValidation,
        togglePassword,
    };

    document.addEventListener('DOMContentLoaded', function () {
        initLoginValidation();
        initRegistroValidation();
    });
})();
