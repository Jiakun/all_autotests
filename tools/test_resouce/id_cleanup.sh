#! /bin/bash

NAME_PATTERN=$1
ID_PATTERN="[0-9a-f]\{32\}"

if [ -z $NAME_PATTERN ]; then
        echo "name pattern is required!"
        exit 1
fi

# cleanup project
PROJECTS=`openstack project list -c ID -c Name | grep -e "$NAME_PATTERN" | grep -e "$ID_PATTERN"`

if [ $? -gt 0 ]; then
    echo "No project found to delete!"
else
    PROJECTS=`echo "$PROJECTS" | awk -F "|" '{print $2}'`    
    
    for project in $PROJECTS;
    do
        echo "Deleting project $project"
        openstack project delete $project
    done
fi

# cleanup user
USERS=`openstack user list -c ID -c Name | grep -e "$ID_PATTERN" | grep -e "$NAME_PATTERN"`

if [ $? -gt 0 ]; then
    echo "No user found to delete!"
else
    USERS=`echo "$USERS" | awk -F "|" '{print $2}'`

    for user in $USERS;
    do
        echo "Deleing user $user"
        openstack user delete $user
    done
fi

# cleanup region
REGIONS=`openstack region list -c Region | grep -e "$NAME_PATTERN"`

if [ $? -gt 0 ]; then
    echo "No region found to delete!"
else
    REGIONS=`echo "$REGIONS" | awk -F "|" '{print $2}'`

    for region in $REGIONS;
    do
        echo "Deleting region $region"
        openstack region delete $region
    done
fi

