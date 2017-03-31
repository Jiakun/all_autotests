""" wrapper for Glance client's managers """
from os import path

from glanceclient.exc import HTTPNotFound

from sedna.error import NoneReferenceError
from sedna.openstack.base import ResourceManager
from sedna.openstack.common import Image

IMAGE_PATH = path.join(path.abspath(path.dirname(__file__)), "sedna_test.img")


class ImageManager(ResourceManager):
    """The class contains the logic to manipulate image in OpenStack"""

    def __init__(self, glance_client):
        super(ImageManager, self).__init__(glance_client, "images", Image)

    def upload_image(self, image, image_file_path):
        """
        Upload image data onto openstack
        :param image: the image record on OpenStack where to upload the data
        :param image_file_path: the file contains image data
        """
        if not image:
            raise NoneReferenceError(
                "image can't be None to upload image data")
        if not image.id:
            raise ValueError("image %s has not valid id" % image)
        if not path.exists(image_file_path)\
                or not path.isfile(image_file_path):
            raise ValueError("image file path %s is invalid!"
                             % image_file_path)

        with open(image_file_path, "rb") as image_file:
            self._os_resource_manager.upload(image.id, image_file)

    def get(self, image):
        """
        Get image by its id.
        :param image: volume object whose id is used to retrieve image data
        :return: image object got from openstack. None is returned when no
        data is found for the given id
        """
        try:
            return super(ImageManager, self).get(image)
        except HTTPNotFound:
            return None

    def list_by_nova(self, nova_client):
        nova_resource_manager = getattr(nova_client,
                                        "images")
        return nova_resource_manager.list()
