from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from .models import Dataset, MLModel, Report, ImageDataset, AudioDataset, VideoDataset
import io


class ModelTestCase(TestCase):
    """Test core models"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='TestPass@123'
        )

    def test_dataset_creation(self):
        """Dataset create ho raha hai?"""
        dataset = Dataset.objects.create(
            name='test.csv',
            user=self.user
        )
        self.assertEqual(dataset.name, 'test.csv')
        self.assertEqual(dataset.user, self.user)
        self.assertEqual(Dataset.objects.count(), 1)

    def test_ml_model_creation(self):
        """ML model create ho raha hai?"""
        ml_model = MLModel.objects.create(
            name='test_model',
            algorithm='RandomForest',
            accuracy=0.95
        )
        self.assertEqual(ml_model.algorithm, 'RandomForest')
        self.assertEqual(ml_model.accuracy, 0.95)

    def test_image_dataset_creation(self):
        """ImageDataset create ho raha hai?"""
        img = ImageDataset.objects.create(
            name='test.jpg',
            user=self.user
        )
        self.assertEqual(img.name, 'test.jpg')

    def test_audio_dataset_creation(self):
        """AudioDataset create ho raha hai?"""
        audio = AudioDataset.objects.create(
            name='test.mp3',
            user=self.user
        )
        self.assertEqual(audio.name, 'test.mp3')

    def test_video_dataset_creation(self):
        """VideoDataset create ho raha hai?"""
        video = VideoDataset.objects.create(
            name='test.mp4',
            user=self.user
        )
        self.assertEqual(video.name, 'test.mp4')


class AuthenticationTestCase(TestCase):
    """Test authentication & authorization"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass@123'
        )

    def test_dashboard_requires_login(self):
        """Dashboard login ke bina access nahi hona chahiye"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/accounts/login/', response.url)

    def test_dashboard_accessible_after_login(self):
        """Login ke baad dashboard khulna chahiye"""
        self.client.login(username='testuser', password='TestPass@123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_signup_creates_user(self):
        """Signup se naya user ban raha hai?"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'NewPass@123',
            'password2': 'NewPass@123',
        })
        self.assertEqual(User.objects.filter(username='newuser').count(), 1)

    def test_login_works(self):
        """Login valid credentials se kaam kar raha hai?"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'TestPass@123',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_logout_works(self):
        """Logout kaam kar raha hai?"""
        self.client.login(username='testuser', password='TestPass@123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class ViewTestCase(TestCase):
    """Test views & URL access"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass@123'
        )
        self.client.login(username='testuser', password='TestPass@123')

    def test_upload_image_page_accessible(self):
        """Image upload page khul raha hai?"""
        response = self.client.get(reverse('upload_image'))
        self.assertEqual(response.status_code, 200)

    def test_upload_audio_page_accessible(self):
        """Audio upload page khul raha hai?"""
        response = self.client.get(reverse('upload_audio'))
        self.assertEqual(response.status_code, 200)

    def test_upload_video_page_accessible(self):
        """Video upload page khul raha hai?"""
        response = self.client.get(reverse('upload_video'))
        self.assertEqual(response.status_code, 200)

    def test_dataset_list_accessible(self):
        """My Datasets page khul raha hai?"""
        response = self.client.get(reverse('dataset_list'))
        self.assertEqual(response.status_code, 200)

    def test_merge_page_accessible(self):
        """Merge page khul raha hai?"""
        response = self.client.get(reverse('merge_datasets'))
        self.assertEqual(response.status_code, 200)


class UploadTestCase(TestCase):
    """Test file upload functionality"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass@123'
        )
        self.client.login(username='testuser', password='TestPass@123')

    def test_csv_upload_creates_dataset(self):
        """CSV upload karne se Dataset create ho raha hai?"""
        csv_content = b"name,age,salary\nMunish,25,30000\nRaj,30,45000"
        csv_file = SimpleUploadedFile(
            "test.csv",
            csv_content,
            content_type="text/csv"
        )
        response = self.client.post(reverse('upload_dataset'), {
            'dataset_file': csv_file
        })
        self.assertEqual(Dataset.objects.count(), 1)
        self.assertEqual(response.status_code, 302)  # Redirect after upload