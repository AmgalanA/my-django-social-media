from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile

import uuid

from core.models import Post

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.index_url = reverse('index')
        self.like_post_url = reverse('like-post')

    def test_index_GET(self):
        response = self.client.get(self.index_url)

        self.assertEquals(response.status_code, 302)
        # self.assertTemplateUsed(response, '/signup.html')

    def test_signup_POST(self, username = 'TestUser', email = 'testuser@gmail.com'):
        response = self.client.post('/signup', {
            'username': username,
            'email': email,
            'password': 'testpassword',
            'password2': 'testpassword',
        })

        self.assertEquals(response.status_code, 302)

    def test_signup_passwords_do_not_match_POST(self):
        response = self.client.post('/signup', {
            'username': 'TestUser',
            'email': 'testuser@example',
            'password': 'testpassword',
            'password2': 'anotherpassword',
        })
        self.assertEquals(response.status_code, 302)

        messages = list(get_messages(response.wsgi_request))

        self.assertEquals(str(messages[0]), 'Passwords Not Matching')
    
    def test_signup_email_already_taken_POST(self):
        response = self.client.post('/signup', {
            'username': 'TestUser',
            'email': 'testuser@example',
            'password': 'testpassword',
            'password2': 'testpassword',
        })  

        self.assertEquals(response.status_code, 302)

        response = self.client.post('/signup', {
            'username': 'AnotherUser',
            'email': 'testuser@example',
            'password': 'testpassword',
            'password2': 'testpassword',
        })

        self.assertEquals(response.status_code, 302)
        
        messages = list(get_messages(response.wsgi_request))

        self.assertEquals(str(messages[0]), 'Email Already Taken')
    
    def test_signup_username_already_taken_POST(self):
        response = self.client.post('/signup', {
            'username': 'TestUser',
            'email': 'testuser@example',
            'password': 'testpassword',
            'password2': 'testpassword',
        })  

        self.assertEquals(response.status_code, 302)

        response = self.client.post('/signup', {
            'username': 'TestUser',
            'email': 'anotheruser@example',
            'password': 'testpassword',
            'password2': 'testpassword',
        })

        self.assertEquals(response.status_code, 302)
        
        messages = list(get_messages(response.wsgi_request))

        self.assertEquals(str(messages[0]), 'Username Already Taken')

    def test_correct_template_signup_GET(self):
        response = self.client.get('/signup') 

        self.assertEquals(response.status_code, 200)

        self.assertTemplateUsed(response, 'signup.html')

    def test_signin_POST(self):
        response = self.client.post('/signup', {
            'username': 'TestUser',
            'email': 'testuser@example',
            'password': 'testpassword',
            'password2': 'testpassword',
        })  

        self.assertEquals(response.status_code, 302)

        signin_response = self.client.post('/signin', {
            'username': "TestUser",
            'password': 'testpassword'
        })

        self.assertEquals(signin_response.status_code, 302)

    def test_signin_credentials_invalid_POST(self):
        self.test_signup_POST()

        response = self.client.post('/signin', {
            'username': 'SomeAnotherUser',
            'password': 'someanotherpassword',
        })

        messages = list(get_messages(response.wsgi_request))

        self.assertEquals(str(messages[0]), 'Credentials Invalid')

    def test_correct_template_signin_GET(self):
        response = self.client.get('/signin')

        self.assertTemplateUsed(response, 'signin.html')

    def test_logout_GET(self):
        response = self.client.get('/logout')

        self.assertEquals(response.status_code, 302)

    def test_check_index_GET(self):
        self.test_signup_POST()

        self.test_signup_POST(username='AnotherUser', email='anotheruser@example.com')

        self.test_signup_POST(username='AnotherUser2', email='anotheruser2@example.com')
        
        self.test_signup_POST(username='AnotherUser3', email='anotheruser3@example.com')
        
        self.test_signup_POST(username='AnotherUser4', email='anotheruser4@example.com')

        response = self.client.get('/')

        profile_list = response.context['suggestions_username_profile_list']

        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
        self.assertEquals(len(profile_list), 4)

        self.test_signup_POST(username='AnotherUser5', email='anotheruser5@example.com')

        self.assertEquals(len(profile_list), 4)

        profile_list = sorted(profile_list, key=lambda profile: profile.id)

        count = 1

        for profile in profile_list:
            self.assertEquals(profile.id, count)
            count += 1

    def test_upload_POST(self):
        self.test_signup_POST()

        file = SimpleUploadedFile('credit-cards.png', b'file_content', content_type='image/png')

        response = self.client.post('/upload', {
            'image_upload': file,
            'caption': 'Some Caption'
        })

        profile_response = self.client.post('/profile/TestUser')

        post = profile_response.context['user_posts'][0]
        
        self.assertEquals(post.caption, 'Some Caption')

        return post

    def test_like_post(self):
        post = self.test_upload_POST()

        response = self.client.get(self.like_post_url, {
            'post_id': post.id
        })

        profile_response = self.client.post('/profile/TestUser')

        post = profile_response.context['user_posts'][0]
        
        self.assertEquals(post.no_of_likes, 1)

        response = self.client.get(self.like_post_url, {
            'post_id': post.id
        })

        profile_response = self.client.post('/profile/TestUser')

        post = profile_response.context['user_posts'][0]
        
        self.assertEquals(post.no_of_likes, 0)

    def test_delete_POST(self):
        post = self.test_upload_POST()

        delete_post_response = self.client.post('/delete-post', {
            'post_id': post.id
        })

        self.assertRedirects(delete_post_response, '/')

    def test_delete_non_existing_post_POST(self):
        post = self.test_upload_POST()

        delete_post_response = self.client.post('/delete-post', {
            'post_id': post.id
        })

        delete_post_response = self.client.post('/delete-post', {
            'post_id': post.id
        })

    def test_follow_user_POST(self):
        self.test_signup_POST()
        self.test_signup_POST('AnotherUser', 'anotheruser@gmail.com')
        self.test_signup_POST('AnotherUser2', 'anotheruser2@gmail.com')

        sub_response = self.client.post('/follow', {
            'follower': 'TestUser',
            'user': 'AnotherUser'
        })

        profile_response = self.client.post('/profile/TestUser')

        self.assertEquals(profile_response.context['user_following'], 1)

        one_more_sub_response = self.client.post('/follow', {
            'follower': 'TestUser',
            'user': 'AnotherUser2'
        })

        profile_response = self.client.post('/profile/TestUser')

        self.assertEquals(profile_response.context['button_text'], 'Unfollow')
        self.assertEquals(profile_response.context['user_following'], 2)

        unsub_response = self.client.post('/follow', {
            'follower': 'TestUser',
            'user': 'AnotherUser'
        })

        profile_response = self.client.post('/profile/TestUser')

        self.assertEquals(profile_response.context['user_following'], 1)

    def test_settings_POST(self):
        self.test_signup_POST()

        file = SimpleUploadedFile('credit-cards.png', b'file_content', content_type='image/png')

        response = self.client.post('/settings', {
            'image': file,
            'bio': 'Some Bio',
            'location': 'Some Location'
        })

        profile_response = self.client.post('/profile/TestUser')

        profile_image = profile_response.context['user_profile'].profileimg
        profile_bio = profile_response.context['user_profile'].bio
        profile_location = profile_response.context['user_profile'].location
        self.assertNotEquals(profile_image, 'blank_profile.png')
        self.assertNotEquals(profile_image, None)
        self.assertEquals(profile_bio, 'Some Bio')
        self.assertEquals(profile_location, 'Some Location')

    def test_search_POST(self):
        self.test_signup_POST()
        self.test_signup_POST(username='ANOTHERUSER', email='anotheruser@example.com')

        response = self.client.post('/search', {
            'username': "Test"
        })

        profile_list = response.context['username_profile_list']

        self.assertEquals(profile_list[0].id_user, 1)

    


        