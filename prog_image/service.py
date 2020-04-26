import json
from uuid import uuid4

from nameko.dependency_providers import Config
from nameko.rpc import rpc
from nameko.web.handlers import http
from werkzeug.wrappers import Response

from prog_image.dependencies.cloudinary import Cloudinary, ImageNotFound


class ImageService:
    name = "image_service"

    config = Config()
    image_host = Cloudinary()

    @rpc
    def new_image(self, image):
        image_id = uuid4().hex
        self.image_host.upload_image(image, image_id)

        return image_id

    @rpc
    def download_image(self, image_id):
        return self.image_host.download_image(image_id)

    @http('POST', '/image')
    def post_image(self, request):
        image = request.files['data']
        image_id = self.new_image(image)

        return create_json_response({'image_id': image_id})

    @http('GET', '/image/<image_id>')
    def get_image(self, request, image_id):
        try:
            raw_image = self.download_image(image_id)
        except ImageNotFound as err:
            return 404, str(err)
        else:
            response = create_image_response(raw_image)

            return response


def create_json_response(content):
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(content)
    return Response(json_data, status=200, headers=headers)


def create_image_response(image):
    headers = {'Content-Type': 'image/jpeg'}
    return Response(
        image,
        status=200,
        mimetype='image/jpeg',
        headers=headers,
        direct_passthrough=True,
    )
