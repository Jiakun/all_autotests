""" The script to generate tempest configuration file """

from ConfigParser import ConfigParser, DEFAULTSECT

from keystoneauth1.identity.v3 import Password
from keystoneauth1.session import Session as OS_Session
from keystoneclient.v3.client import Client as Keystone_Client
from glanceclient.v2 import Client as GlanceClient
from neutronclient.v2_0.client import Client as NeutronClient
from novaclient.client import Client as NovaClient

auth_url = "http://lb.2.stage.polex.io:35357/"
admin_username = "admin"
admin_password = "f657d7e44ed39057a8d1d1ed"
admin_project_id = "66124df8b15b46dead4bff69ab35cdfb"
admin_domain_id = "default"
region = "RegionOne"

auth = Password(auth_url=auth_url + "v3",
        username=admin_username,
        password=admin_password,
        project_id=admin_project_id,
        user_domain_id=admin_domain_id
)

os_session = OS_Session(auth=auth)
keystone_client = Keystone_Client(session=os_session)

admin_project = keystone_client.projects.get(admin_project_id)
admin_domain = keystone_client.domains.get(admin_domain_id)

services = keystone_client.services.list()

glance_service = None
nova_service = None

for service in services:
    if service.name == "glance":
        glance_service = service
    if service.name == "nova":
        nova_service = service


glance_admin_endpoint = None
nova_admin_endpoint = None

for endpoint in keystone_client.endpoints.list(interface="admin"):
    if endpoint.service_id == glance_service.id:
        glance_admin_endpoint = endpoint
    if endpoint.service_id == nova_service.id:
        nova_admin_endpoint = endpoint


glance_client =\
        GlanceClient(endpoint=glance_admin_endpoint.id, session=os_session)

cirros_image = None
for image in glance_client.images.list():
    if image.has_key("image_type") and image["image_type"] == "snapshot":
        continue

    if "cirros" in image["name"]:
        cirros_image = image
        break

if cirros_image is None:
    raise Exception("no cirros image found!")


nova_client = NovaClient("2", session=os_session)

flavors = nova_client.flavors.list()

compute_hosts = nova_client.hosts.list("nova")


neutron_client = NeutronClient(session=os_session)
public_network = neutron_client.list_networks(**{"router:external": True})["networks"][0]


config = ConfigParser()


# DEFAULT section
config.set(DEFAULTSECT, "debug", "False")
config.set(DEFAULTSECT, "verbose", "False")

# alarming section
alarming_section_name = "alarming"
config.add_section(alarming_section_name)
# no option for alarming service

# auth section
auth_section_name = "auth"
config.add_section(auth_section_name)
config.set(auth_section_name, "use_dynamic_credentials", "True")
config.set(auth_section_name, "tempest_roles", "billing_owner")
config.set(auth_section_name, "admin_username", admin_username)
config.set(auth_section_name, "admin_tenant_name", admin_project.name)
config.set(auth_section_name, "admin_domain_name", admin_domain.name)

# baremetal section
baremetal_section_name = "baremetal"
config.add_section(baremetal_section_name)
# no option for baremetal

# compute section
compute_section_name = "compute"
config.add_section(compute_section_name)
config.set(compute_section_name, "image_ref", image["id"])
config.set(compute_section_name, "image_ref_alt", image["id"])
config.set(compute_section_name, "flavor_ref", flavors[0].id)
config.set(compute_section_name, "flavor_ref_alt", flavors[1].id)
config.set(compute_section_name, "min_compute_nodes", len(compute_hosts))

# compute-feature-enabled section
compute_feature_enabled_section_name = "compute-feature-enabled"
config.add_section(compute_feature_enabled_section_name)
config.set(compute_feature_enabled_section_name, "change_password", "True")
config.set(compute_feature_enabled_section_name, "resize", "True")
config.set(compute_feature_enabled_section_name, "console_output", "True")
config.set(compute_feature_enabled_section_name, "pause", "True")
config.set(compute_feature_enabled_section_name, "shelve", "True")
config.set(compute_feature_enabled_section_name, "suspend", "True")
config.set(compute_feature_enabled_section_name, "live_migration", "True")
config.set(compute_feature_enabled_section_name, "metadata_service", "True")
config.set(compute_feature_enabled_section_name,
        "block_migration_for_live_migration", "False")
