from http import HTTPStatus

from django.test import TestCase
from django.urls import reverse
from rest_framework.response import Response
from rest_framework.test import APIClient


class SanityTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_sanity_endpoint(self):
        response = self.client.get(reverse("sanity"))
        assert isinstance(response, Response)
        self.assertEqual(response.status_code, HTTPStatus.OK)
