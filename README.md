# pixel-panels

This is a small tool to run animations on WS2812B-based LED displays.

# Installation

Install OS-level dependencies using apt on your pi. Please note that this includes some python packages that could be installed via pip. We install the OS package specifically due to binary incompatibility of those installed with pip

    sudo apt-get install libatlas-base-dev libopenjp2-7 libtiff5 python3 python3-numpy python3-matplotlib

Create a folder in the home directory of your raspberry pi named pixel-panels

	mkdir pixel-panels

Now copy the repo into this folder. If you are developing on windows and publishing to the pi there is a convenient deployment script using that uses [WinSCP](https://winscp.net/). To user it navigate to the `deploy` subdirectory on your windows host and run the below command adding your own credentials and raspberry pi address

    winscp /script=.\winScpPublish.script /parameter sftp://<user>:<password>@<IP address>/

You can now run `pip install .` in the `pixel-panels` directory to install the module.

# Running

You can run directly by executing the module as sudo with a path to a `*.gif` file. You can also optionally add a `--debug` parameter to display each frame as it is drawn on the panel.

    sudo python3 -m pixelpanels "./data/Test_64x32.gif"
    
NOTE: If you are using a python virtual environment you must be sure that you are specifying the path of the python3 executable within the environment. Due to the hardware-level calls, you must execute pixelpanels as root, and running `sudo` in a virtual environement will pickup whichever version of python is isntalled at the system level. Additionally, when creating your virtual environment be sure to create it with `--system-site-packages`. If you do not you will install binary-incompatible versions of the pixelpanel dependencies we installed with `apt-get`