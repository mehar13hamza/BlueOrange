from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from unittest.mock import patch, Mock
import difflib
import requests

class ZipCodeDetailViewTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('zip-code-detail', kwargs={'zipcode': '12345'})

    def setUp(self):
        self.zip_code_data = {
            'zipcode': '12345',
            'city': 'Sample City',
            'state': 'Sample State',
            'state_code': 'SS',
            'country': 'Sample Country',
            'latitude': '0.0',
            'longitude': '0.0',
        }

    @patch('api.views.load_zip_codes')
    def test_zip_code_detail_view_returns_correct_data(self, mock_load_zip_codes):
        mock_load_zip_codes.return_value = self.zip_code_data
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('zipcode'), self.zip_code_data['zipcode'])

    @patch('api.views.load_zip_codes')
    def test_zip_code_detail_view_returns_not_found_for_invalid_zipcode(self, mock_load_zip_codes):
        mock_load_zip_codes.return_value = None 
        response = self.client.get(reverse('zip-code-detail', kwargs={'zipcode': '0000000'}))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'message': 'Zip code not found.'})


class TopZipCodesViewTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('top-zipcodes')

    @patch('api.views.zip_codes_data', [
        {'zipcode': '12345', 'city': 'Testville'},
        {'zipcode': '23456', 'city': 'Example City'},
        {'zipcode': '34567', 'city': 'Sample City'}
    ])
    def test_top_zip_codes_view(self):
        post_data = {'city_name': 'Testville'}
        response = self.client.post(self.url, post_data, format='json')
        from api.views import zip_codes_data

        scores = [(zipcode, difflib.SequenceMatcher(None, post_data['city_name'].lower(),\
            (zipcode.get('city') or '').lower()).ratio()) for zipcode in zip_codes_data]
        scores.sort(key=lambda x: x[1], reverse=True)

        expected_response = [zipcode for zipcode, _ in scores[:3]]

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.json(), expected_response,\
            "The response does not match the expected top zip codes.")


class CodeAPITestCase(APITestCase):
    def setUp(self):
        self.url = reverse('authorization-code') 

    @patch('api.views.requests.post')  
    def test_missing_code_parameter(self, mock_post):
        response = self.client.get(self.url) 
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Authorization code is missing'})

    @patch('api.views.requests.post')
    def test_successful_token_exchange(self, mock_post):
        mock_response = Mock()
        expected_json_data = {'access_token': 'abc123', 'token_type': 'Bearer'}
        mock_response.json.return_value = expected_json_data
        mock_response.raise_for_status = Mock() 
        mock_post.return_value = mock_response

        response = self.client.get(self.url, {'code': 'valid_code'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_json_data)

    @patch('api.views.requests.post')
    def test_error_from_token_service(self, mock_post):
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("Error 500: Server Error")
        mock_post.return_value = mock_response

        response = self.client.get(self.url, {'code': 'valid_code'})
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {'error': 'Error 500: Server Error'})
