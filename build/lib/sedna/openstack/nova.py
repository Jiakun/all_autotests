""" wrapper for nova resource """
from time import sleep
from exceptions import TypeError
from novaclient.exceptions import NotFound

from sedna.error import NoneReferenceError
from sedna.openstack.base import ResourceManager
from sedna.openstack.glance import ImageManager
from sedna.openstack.neutron import NetworkManager
from sedna.openstack.neutron import SubnetManager
from sedna.openstack.cinder import VolumeManager
from sedna.openstack.common import Server, Flavor
from sedna.openstack.common import Image
from sedna.openstack.common import Volume
from sedna.openstack.common import Keypair
from sedna.openstack.util import SyncStateChecker


class ServerManager(ResourceManager):
    """Manager class used to manipulate Server resource."""

    def __init__(self, nova_client, glance_client, neutron_client):
        super(ServerManager, self).__init__(nova_client, "servers", Server)
        self.glance_client = glance_client
        self.nova_client = nova_client
        self.neutron_client = neutron_client

        self.flavor_manager = FlavorManager(nova_client)
        self.image_manager = ImageManager(glance_client)
        self.neutron_manager = NetworkManager(neutron_client)
        self.subnet_manager = SubnetManager(neutron_client)

    def get(self, server):
        """
        Get server by its id.
        :param server: server object whose id is used to retrieve volume data
        :return: Server object got from openstack. None is returned when no
        data is found for the given id
        """
        try:
            return super(ServerManager, self).get(server)
        except NotFound:
            return None

    def create(self, resource):
        """
        Create a new OpenStack server with the given data
        :param resource: the server to create
        :return: the newly created server
        """
        if not resource:
            raise NoneReferenceError("Server to create cannot be None.")

        if not isinstance(resource, self._resource_class):
            raise TypeError("Server %s is not %s instance." %
                            (resource, self._resource_class.__name__))

        if isinstance(resource.image, Image):
            resource.image = self.glance_client.images.get(resource.image.id)

        if isinstance(resource.flavor, Flavor):
            resource.flavor = self.nova_client.flavors.get(resource.flavor.id)

        server_built = self.nova_client.servers.create(**vars(resource))
        server = self.build_resource(server_built)
        return server

    def create_server_volume(self, server, volume, cinder_client):
        """
        Attach a volume identified by the volume ID to the given server ID

        :param server: The object of the Server
        :param volume: The object of the Volume
        :param cinder_client: The object of CinderClient
        :return: attached a volume identified
                 by the volume ID to the given server ID
        """
        if not server:
            raise NoneReferenceError("Attach a volume identified "
                                     "by the volume ID to the given "
                                     "server ID cannot be None")
        if not volume:
            raise NoneReferenceError("Attach a volume identified "
                                     "by the volume ID to the given "
                                     "server ID cannot be None")
        if not isinstance(server, Server):
            raise TypeError(
                "resource %s is not %s instance"
                % (server, Server.__name__))
        if not isinstance(volume, Volume):
            raise TypeError(
                "resource %s is not %s instance"
                % (volume, Volume.__name__))
        if not hasattr(server, "id") or not server.id:
            raise NoneReferenceError(
                "The server's id is None. %s" % server)
        if not hasattr(volume, "id") or not volume.id:
            raise NoneReferenceError(
                "The volume's id is None. %s" % volume)
        self.nova_client.volumes.create_server_volume(
            server.id, volume.id)

        sync_checker = SyncStateChecker()
        cinder_manager = VolumeManager(cinder_client)
        temp = sync_checker.wait_for_status(
            volume, "in-use", cinder_manager.get)
        return temp

    def delete_server_volume(self, server, volume, cinder_client):
        """
        Detach a volume identified by the attachment ID from the given server

        :param server: The object of the Server
        :param volume: The object of the Volume
        :param cinder_client: The object of CinderClient
        """
        if not server:
            raise NoneReferenceError("Detach a volume identified "
                                     "by the volume ID to the given "
                                     "server ID cannot be None")
        if not volume:
            raise NoneReferenceError("Detach a volume identified "
                                     "by the volume ID to the given "
                                     "server ID cannot be None")
        if not isinstance(server, Server):
            raise TypeError(
                "resource %s is not %s instance"
                % (server, Server.__name__))
        if not isinstance(volume, Volume):
            raise TypeError(
                "resource %s is not %s instance"
                % (volume, Volume.__name__))
        if not hasattr(server, "id") or not server.id:
            raise NoneReferenceError(
                "The server's id is None. %s" % server)
        if not hasattr(volume, "id") or not volume.id:
            raise NoneReferenceError(
                "The volume's id is None. %s" % volume)
        self.nova_client.volumes.delete_server_volume(server.id, volume.id)
        sync_checker = SyncStateChecker()
        cinder_manager = VolumeManager(cinder_client)
        sync_checker.wait_for_status(volume, "available", cinder_manager.get)

    def update_server_volume(self, server_id, attachment_id, new_volume_id):
        """
        Update the volume identified by the attachment ID, that is attached to
        the given server ID

        :param server_id: The ID of the server
        :param attachment_id: The ID of the attachment
        :param new_volume_id: The ID of the new volume to attach
        :rtype: :class:`Volume`
        """
        # this method is not used
        if not server_id:
            raise NoneReferenceError("The lack of server_id fail to "
                                     "update the volume identified "
                                     "by the attachment ID, "
                                     "that is attached to "
                                     "the given server ID operation")
        if not attachment_id:
            raise NoneReferenceError("The lack of attachment_id fail to "
                                     "update the volume identified "
                                     "by the attachment ID, "
                                     "that is attached to "
                                     "the given server ID operation")
        if not new_volume_id:
            raise NoneReferenceError("The lack of new_volume_id fail to "
                                     "update the volume identified "
                                     "by the attachment ID, "
                                     "that is attached to "
                                     "the given server ID operation")
        server_volume_update = self.nova_client.servers.update_server_volume(
            server_id, attachment_id, new_volume_id)
        return server_volume_update

    def reboot(self, server):
        """
        Reboot a server.

        :param server: The :class:`Server` (or its ID) to share onto.
        """
        if not server:
            raise NoneReferenceError("The lack of server fail to "
                                     "reboot a server operation")
        self.nova_client.servers.reboot(server.id)

    def build_resource(self, os_resource):
        server = Server(os_resource=os_resource)
        while True:
            state = os_resource.__dict__["OS-EXT-STS:vm_state"]
            if state not in ("building", "Unknown"):
                break
            else:
                sleep(3)
                os_resource = self._os_resource_manager.get(os_resource.id)

        image = self.image_manager.get(Image(os_resource.image["id"]))
        flavor = self.flavor_manager.get(Flavor(os_resource.flavor["id"]))

        server.name = os_resource.name
        server.id = os_resource.id
        server.image = image
        server.flavor = flavor
        server.nics =\
            [{"net-name": os_resource._info.get("addresses").keys()[0]}]

        return server


