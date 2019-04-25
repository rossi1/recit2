import unittest
import time

from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework import status

from accounts.serializer import generated_unique_id

class ClientViewTests(APITestCase):
    data = {'email': 'emma@outlook.com', 'password': 'fhdh',
    'first_name': 'John', 'last_name': 'Emma'
    }

    def setUp(self):
        user = get_user_model().objects.create_user(email=self.data['email'],
        first_name=self.data['first_name'], last_name=self.data['last_name'],
        user_id=generated_unique_id(6))
        user.set_password(self.data['password'])
        user.save()

    def test_client_views(self):
        client_url = reverse('create_client')
        login_url = reverse('login')
        client_details = {
            'client_name': 'Josphen Martins',
            'client_email': 'martins@outlook.com',
            'client_phone_number': '08106125357'
        }
        login_details = {'email': self.data['email'], 'password': self.data['password']}

        login_resp = self.client.post(login_url, data=login_details, format='json')
        if login_resp.status_code == status.HTTP_200_OK:
            token = {'Token': login_resp.data['token']}
            

            client_resp = self.client.post(client_url, data=client_details, format='json', HTTP_AUTHORIZATION=token)
            self.assertEqual(client_resp.status_code, status.HTTP_400_BAD_REQUEST)




if '__name__' == '__main__':
    unittest.main()