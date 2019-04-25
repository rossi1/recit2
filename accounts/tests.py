import unittest
import time

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status
from . serializer import UserSerializer, generated_unique_id
from .utils import generate_safe_token,  validate_code, password_reset_code

class SerializerTests(APITestCase):

    data = {'email': 'emma@outlook.com', 'password': 'fhdh',
    'first_name': 'John', 'last_name': 'Emma'
    }
    
    def test_user_serializer(self):
        
        serializer  = UserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid(raise_exception=True))


class ViewTests(APITestCase):
    data = {'email': 'emma@outlook.com', 'password': 'fhdh',
    'first_name': 'John', 'last_name': 'Emma'}


    def setUp(self):
        user = get_user_model().objects.create_user(email=self.data['email'],
        first_name=self.data['first_name'], last_name=self.data['last_name'],
        user_id=generated_unique_id)
        user.set_password(self.data['password'])
        user.save()
        

    def test_create_account(self):
        url = reverse('signup')
        data = {'email': 'emman@outlook.com', 'password': 'fhdh',
        'first_name': 'John', 'last_name': 'Emma'}
        response = self.client.post(url, data, format='json')
    
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_user_model().objects.count(), 2)
        

    def test_login_account(self):
        url = reverse('login')
        data = {'email': 'emma@outlook.com', 'password': 'fhdh'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_login_failed_account(self):
        url = reverse('login')
        data = {'email': 'emma@outlook.com', 'password': 'fhdh1'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    '''
    def test_logout_accont(self):
        url = reverse('login')
        data = {'email': 'emma@outlook.com', 'password': 'fhdh'}
        response = self.client.post(url, data, format='json')

        if response.status_code == status.HTTP_200_OK:
            logout_url = reverse('logout')
            headers = {'HTTP_Token': response.data}
            response = self.client.get(logout_url, headers=headers)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
    '''

class ForgotPasswordTests(APITestCase):

    data = {'email': 'emma@outlook.com', 'password': 'fhdh',
    'first_name': 'John', 'last_name': 'Emma'}



    def setUp(self):
        user = get_user_model().objects.create_user(email=self.data['email'],
        first_name=self.data['first_name'], last_name=self.data['last_name'],
        user_id=generated_unique_id)
        user.set_password(self.data['password'])
        user.save()

    
    def test_verification_code(self):
        code = password_reset_code()
        password = {'password': code}
        generate_code = generate_safe_token(code)
        url = '{}?code={}&email={}'.format(reverse('verify_token'), generate_code, self.data['email'])
        resp = self.client.post(url, data=password, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('Successful', resp.data['message'])
        if resp.status_code == status.HTTP_200_OK:
            url = '{}?code={}&email={}'.format(reverse('pasword-reset'), resp.data['code'], resp.data['email'])
            resp = self.client.post(url, data=password, format='json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertIn('Succesfully', resp.data)


'''
class BusinessAccountTests(APITestCase):
    data = {'email': 'emman@outlook.com', 'password': 'fhdh', 'first_name': 'John', 'last_name': 'Emma'}

    def setUp(self):
        user = get_user_model().objects.create_user(email=self.data['email'],
        first_name=self.data['first_name'], last_name=self.data['last_name'],
        user_id=generated_unique_id)
        user.set_password(self.data['password'])
        user.save()
        
    
    def test_create_buisness_account(self):
        url_login = reverse('login')
        data = {'email': 'emman@outlook.com', 'password': 'fhdh'}
        response = self.client.post(url_login, data, format='json')

        if response.status_code == status.HTTP_200_OK:
            url_acct = '{}'.format(reverse('create-business'))
            params = {"business_name": "ola", "business_description": "wayne",
            "business_number": "0705496321", "business_type": "buu"}
            header = {'Authorization': 'Token {}'.format(response.data['token'])}
            resp = self.client.post(url_acct, data=params, header=header, format='json')
            self.assertEqual(resp.status_code, status.HTTP_200_OK)

        
'''


if '__name__' == '__main__':
    unittest.main()