""" wrapper for Cinder client's managers """
from cinderclient.exceptions import NotFound

from sedna.error import NoneReferenceError
from sedna.openstack.base import ResourceManager
from sedna.openstack.common import Snapshot, Volume
from sedna.openstack.util import SyncStateChecker


class VolumeManager(ResourceManager):
    """The class contains the logic to manipulate volume in OpenStack"""

    def __init__(self, cinder_client):
        super(VolumeManager, self).__init__(cinder_client, "volumes", Volume)

    def get(self, volume):
        """
        Get volume by its id.
        :param volume: volume object whose id is used to retrieve volume data
        :return: Volume object got from openstack. None is returned when no
        data is found for the given id
        """
        try:
            return super(VolumeManager, self).get(volume)
        except NotFound:
            return None

    def create(self, resource):
        volume = super(VolumeManager, self).create(resource)

        sync_checker = SyncStateChecker()
        return sync_checker.wait_for_status(volume, "available", self.get)


class SnapshotManager(ResourceManager):
    """The class contains the logic to manipulate snapshot in OpenStack"""

    def __init__(self, cinder_client):
        super(SnapshotManager, self)\
            .__init__(cinder_client, "volume_snapshots", Snapshot)
        self.volume_manager = VolumeManager(cinder_client)

    def get(self, snapshot):
        """
        Get snapshot by its id.
        :param snapshot: snapshot object whose id is used to retrieve snapshot
        data
        :return: Snapshot object got from openstack. None is returned when no
        data is found for the given id
        """

        try:
            return super(SnapshotManager, self).get(snapshot)
        except NotFound:
            return None

    def create(self, resource):
        """
        Create a new OpenStack snapshot with the given data
        :param resource: the snapshot to create
        :return: the newly created snapshot
        """
        if not resource:
            raise NoneReferenceError("resource to create can't be None")

        if not isinstance(resource, self._resource_class):
            raise TypeError(
                "snapshot %s is not %s instance"
                % (resource, self._resource_class.__name__))

        snapshot = self.build_resource(
            self._os_resource_manager.create(
                volume_id=resource.volume.id, name=resource.name))

        sync_checker = SyncStateChecker()
        return sync_checker.wait_for_status(snapshot, "available", self.get)

    def build_resource(self, os_resource):
        snapshot = Snapshot(os_resource=os_resource)
        volume = self.volume_manager.get(Volume(os_resource.volume_id))
        snapshot.volume = volume
        return snapshot
