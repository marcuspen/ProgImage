import logging

import requests
from cloudinary import uploader, config, CloudinaryImage
from cloudinary.exceptions import Error as CloudinaryError
from nameko.extensions import DependencyProvider

log = logging.getLogger(__name__)


class ImageNotFound(Exception):
    pass


class ImageUploadError(Exception):
    pass


class ImageDownloadError(Exception):
    pass


class Client:

    def upload_image(self, image, image_id):
        try:
            return uploader.upload(image, public_id=image_id)
        except CloudinaryError as err:
            error_message = (
                f'Unable to upload image with ID {image_id} - {err}'
            )
            log.exception(error_message)
            raise ImageUploadError(error_message) from err

    def download_image(self, image_id):
        image_location = CloudinaryImage(public_id=image_id).url
        response = requests.get(image_location, stream=True)

        if response.status_code == 200:
            return response.raw
        elif response.status_code == 404:
            error_message = f'Image {image_id} not found'
            log.error(error_message)

            raise ImageNotFound(error_message)
        else:
            error_message = (
                f'Unexpected error when downloading image {image_id} - '
                f'{response.content}'
            )
            log.error(error_message)

            raise ImageDownloadError(error_message)


class Cloudinary(DependencyProvider):

    def __init__(self):
        self.client = None

    def setup(self):
        config(**self.container.config['CLOUDINARY'])

    def start(self):
        self.client = Client()

    def stop(self):
        self.client = None

    def kill(self):
        self.client = None

    def get_dependency(self, worker_ctx):
        return self.client
