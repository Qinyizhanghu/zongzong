
from django.test import TestCase

from commercial.testing import mock
from utilities.mock_utility.helper import create_user_login_client


class TestFootPrint(TestCase):

    def test_add_favor(self):
        """
        python manage.py test --settings=settings-test commercial.testing.test_footprint.TestFootPrint.test_add_favor
        """
        client, user = create_user_login_client()
        foorprint = mock.create_footprint(user)
        # 1
        result = client.json_post('/footprint/favor/', {'footprint_id': foorprint.id})
        # 0
        # result = client.json_post('/footprint/favor/', {'footprint_id': foorprint.id})
        print(result)
