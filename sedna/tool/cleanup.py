""" Classes to clean up openstack resources """


class ResourceCleaner(object):
    """ Class to clean up openstack resources"""

    def __init__(self, keystone_client):
        """
        Initializer
        :param keystone_client: keystone client
        """
        self.keystone_client = keystone_client

    def cleanup_users(self, users):
        """
        Clean up given users.
        :param users: users to clean up
        :return: the users deleted
        """
        if not users or len(users) < 1:
            return []
        deleted_users = []
        for user in users:
            if not user:
                continue

            self.keystone_client.users.delete(user)
            deleted_users.append(user)
        return deleted_users
