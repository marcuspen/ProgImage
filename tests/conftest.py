import pytest


@pytest.fixture
def cloudinary_config():
    return {
        'cloud_name': 'cloud_1',
        'api_key': 123,
        'api_secret': 'secret',
    }


@pytest.fixture
def config(web_config, cloudinary_config):
    return dict(
        AMQP_URI='pyamqp://guest:guest@localhost',
        CLOUDINARY=cloudinary_config,
        **web_config
    )
