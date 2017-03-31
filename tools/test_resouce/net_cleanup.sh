#! /bin/bash

NAME_PATTERN=$1
ID_PATTERN="[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}"
HA_PORT_PATTERN="HA port tenant [0-9a-f]\{32\}"
HA_NET_PATTERN="HA network tenant [0-9a-f]\{32\}"

if [ -z $NAME_PATTERN ]; then
        echo "name pattern is required!"
        exit 1
fi

ROUTERS=`neutron router-list --all-tenants -F id -F name | grep -e "$ID_PATTERN" | grep "$NAME_PATTERN" | awk -F '|' '{print $2}'` 

#remove external network gateway of routers
for router in $ROUTERS;
do
    neutron router-list --id $router -F external_gateway_info | grep "network_id" &> /dev/null
    if [ $? -gt 0 ]; then
          echo "router $router has no external network gateway, skip the external gateway cleanup"
    else
        neutron router-gateway-clear $router
    fi
done

#remove the connection between router and subnet
for router in $ROUTERS;
do
    #ports=`neutron port-list --device-id $router -F id | grep -e $ID_PATTERN | awk -F "|" '{print $2}'`
    ports=`neutron port-list --device-id $router -F id -F name | grep -e "$ID_PATTERN" | grep -v "$HA_PORT_PATTERN" | awk -F "|" '{print $2}'`
    for port in $ports;
    do
       #echo "port: $port" 
       neutron router-interface-delete $router port=$port
    done
done

#cleanup routers
for router in $ROUTERS;
do
    neutron router-delete $router
done

NETS=`neutron net-list --all-tenants -F id -F name | grep -e "$ID_PATTERN" | grep -e "$NAME_PATTERN" | awk -F '|' '{print $2}'`

# cleanup net created for testing
for net in $NETS;
do
    neutron net-delete $net
done

# cleanup leaking HA network which belongs to the project gone
HA_NETS=`neutron net-list --all-tenants -F id -F name | grep -e "$HA_NET_PATTERN" | awk -F "|" '{print $2}'`

for ha_net in $HA_NETS;
do
    project_id=`neutron net-list --id $ha_net -F name | grep -e "$HA_NET_PATTERN" | awk '{print $5}'`
    openstack project show $project_id &> /dev/null
    if [ $? -gt 0 ]; then
        echo "$ha_net's project $project_id is NOT existed! Clean it up!"
        neutron net-delete $ha_net 
    else
        echo "$ha_net's project $project_id IS existed! Skip it!"
    fi 
done
