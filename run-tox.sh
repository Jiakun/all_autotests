#!/usr/bin/env bash -e

PIP_SERVER="https://pypi.python.org/simple"
TOX_ENV_LIST="ALL"

while [ $# -gt 1 ]
do
    key="$1"
    case $key in
        -i)
        PIP_SERVER="$2"
        shift
        ;;
        -e)
        TOX_ENV_LIST="$2"
        shift
        ;;
    esac
    shift
done

echo "PIP_SERVER $PIP_SERVER"
echo "TOX_ENV_LIST $TOX_ENV_LIST"

WORKSPACE=$PWD
VENV="$WORKSPACE/venv"
PIP="$VENV/bin/pip"

function setup_venv() {
    if [ ! -d $VENV ]; then
        echo "setting up virtual environment"
        virtualenv $VENV
        echo "virtual environment is set up in directory $VENV"
    fi
}

setup_venv
source $VENV/bin/activate

echo "installing tox"
$PIP install tox -i $PIP_SERVER
echo "tox is installed"

#TOX=$VENV/bin/tox
TOXINI=$WORKSPACE/tox.ini
tox -c $TOXINI -i $PIP_SERVER -e $TOX_ENV_LIST

TOX_RESULT=$?

deactivate

exit "$TOX_RESULT"
