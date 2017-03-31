from neutronclient.v2_0.client import ClientBase
from neutronclient.v2_0.client import Client


class SednaClient(Client, ClientBase):
    router_path = "/routers/%s"
    portforwarding_path = router_path + "/portforwardings/%s"
    portforwardings_path = router_path + "/portforwardings"

    EXTED_PLURALS = {'routers': 'router',
                     'portforwardings': 'portforwarding'
                     }

    def list_portforwardings(self, router, retrieve_all=True, **_params):
        """Fetches a list of all portforwardings for a project."""
        return self.list('portforwardings', self.portforwardings_path % router,
                         retrieve_all, **_params)

    def show_portforwarding(self, portforwarding, router, **_params):
        """Fetches information of a certain portforwarding."""
        return self.get(self.portforwarding_path % (router, portforwarding),
                        params=_params)

    def create_portforwarding(self, router, body=None):
        """Creates a portforwarding."""
        return self.post(self.portforwardings_path % router, body=body)

    def update_portforwarding(self, portforwarding, router, body=None):
        """Updates a portforwarding."""
        return self.put(self.portforwarding_path % (router, portforwarding),
                        body=body)

    def delete_portforwarding(self, portforwarding, router):
        """Deletes the specified portforwarding."""
        return self.delete(self.portforwarding_path % (router, portforwarding))