config.set(compute_feature_enabled_section_name, "vnc_console", "True")
config.set(compute_feature_enabled_section_name, "spice_console", "False")
config.set(compute_feature_enabled_section_name, "rdp_console", "False")
config.set(compute_feature_enabled_section_name, "rescue", "True")
config.set(compute_feature_enabled_section_name, "interface_attach", "True")
config.set(compute_feature_enabled_section_name, "snapshot", "True")
config.set(compute_feature_enabled_section_name, "nova_cert", "True")
config.set(compute_feature_enabled_section_name,
           "scheduler_available_filters", "all")

# identity section
identity_section_name = "identity"
config.add_section(identity_section_name)
config.set(identity_section_name, "catalog_type", "identity")
config.set(identity_section_name, "uri", auth_url)
config.set(identity_section_name, "uri_v3", auth_url + "v3")
config.set(identity_section_name, "auth_version", "v3")
# TODO multi region scenario handling
config.set(identity_section_name, "region", region)
config.set(identity_section_name, "v2_admin_endpoint_type", "admin")
config.set(identity_section_name, "v2_public_endpoint_type", "public")
config.set(identity_section_name, "v3_endpoint_type", "admin")
config.set(identity_section_name, "admin_role", "admin")
config.set(identity_section_name, "default_domain_id", "default")

# identity-feature-enabled section
identity_feature_enabled_section_name = "identity-feature-enabled"
config.add_section(identity_feature_enabled_section_name)

# image section
image_section_name = "image"
config.add_section(image_section_name)
config.set(image_section_name, "catalog_type", "image")
config.set(image_section_name, "region", region)
config.set(image_section_name, "endpoint_type", "public")
config.set(image_section_name,
        "http_image",
        "http://download.cirros-cloud.net/0.3.1/cirros-0.3.1-x86_64-uec.tar.gz")
config.set(image_section_name, "build_timeout", "300")
config.set(image_section_name, "build_interval", "5")
config.set(image_section_name, "container_formats", "bare")
config.set(image_section_name,
        "disk_formats", "ami,ari,aki,vhd,vmdk,raw,qcow2,vdi,iso")

# image section
image_feature_enabled_section_name = "image-feature-enabled"
config.add_section(image_feature_enabled_section_name)
config.set(image_feature_enabled_section_name, "api_v2", "True")
config.set(image_feature_enabled_section_name, "api_v1", "True")
config.set(image_feature_enabled_section_name, "deactivate_image", "True")

# image section
input_scenario_section_name = "input-scenario"
config.add_section(input_scenario_section_name)

# negative section
negative_section_name = "negative"
config.add_section(negative_section_name)

# image section
network_section_name = "network"
config.add_section(network_section_name)
config.set(network_section_name, "catalog_type", "network")
config.set(network_section_name, "region", region)
config.set(network_section_name, "endpoint_type", "public")
config.set(network_section_name, "tenant_network_cidr", "10.100.0.0/16")
config.set(network_section_name, "tenant_networks_reachable", "False")
config.set(network_section_name, "public_network_id", public_network["id"])
config.set(network_section_name,
        "floating_network_name", public_network["name"])
config.set(network_section_name, "build_timeout", "300")
config.set(network_section_name, "build_interval", "5")

# network-feature-enabled section
network_feature_enabled_section_name = "network-feature-enabled"
config.add_section(network_feature_enabled_section_name)
config.set(network_feature_enabled_section_name, "ipv6", "true")
config.set(network_feature_enabled_section_name, "api_extensions", "all")

# object-storage section
object_storage_section_name = "object-storage"
config.add_section(object_storage_section_name)

# object-storage-feature-enabled section
object_storage_feature_enabled_section_name = "object-storage-feature-enabled"
config.add_section(object_storage_feature_enabled_section_name)

