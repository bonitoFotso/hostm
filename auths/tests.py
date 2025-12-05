from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserModelTests(TestCase):
    """Tests pour le modèle User"""

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_create_user(self):
        """Test de création d'un utilisateur normal"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.assertEqual(user.email, self.user_data['email'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNotNone(user.username)  # Username auto-généré

    def test_create_user_without_email(self):
        """Test que la création d'un utilisateur sans email échoue"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password=self.user_data['password'])

    def test_create_superuser(self):
        """Test de création d'un superutilisateur"""
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='AdminPassword123!'
        )
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_user_str_method(self):
        """Test de la méthode __str__"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.assertEqual(str(user), self.user_data['email'])

    def test_full_name_property(self):
        """Test de la propriété full_name"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name='John',
            last_name='Doe'
        )
        self.assertEqual(user.full_name, 'John Doe')

    def test_full_name_without_names(self):
        """Test de full_name sans prénom ni nom"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        self.assertEqual(user.full_name, user.username)

    def test_get_short_name(self):
        """Test de la méthode get_short_name"""
        user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name='John'
        )
        self.assertEqual(user.get_short_name(), 'John')

    def test_username_auto_generation(self):
        """Test de la génération automatique du username"""
        user = User.objects.create_user(
            email='testuser@example.com',
            password='password123'
        )
        self.assertEqual(user.username, 'testuser')

    def test_username_uniqueness(self):
        """Test que les usernames générés sont uniques"""
        user1 = User.objects.create_user(
            email='test@example.com',
            password='password123'
        )
        user2 = User.objects.create_user(
            email='test@gmail.com',
            password='password123'
        )
        self.assertNotEqual(user1.username, user2.username)


class AuthenticationAPITests(APITestCase):
    """Tests pour les endpoints d'authentification"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('auths:auth-list')
        self.login_url = reverse('auths:login')
        self.token_refresh_url = reverse('auths:token_refresh')
        self.token_verify_url = reverse('auths:token_verify')
        
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        self.user = User.objects.create_user(
            email='existing@example.com',
            password='ExistingPassword123!',
            first_name='Existing',
            last_name='User'
        )

    def test_user_registration_success(self):
        """Test d'inscription réussie"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('tokens', response.data)
        self.assertEqual(response.data['user']['email'], self.user_data['email'])
        
        # Vérifier que l'utilisateur existe en base
        user_exists = User.objects.filter(email=self.user_data['email']).exists()
        self.assertTrue(user_exists)

    def test_user_registration_duplicate_email(self):
        """Test d'inscription avec un email déjà existant"""
        duplicate_data = {
            'email': 'existing@example.com',
            'password': 'TestPassword123!',
        }
        response = self.client.post(self.register_url, duplicate_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        """Test d'inscription avec un email invalide"""
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid-email'
        
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_missing_password(self):
        """Test d'inscription sans mot de passe"""
        data = self.user_data.copy()
        data.pop('password')
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        """Test de connexion réussie"""
        login_data = {
            'email': 'existing@example.com',
            'password': 'ExistingPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Test de connexion avec des identifiants invalides"""
        login_data = {
            'email': 'existing@example.com',
            'password': 'WrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_user(self):
        """Test de connexion avec un utilisateur inexistant"""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        """Test de rafraîchissement du token"""
        refresh = RefreshToken.for_user(self.user)
        
        response = self.client.post(
            self.token_refresh_url,
            {'refresh': str(refresh)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_verify(self):
        """Test de vérification du token"""
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        response = self.client.post(
            self.token_verify_url,
            {'token': access_token},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserProfileAPITests(APITestCase):
    """Tests pour les endpoints de profil utilisateur"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        
        # Authentifier l'utilisateur
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.me_url = reverse('auths:auth-me')
        self.change_password_url = reverse('auths:auth-change-password')
        self.password_reset_url = reverse('auths:auth-request-password-reset')
        self.delete_account_url = reverse('auths:auth-delete-account')

    def test_get_profile_authenticated(self):
        """Test de récupération du profil utilisateur connecté"""
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['first_name'], self.user.first_name)

    def test_get_profile_unauthenticated(self):
        """Test de récupération du profil sans authentification"""
        self.client.credentials()  # Supprimer les credentials
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_profile(self):
        """Test de mise à jour du profil"""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        response = self.client.patch(self.me_url, update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')

    def test_change_password_success(self):
        """Test de changement de mot de passe réussi"""
        password_data = {
            'old_password': 'TestPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        response = self.client.post(self.change_password_url, password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))

    def test_change_password_wrong_old_password(self):
        """Test de changement avec un ancien mot de passe incorrect"""
        password_data = {
            'old_password': 'WrongPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        response = self.client.post(self.change_password_url, password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_change_password_mismatch(self):
        """Test de changement avec confirmation non correspondante"""
        password_data = {
            'old_password': 'TestPassword123!',
            'new_password': 'NewPassword123!',
            'confirm_password': 'DifferentPassword123!'
        }
        response = self.client.post(self.change_password_url, password_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_password_reset(self):
        """Test de demande de réinitialisation de mot de passe"""
        self.client.credentials()  # Pas besoin d'auth pour reset
        
        reset_data = {'email': 'test@example.com'}
        response = self.client.post(self.password_reset_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_delete_account(self):
        """Test de suppression/désactivation du compte"""
        response = self.client.delete(self.delete_account_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class PermissionsTests(APITestCase):
    """Tests pour les permissions"""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!'
        )
        self.me_url = reverse('auths:auth-me')

    def test_authenticated_required_endpoints(self):
        """Test que certains endpoints nécessitent une authentification"""
        endpoints_requiring_auth = [
            self.me_url,
            reverse('auths:auth-change-password'),
            reverse('auths:auth-delete-account'),
        ]
        
        for endpoint in endpoints_requiring_auth:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"Endpoint {endpoint} devrait nécessiter une authentification"
            )

    def test_public_endpoints(self):
        """Test que certains endpoints sont publics"""
        register_url = reverse('auths:auth-list')
        login_url = reverse('auths:login')
        
        # Ces endpoints devraient être accessibles sans authentification
        # (même si les requêtes échouent pour d'autres raisons)
        response = self.client.post(register_url, {}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(login_url, {}, format='json')
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)