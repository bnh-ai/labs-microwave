#!/bin/bash

################################################################################
# This setup script performs the following commands
################################################################################

function error() {
    echo " " >&2
    echo "Error: $1.  Please contact BNH.AI customer support at luminos@bnh.ai if you need assistance resolving this error." >&2
    echo " " >&2
    exit 1
}

if [ `basename "$PWD"` == "scripts" ]; then
    cd ..
    echo "Setting up Jupyter notebook environment in $PWD ..."
    sleep 2
else
    error "The setup script should be run from the scripts folder"
fi

if [[ -d "./venv" ]]; then

    echo -e " "
    echo -e "It appears you already have already installed a Python virtual environment in "
    echo -e "the venv folder, as would be the case if you had run this setup script previously."
    echo " "
    echo -e "After you have installed a virtual environment, you do not need to install it "
    echo -e "again and can restart Jupyter by running the following commands in the folder "
    echo -e "$PWD:"
    echo " "
    echo -e "    source ./venv/bin/activate"
    echo -e "    jupyter notebook # or, equivalently, python3 -m jupyter notebook"
    echo " "
    echo -e "When you are finished using the notebook, you can shut down the Jupyter server with "
    echo -e "Ctrl-C and deactivate the virtual environment with the command "
    echo " "
    echo -e "    deactivate"
    echo " "
    exit 0

else

    echo " "
    echo -e "\tChecking whether you have virtualenv installed ..."
    if [ -z `which virtualenv` ]; then
        echo -e "\t\tThe setup script could not locate virtualenv so it will be installed now ..."
        sleep 2
        python3 -m pip install --user virtualenv
        EXITCODE=$?
        if [ $EXITCODE -ne 0 ]; then
            echo -e "\n"
            error "There was a problem installing the virtualenv tool to create virtual environments in Python so the setup script will terminate"
        else
            if [ -z `which virtualenv` ]; then
                # Sometimes virtualenv is not on the path even when it's already installed.
                # In such cases, trying to install virtualenv will be successful but it will still not be on the path.
                # This is particularly a known issue on MacOS.
                # The following condition checks if we can assume virtualenv is installed regardless.
                python3 -m pip show virtualenv
                EXITCODE=$?
                if [ $EXITCODE -ne 0 ]; then
                    echo -e "\n"
                    error "The virtualenv tool to create virtual environments in Python could still not be found so the setup script will terminate"
                else
                    # Assume virtualenv is installed and can be used since `pip show` finds it.
                    echo -e "\t\tIt appears that you may already have virtualenv installed but there were issues locating it"
                    echo -e "\t\tThe setup script will attempt to proceed assuming that virtualenv is correctly installed"
                fi
            else
                echo -e "\n"
                echo "\t\tThe installation of virtualenv was successful"
            fi
        fi
    else
        echo -e "\t\tYou appear to have virtualenv installed"
    fi

    echo " "
    echo -e "\tCreating Python virtual environment ..."
    sleep 2
    python3 -m virtualenv venv
    EXITCODE=$?
    if [ $EXITCODE -ne 0 ]; then
        error "There was a problem creating the Python virtual environment so the setup script will terminate"
    else
        echo -e "\t\tA Python virtual environment has been created in the folder ./venv."
    fi
fi

echo " "
echo -e "\tActivating the virtual environment ..."
sleep 2
source ./venv/bin/activate
EXITCODE=$?
if [ $EXITCODE -ne 0 ]; then
    error "There was a problem activating the Python virtual environment so the setup script will terminate"
fi
if [ -z $VIRTUAL_ENV ]; then
    error "It does not appear the virtual environment could be activated so the setup script will terminate"
fi

echo " "
echo -e "\tUpgrading pip (if necessary) ..."
sleep 2
./venv/bin/pip3 install --upgrade pip

echo " "
echo -e "\tInstalling Python modules required by the notebook (this may take a minute) ..."
sleep 2
./venv/bin/pip3 install -r ./requirements.txt
EXITCODE=$?
if [ $EXITCODE -ne 0 ]; then
    error "There was a problem installing the necessary Python modules so the setup script will terminate"
fi

echo " "
echo -e "\tGenerating signature for the Jupyter notebook ..."
sleep 2
python3 -m jupyter trust ./microwave/Microwave.ipynb
EXITCODE=$?
if [ $EXITCODE -ne 0 ]; then
    error "Jupyter encountered a problem signing the notebook so the setup script will terminate"
fi

echo " "
echo "Jupyter will now be started, after which a browser window will be opened and you "
echo "should navigate to the microwave folder and select the notebook Microwave.ipynb."
echo " "
echo "When you are finished with the notebook, you can shut down the Jupyter server by "
echo "pressing Ctrl-C and deactivate the virtual environment with the command 'deactivate'."
echo " "
echo "Starting Jupyter ..."
sleep 2
python3 -m jupyter notebook

