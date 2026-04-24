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
