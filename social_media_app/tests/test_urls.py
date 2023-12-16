from django.test import SimpleTestCase
from django.urls import reverse, resolve

from core.views import index, settings, upload, delete_post, follow, like_post, signin, signup, logout

# Test if path resolves with correct function 
class TestUrls(SimpleTestCase):
    def test_index(self):
        url = reverse('index')
        self.assertEquals(resolve(url).func, index)

    def test_settings(self):
        url = reverse('settings')
        self.assertEquals(resolve(url).func, settings)

    def test_upload(self):
        url = reverse('upload')
        self.assertEquals(resolve(url).func, upload)

    def delete_post(self):
        url = reverse('delete-post')
        self.assertEquals(resolve(url).func, delete_post)

    def test_follow(self):
        url = reverse('follow')
        self.assertEquals(resolve(url).func, follow)

    def test_like_post(self):
        url = reverse('like-post')
        self.assertEquals(resolve(url).func, like_post)

    def test_signup(self):
        url = reverse('signup')
        self.assertEquals(resolve(url).func, signup)

    def test_signin(self):
        url = reverse('signin')
        self.assertEquals(resolve(url).func, signin)

    def test_logout(self):
        url = reverse('logout')
        self.assertEquals(resolve(url).func, logout)