# orchestration section
orchestration_section_name = "orchestration"
config.add_section(orchestration_section_name)
config.set(orchestration_section_name, "catalog_type", "orchestration")
config.set(orchestration_section_name, "region", region)
config.set(orchestration_section_name, "endpoint_type", "public")
config.set(orchestration_section_name, "stack_owner_role", "heat_stack_owner")
config.set(orchestration_section_name, "build_timeout", "300")
config.set(orchestration_section_name, "build_interval", "5")
config.set(orchestration_section_name, "instance_type", "m1.micro")
config.set(orchestration_section_name, "max_template_size", "524288")
config.set(orchestration_section_name, "max_resources_per_stack", "1000")


# service_available section
service_available_section_name = "service_available"
config.add_section(service_available_section_name)
config.set(service_available_section_name, "cinder", "true")
config.set(service_available_section_name, "neutron", "true")
config.set(service_available_section_name, "glance", "true")
config.set(service_available_section_name, "swift", "false")
config.set(service_available_section_name, "nova", "true")
config.set(service_available_section_name, "heat", "true")
config.set(service_available_section_name, "ceilometer", "false")
config.set(service_available_section_name, "aodh", "false")
config.set(service_available_section_name, "horizon", "true")
config.set(service_available_section_name, "sahara", "false")
config.set(service_available_section_name, "ironic", "false")
config.set(service_available_section_name, "trove", "false")

# stress section
stress_section_name = "stress"
config.add_section(stress_section_name)

# telemetry section
telemetry_section_name = "telemetry"
config.add_section(telemetry_section_name)

# telemetry-feature-enabled section
telemetry_feature_enabled_section_name = "telemetry-feature-enabled"
config.add_section(telemetry_feature_enabled_section_name)

# validation section
validation_section_name = "validation"
config.add_section(validation_section_name)
config.set(validation_section_name, "run_validation", "true")
config.set(validation_section_name, "security_group", "true")
config.set(validation_section_name, "security_group_rules", "true")
config.set(validation_section_name, "connect_method", "floating")
config.set(validation_section_name, "auth_method", "keypair")
config.set(validation_section_name, "ip_version_for_ssh", "4")
config.set(validation_section_name, "ping_timeout", "60")
config.set(validation_section_name, "connect_timeout", "10")
config.set(validation_section_name, "ssh_timeout", "10")
config.set(validation_section_name, "image_ssh_user", "cirros")
config.set(validation_section_name, "image_ssh_password", "cubswin:)")
config.set(validation_section_name, "network_for_ssh", "public")

# volume section
volume_section_name = "volume"
config.add_section(volume_section_name)
config.set(volume_section_name, "catalog_type", "volume")
config.set(volume_section_name, "region", region)
config.set(volume_section_name, "endpoint_type", "public")
config.set(volume_section_name, "build_timeout", "300")
config.set(volume_section_name, "build_interval", "5")
config.set(volume_section_name, "backend_names", "ssd")
config.set(volume_section_name, "storage_protocol", "ceph")
config.set(volume_section_name, "vendor_name", "Open Source")
config.set(volume_section_name, "disk_format", "qcow2")
config.set(volume_section_name, "volume_size", "1")

# volume-feature-enabled section
volume_feature_enabled_section_name = "volume-feature-enabled"
config.add_section(volume_feature_enabled_section_name)
config.set(volume_feature_enabled_section_name, "multi_backend", "false")
config.set(volume_feature_enabled_section_name, "backup", "false")
config.set(volume_feature_enabled_section_name, "snapshot", "true")
config.set(volume_feature_enabled_section_name, "clone", "true")
config.set(volume_feature_enabled_section_name, "api_extensions", "all")
config.set(volume_feature_enabled_section_name, "api_v1", "true")
config.set(volume_feature_enabled_section_name, "api_v2", "true")
config.set(volume_feature_enabled_section_name, "bootable", "true")

with open("test.conf", "wb") as config_file:
    config.write(config_file)


