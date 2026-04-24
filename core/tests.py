from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from game.models import UserProfile


class AuthAndProgressFlowTests(TestCase):

	def setUp(self):
		self.password = 'Segura123!'
		self.user = User.objects.create_user(username='nino', password=self.password)
		UserProfile.objects.create(usuario=self.user)

	def test_login_page_renders(self):
		response = self.client.get(reverse('login'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Iniciar Sesión')

	def test_login_success_redirects_to_index(self):
		response = self.client.post(
			reverse('login'),
			data={'username': self.user.username, 'password': self.password},
		)
		self.assertRedirects(response, reverse('index'))

	def test_index_requires_authentication(self):
		response = self.client.get(reverse('index'))
		expected = f"{reverse('login')}?next={reverse('index')}"
		self.assertRedirects(response, expected)

	def test_tema_2_blocked_by_default(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('aprendizaje', kwargs={'tema': 2}))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Tema bloqueado')

	def test_completar_tema_unlocks_next_topic(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.post(reverse('completar_tema', kwargs={'tema': 1}))
		self.assertRedirects(response, reverse('aprendizaje', kwargs={'tema': 2}))

		profile = UserProfile.objects.get(usuario=self.user)
		self.assertEqual(profile.ultimo_tema_desbloqueado, 2)

	def test_completar_tema_rejects_get(self):
		self.client.login(username=self.user.username, password=self.password)
		response = self.client.get(reverse('completar_tema', kwargs={'tema': 1}))
		self.assertEqual(response.status_code, 405)

	def test_registro_crea_usuario_y_perfil(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': 'nuevo_nino',
				'password1': 'ClaveSegura123!',
				'password2': 'ClaveSegura123!',
				'fecha_nacimiento': '2015-10-03',
				'genero': 'M',
				'nombre_tutor': 'Tutor Uno',
				'email_tutor': 'tutor@example.com',
				'pais': 'Colombia',
				'acepto_terminos': 'on',
				'consentimiento_tutor': 'on',
			},
		)
		self.assertRedirects(response, reverse('login'))

		user = User.objects.get(username='nuevo_nino')
		profile = UserProfile.objects.get(usuario=user)
		self.assertEqual(profile.genero, 'M')
		self.assertEqual(profile.nombre_tutor, 'Tutor Uno')
		self.assertTrue(profile.acepto_terminos)
		self.assertTrue(profile.consentimiento_tutor)
		self.assertIsNotNone(profile.acepto_terminos_en)
		self.assertIsNotNone(profile.consentimiento_tutor_en)

	def test_registro_rechaza_passwords_distintas(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': 'nino_mismatch',
				'password1': 'ClaveSegura123!',
				'password2': 'ClaveSeguraXYZ!',
				'nombre_tutor': 'Tutor Mismatch',
				'email_tutor': 'tutor.mismatch@example.com',
				'acepto_terminos': 'on',
				'consentimiento_tutor': 'on',
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Las contraseñas no coinciden')
		self.assertFalse(User.objects.filter(username='nino_mismatch').exists())

	def test_registro_rechaza_username_duplicado(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': self.user.username,
				'password1': 'OtraClave123!',
				'password2': 'OtraClave123!',
				'nombre_tutor': 'Tutor Duplicado',
				'email_tutor': 'tutor.duplicado@example.com',
				'acepto_terminos': 'on',
				'consentimiento_tutor': 'on',
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'El nombre de usuario ya existe')

	def test_registro_requiere_aceptar_terminos_y_consentimiento(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': 'nino_sin_consent',
				'password1': 'ClaveSegura123!',
				'password2': 'ClaveSegura123!',
				'nombre_tutor': 'Tutor Sin Consent',
				'email_tutor': 'tutor.sinconsent@example.com',
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Debes aceptar los términos y condiciones')
		self.assertContains(response, 'Debes confirmar el consentimiento del tutor')
		self.assertFalse(User.objects.filter(username='nino_sin_consent').exists())

	def test_registro_requiere_datos_del_tutor(self):
		response = self.client.post(
			reverse('registro'),
			data={
				'username': 'nino_sin_tutor',
				'password1': 'ClaveSegura123!',
				'password2': 'ClaveSegura123!',
				'acepto_terminos': 'on',
				'consentimiento_tutor': 'on',
			},
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'El nombre del tutor es obligatorio')
		self.assertContains(response, 'El email del tutor es obligatorio')
		self.assertFalse(User.objects.filter(username='nino_sin_tutor').exists())
