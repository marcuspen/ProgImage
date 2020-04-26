# ProgImage

An Image service that allows you to upload images and download images given a unique ID.
It uses Cloudinary as an image host which will allow us in the future to utilize additional image processing features.

### Requirements

- Docker: https://www.docker.com/products/docker-desktop

### Getting started

First update the config.yaml with your cloudinary details.
To run, simply execute:

    $ docker-compose up

This will start the containers necessary to run ProgImage.

You can then access the following endpoints:


### How it works

#### Upload Image

    POST http://localhost:8999/image

Upload the image binary to this URL. Will return a unique ID of the image.
Example using CURL:

    $ curl --request POST --url http://localhost:8999/image -F 'data=@tests/test_data/test_image.jpg'
    >>> {"image_id": "b24c274e4e7a46c98e183ff669895472"}

#### Download Image

    GET http://localhost:8999/image/<image_id>

Will download the image of the supplied ID.
