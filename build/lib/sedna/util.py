""" utilities shared across sedna project """
import uuid


def generate_uuid_str():
    """
    Generate a uuid string.
    :return: a uuid string
    """
    return str(uuid.uuid1())
