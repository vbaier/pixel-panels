# pixel-panels

This is a small tool to run animations on WS2812B-based LED displays.

# Setup for running the CLI locally

The simplest way to run pixelpanels is as a local module. It can be debugged/developed on x86/x64 or run against Pixel Panel hardware via a Raspberry Pi. Running locally requires Python 3.7 or later.

## x86/x64 Setup

The x86/x64 implementation runs comfortably in a python virtual environment and has been tested on debian-family distros and windows.

Upgrade pip and install wheel to ensure binary packages are available and installed quickly.

	pip install --upgrade pip
	pip install wheel

To debug you will need a GUI backend for matplot-lib The easiest method on x86 is to install a qt backend with pip which matplotlib will pick up.

	pip install pyqt5

Finally complete installation from the PanelDriver folder via

	pip install .

## Raspberry Pi Setup

Installation on a pi with Raspbian is a bit tricky as there are some specific binary dependencies that aren't available directly from the Python Package Index. Instead these are installed from the package manager which adds them to site-packages.

    sudo apt-get install libatlas-base-dev libopenjp2-7 libtiff5 python3 python3-numpy python3-matplotlib

Navigate to the PanelDriver folder and run

	pip install .

## Running the local CLI

Currently the local CLI only supports one command, running a gif on an infinite loop. Give it a go from the PanelDriver folder by running

    sudo python3 -m pixelpanels "../data/Test_64x32.gif"

 If you are on an x86/x64 machine or don't have Pixel Panel hardware, run with the `--debug` option to get a debug window of what is being sent to the panel display

# Setup for Running Remotely via the Web Application

Controlling the Pixel Panel remotely requires two components. The Panel Driver which hosts a gRPC server and commands the display hardware (or debug window) and the Panel Service which takes commands from the web and sends them over to the Panel Driver display the results.

## Certificates

Since we're generally planning to expose hardware to the internet with this project, the system is designed to use x509 certificate authentication between the Panel Driver and the Panel Service as well as between any user and the Panel service.

### Default Certificates

Default certificates are provided for local debugging, but it is strongly recommended to create new ones before deploying anything. The password for all default certificates is "changeme"

### Creating New Self-Signed Certificates

Here we cover the process for generating new self-signed certificates, though you can easily extend this to authoritative certificates from a third party service. Certificate creation will require openssl and keytool. On windows I recommend installing Msys2 and performing these tasks from there.

Create a certificate for your root Certificate Authority. You only need to enter a password and a common name (cn), you can leave all other fields blank.

	openssl req -x509 -sha256 -days 3650 -newkey rsa:4096 -keyout rootCA.key -out rootCA.crt

Create a certificate signing request for the Panel Service server. As before, only a password and common name are needed.

	openssl req -new -newkey rsa:4096 -nodes -keyout server.key -out server.csr

Create a version of the server private key with the password stripped for later usage with gRPC which doesn't play nice with password-protected keyfiles

	openssl rsa -in server.key -out server_nopass.key

Generate the actual certificate. You will need an .ext file as an input. Modify the default server.ext file provided in the `certs` folder as needed

	openssl x509 -req -CA rootCA.crt -CAkey rootCA.key -in server.csr -out server.crt -days 365 -CAcreateserial -extfile server.ext

Convert the certificate to PKCS12 for importing into the java keystore and then create the keystore

	openssl pkcs12 -export -out server.p12 -name "server" -inkey server.key -in server.crt

	keytool -importkeystore -srckeystore server.p12 -srcstoretype PKCS12 -destkeystore keystore.jks -deststoretype JKS

Create a truststore with our root CA which we are using to sign certificates

	keytool -import -trustcacerts -noprompt -alias ca -ext san=dns:localhost,ip:127.0.0.1 -file rootCA.crt -keystore truststore.jks

Create a client cert for calling the Panel Driver. In our naive implementation, this is also the certificate that is used to access the Panel Service

	openssl req -new -newkey rsa:4096 -nodes -keyout client.key -out client.csr
	CN=pi_client

	openssl x509 -req -CA rootCA.crt -CAkey rootCA.key -in client.csr -out client.crt -days 365 -CAcreateserial

Export the certificate in PKCS12 format for authentication via a browser.

	openssl pkcs12 -export -out client.p12 -name "pi_client" -inkey client.key -in client.crt

### Installing Certificates

Install your root CA and and the pi_client (client.p12) certificate in your browser to authenticate when accessing the Panel Service. An example of adding certificates in Chrome on Windows is below.

https://support.globalsign.com/digital-certificates/digital-certificate-installation/install-client-digital-certificate-windows-using-chrome

## Configuring the Panel Driver to listen via gRPC

After installing the module navigate to the PanelDriver folder and run

	python -m pixelpanels.rpcserver

Much like the local CLI this can be run with the `--debug` option for devices not-connected to Pixel Panel hardware

## Running the Panel Service

The panel service is built from source with maven and Java 17. Install these dependencies on your platform and then run the following from the PanelService folder

	mvn clean
	mvn install

To start the service run the following from the PanelService/SpringService folder

	mvn spring-boot:run

## Trying the Panel Service

If both the Panel Driver and Panel Service are running then you can navigate to the following location and you should see a debug image play.

https://localhost:8443/PlayGif

# Development workflow on windows

To quickly iterate on the Panel Driver portion of the system I've created a simple workflow on windows for deploying and testing updates

Create a folder in the home directory of your raspberry pi named pixel-panels

	mkdir pixel-panels

Now copy the repo into this folder. If you are developing on windows and publishing to the pi there is a convenient deployment script using that uses [WinSCP](https://winscp.net/). To user it navigate to the `deploy` subdirectory on your windows host and run the below command adding your own credentials and raspberry pi address

    winscp /script=.\winScpPublish.script /parameter sftp://<user>:<password>@<IP address>/

You can now run `pip install .` in the `pixel-panels` directory to install the module.

# Outstanding Tasks

* Expand documentation of the Panel Service
* Improve naming and file structure
* Clean up .gitignore files
* Connect the image upload call to the PlayGif feature on the Raspberry Pi
* And a unique client certificate for the browser client
* Migrate dependency management to a pipenv workflow
* Update to latest packaging standards with project.toml
