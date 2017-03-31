""" The tools used to verify resouce billing data """

from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session as OS_Session
from keystoneclient.v3.client import Client as Keystone_Client

from sedna.tool.orm import CinderDAO, GlanceDAO, GringottsDAO, NovaDAO,\
        NeutronDAO

import logging
from logging import StreamHandler

LOG = logging.getLogger("billing_verfier")
LOG.addHandler(StreamHandler())
LOG.setLevel(logging.ERROR)


def verify_billing(resource_id, resource_type):
    gringotts_dao = GringottsDAO(
        "mysql+pymysql://root:^polex$@10.0.2.37/gringotts")

    orders = gringotts_dao.get_orders(resource_id)
    if len(orders) is 0:
        LOG.info("==================================================")
        LOG.error("NO ORDER FOUND for %s %s " % (resource_type, resource_id))
        return

    for order in orders:
        LOG.info("==================================================")
        LOG.info("Order")
        LOG.info("\torder_id: " + order.order_id)
        LOG.info("\ttype: " + order.type)
        LOG.info("\tstatus: " + order.status)

        bills = gringotts_dao.get_bills(order.order_id)

        if len(bills) is 0:
            LOG.info("--------------------------------------------------")
            LOG.error(
                    "NO BILL FOUND for order %s, which belongs to %s %s"
                    % (order, resource_type, resource_id))
            continue
        for bill in bills:
            LOG.info("--------------------------------------------------")
            LOG.info("Bill")
            LOG.info("\tbill_id: " + bill.bill_id)
            LOG.info("\tstatus: " + bill.status)
            LOG.info("\tstart_time: %s" % bill.start_time)
            LOG.info("\tend_time: %s" % bill.end_time)
    return


def verify_volume_biil(project):
    cinder_dao = CinderDAO("mysql+pymysql://root:^polex$@10.0.2.37/cinder")
    volumes = cinder_dao.get_volumes(project.id)

    for volume in volumes:
        LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")
        LOG.info("Volume")
        LOG.info("\tname: %s" % volume.display_name)
        LOG.info("\tid: " + volume.id)
        LOG.info("\tstatus: " + volume.status)

        verify_billing(volume.id, "volume")

    LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")


def verify_snapshot_biil(project):
    cinder_dao = CinderDAO("mysql+pymysql://root:^polex$@10.0.2.37/cinder")
    snapshots = cinder_dao.get_snapshots(project.id)

    for snapshot in snapshots:
        LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")
        LOG.info("snapshot")
        LOG.info("\tid: " + snapshot.id)
        LOG.info("\tvolume_id: " + snapshot.volume_id)
        LOG.info("\tstatus: " + snapshot.status)

        verify_billing(snapshot.id, "snapshot")

    LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")


def verify_instance_biil(project):
    nova_dao = NovaDAO("mysql+pymysql://root:^polex$@10.0.2.37/nova")
    instances = nova_dao.get_instances(project.id)

    for instance in instances:
        LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")
        LOG.info("instance")
        LOG.info("\tname: %s" % instance.display_name)
        LOG.info("\tid: " + instance.uuid)
        LOG.info("\tdeleted: %s" % instance.deleted)

        verify_billing(instance.uuid, "instance")

    LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")


def verify_router_biil(project):
    neutron_dao = NeutronDAO("mysql+pymysql://root:^polex$@10.0.2.37/neutron")
    routers = neutron_dao.get_routers(project.id)

    for router in routers:
        LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")
        LOG.info("router")
        LOG.info("\tname: %s" % router.name)
        LOG.info("\tid: " + router.id)
        LOG.info("\tstatus: %s" % router.status)

        verify_billing(router.id, "router")

    LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")


def verify_image_snapshot_biil(project):
    glance_dao = GlanceDAO("mysql+pymysql://root:^polex$@10.0.2.37/glance")
    snapshots = glance_dao.get_snapshots(project.id)

    for snapshot in snapshots:
        LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")
        LOG.info("snapshot")
        # LOG.info("\tname: %s" % router.name)
        LOG.info("\tid: " + snapshot.id)
        LOG.info("\tstatus: %s" % snapshot.status)

        verify_billing(snapshot.id, "snapshot")

    LOG.info("++++++++++++++++++++++++++++++++++++++++++++++++++")


def get_project(project_name):
    auth = Password(auth_url="http://10.0.2.37:35357/v3",
                    username="admin",
                    password="f657d7e44ed39057a8d1d1ed",
                    project_id="66124df8b15b46dead4bff69ab35cdfb",
                    user_domain_id="default"
                    )
    os_session = OS_Session(auth=auth)
    keystone_client = Keystone_Client(session=os_session)
    project = keystone_client.projects.list(**{"name": project_name})[0]
    return project


""" the verifying logic starts here """
project = get_project("rally_project")

LOG.error("Starting verifying volumes")
verify_volume_biil(project)
LOG.error("Starting verifying snapshots")
verify_snapshot_biil(project)
LOG.error("Starting verifying instances")
verify_instance_biil(project)
LOG.error("Starting verifying routers")
verify_router_biil(project)
LOG.error("Starting verifying image snapshot")
verify_image_snapshot_biil(project)
LOG.error("Verifying finished")
