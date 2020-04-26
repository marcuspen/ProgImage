import os
from unittest.mock import patch, Mock, call

import pytest
from nameko.containers import ServiceContainer
from nameko.testing.services import replace_dependencies

from prog_image.service import ImageService
from prog_image.dependencies.cloudinary import ImageNotFound, ImageUploadError

TEST_IMAGE_FILE = os.path.join(
    os.path.dirname(__file__), 'test_data', 'test_image.jpg'
)


@pytest.fixture
def image_service(config):
    image_svc = ServiceContainer(ImageService, config)
    replace_dependencies(image_svc, 'image_host')
    image_svc.start()

    yield image_svc

    image_svc.stop()


@pytest.fixture
def mock_uuid():
    with patch('prog_image.service.uuid4') as uuid4:
        uuid4.return_value = Mock(hex='abc123')
        yield uuid4


class TestGetImage:

    def test_gets_image(self, config, web_session):
        image_svc = ServiceContainer(ImageService, config)
        mock_image_host = replace_dependencies(image_svc, 'image_host')
        mock_image_host.download_image.return_value = b'foo'

        image_svc.start()

        response = web_session.get('/image/abc123')

        assert response.status_code == 200
        assert response.content == b'foo'
        assert response.headers['Content-Type'] == 'image/jpeg'

    def test_image_not_found(self, config, web_session):
        image_svc = ServiceContainer(ImageService, config)
        mock_image_host = replace_dependencies(image_svc, 'image_host')
        mock_image_host.download_image.side_effect = ImageNotFound('not found')

        image_svc.start()

        response = web_session.get('/image/abc123')

        assert response.status_code == 404
        assert response.text == 'not found'


class TestPostImage:

    def test_posts_image(self, config, web_session, mock_uuid):
        image_svc = ServiceContainer(ImageService, config)
        mock_image_host = replace_dependencies(image_svc, 'image_host')
        mock_image_host.upload_image.return_value = b'foo'

        image_svc.start()

        with open(TEST_IMAGE_FILE, 'rb') as image_file:
            response = web_session.post(
                '/image',
                files={'data': image_file},
            )

        assert response.json() == {'image_id': 'abc123'}
        assert mock_image_host.upload_image.call_args_list[0][0][1] == 'abc123'

    def test_unexpected_error(self, config, web_session, mock_uuid):
        image_svc = ServiceContainer(ImageService, config)
        mock_image_host = replace_dependencies(image_svc, 'image_host')
        mock_image_host.upload_image.side_effect = ImageUploadError('BOOM!')

        image_svc.start()

        with open(TEST_IMAGE_FILE, 'rb') as image_file:
            response = web_session.post(
                '/image',
                files={'data': image_file},
            )

        assert response.text == 'Error: ImageUploadError: BOOM!\n'
        assert response.status_code == 500