class FlavorManager(ResourceManager):
    """Manager class used to manipulate Flavor resource"""
    def __init__(self, os_client):
        """
        initialization
        :param os_client: Openstack Nova client
        """
        self._os_client = os_client
        super(FlavorManager, self).__init__(os_client, "flavors", Flavor)

    def delete(self, resource):
        if not resource:
            raise NoneReferenceError("Flavor to delete is None!")

        if not isinstance(resource, self._resource_class):
            raise TypeError(
                "Flavor %s is not %s instance"
                % (resource, self._resource_class.__name__))

        if not hasattr(resource, "id") or not resource.id:
            raise NoneReferenceError(
                "The flavor's id to delete is None. %s" % resource)

        if resource.id not in\
                [flavor.id for flavor in self._os_client.flavors.list()]:
            raise NoneReferenceError("Flavor to delete is not in flavor-list!")

        return self._os_resource_manager.delete(resource.id)


class KeypairManager(ResourceManager):
    """Manager class used to manipulate Keypair resource"""
    def __init__(self, nova_client):
        """
        initialization
        :param nova_client: Openstack Nova client
        """
        self.nova_client = nova_client
        super(KeypairManager, self).__init__(nova_client, "keypairs", Keypair)

    # def create(self, keypair):
    #     if not keypair:
    #         raise NoneReferenceError("Keypair to create cannot be None.")
    #     if not isinstance(keypair, Keypair):
    #         raise TypeError(
    #             "keypair %s is not %s instance"
    #             % (keypair, Keypair.__name__))
    #     if not hasattr(keypair, "name") or not keypair.name:
    #         raise NoneReferenceError(
    #             "The keypair's name is None. %s" % keypair)
    #     return self.nova_client.keypairs.create(keypair.name)
    #
    # def delete(self, keypair):
    #     if not keypair:
    #         raise NoneReferenceError("Keypair to delete cannot be None.")
    #     self.nova_client.keypairs.delete(keypair)
