from copy import deepcopy
from unittest.mock import Mock, call, patch

import pytest
import requests_mock
from cloudinary.exceptions import Error as CloudinaryError

from prog_image.dependencies.cloudinary import (
    Client,
    Cloudinary,
    ImageNotFound,
    ImageUploadError,
    ImageDownloadError,
)

MOCK_IMAGE_URL = 'http://test-image.com/abc123'


@pytest.fixture
def mock_cloudinary_image():
    with patch('prog_image.dependencies.cloudinary.CloudinaryImage') as img:
        img.return_value.url = MOCK_IMAGE_URL
        yield img


class TestClient:

    def test_upload_image(self):
        mock_image = Mock()
        test_client = Client()

        with patch('prog_image.dependencies.cloudinary.uploader') as uploader:
            test_client.upload_image(mock_image, 'abc123')

        assert uploader.upload.call_args_list == [
            call(mock_image, public_id='abc123')
        ]

    def test_upload_image_error(self):
        mock_image = Mock()
        test_client = Client()

        with patch('prog_image.dependencies.cloudinary.uploader') as uploader:
            uploader.upload.side_effect = CloudinaryError('BOOM!')

            with pytest.raises(ImageUploadError) as err:
                test_client.upload_image(mock_image, 'abc123')

        err.match('Unable to upload image with ID abc123 - BOOM!')

    def test_download_image(self, mock_cloudinary_image):
        test_client = Client()

        with requests_mock.Mocker() as m:
            m.get(MOCK_IMAGE_URL, content=b'foo')
            response = test_client.download_image('abc123')

        assert response.data == b'foo'
        assert m.last_request.url == MOCK_IMAGE_URL

    @pytest.mark.parametrize('status_code,error_class,error_message', [
        (404, ImageNotFound, 'Image abc123 not found'),
        (
            500,
            ImageDownloadError,
            "Unexpected error when downloading image abc123 - b'BOOM!'"
        ),
    ])
    def test_download_image_not_found(
        self, mock_cloudinary_image, status_code, error_class, error_message
    ):
        test_client = Client()

        with requests_mock.Mocker() as m:
            m.get(MOCK_IMAGE_URL, status_code=status_code, content=b'BOOM!')

            with pytest.raises(error_class) as err:
                test_client.download_image('abc123')

        err.match(error_message)


class TestCloudinaryDependency:

    @pytest.fixture
    def mock_client(self):
        with patch('prog_image.dependencies.cloudinary.Client') as client:
            yield client.return_value

    @pytest.fixture
    def mock_cloudinary(self, mock_client, cloudinary_config):
        cloudinary = Cloudinary()
        cloudinary.container = Mock()
        cloudinary.container.config = {'CLOUDINARY': cloudinary_config}

        with patch('prog_image.dependencies.cloudinary.config'):
            cloudinary.setup()

        cloudinary.start()
        yield cloudinary

    def test_init(self):
        cloudinary = Cloudinary()
        assert cloudinary.client is None

    def test_get_dependency(self, mock_client, cloudinary_config):
        cloudinary = Cloudinary()
        cloudinary.container = Mock()
        expected_config = deepcopy(cloudinary_config)
        cloudinary.container.config = {'CLOUDINARY': cloudinary_config}

        with patch('prog_image.dependencies.cloudinary.config') as mock_config:
            cloudinary.setup()

        cloudinary.start()
        client = cloudinary.get_dependency(Mock())

        assert mock_config.call_args_list == [
            call(**expected_config)
        ]
        assert client == mock_client

    def test_stop(self, mock_cloudinary, mock_client):
        assert mock_cloudinary.client == mock_client
        mock_cloudinary.stop()
        assert mock_cloudinary.client is None

    def test_kill(self, mock_cloudinary, mock_client):
        assert mock_cloudinary.client == mock_client
        mock_cloudinary.kill()
        assert mock_cloudinary.client is None
