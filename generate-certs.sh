#!/bin/sh
set -x

if ! command -v keytool &> /dev/null
then
    echo "This script requires keytool to be installed and on the path."
    exit
fi
if ! command -v openssl &> /dev/null
then
    echo "This script requires openssl to be installed and on the path."
    exit
fi

root_ca_subject="/C=US/ST=Your State/L=Your Locale/O=Example Org/CN=www.example.com"
root_ca_pass=changeme
panel_driver_subject="/C=US/ST=Your State/L=Your Locale/O=Example Org/CN=panel_driver"
driver_extra_dns=""
driver_extra_ip=""
panel_service_subject="/C=US/ST=Your State/L=Your Locale/O=Example Org/CN=panel_service"
service_extra_dns=""
service_extra_ip=""
web_client_subject="/C=US/ST=Your State/L=Your Locale/O=Example Org/CN=web_client"
password="changeme"
output_dir="./certs"

while getopts d:i:s:a:p:o: option
do
    case "${option}" in
        d) driver_extra_dns=${OPTARG};;
		i) driver_extra_ip=${OPTARG};;
		s) service_extra_dns=${OPTARG};;
		a) service_extra_ip=${OPTARG};;
		p) password=${OPTARG};;
		o) output_dir=${OPTARG};;
    esac
done

cd "$output_dir"

# Generate the Root CA certificate and key
openssl req \
	-x509 \
	-sha256 \
	-days 3650 \
	-newkey rsa:4096 \
	-subj "$root_ca_subject" \
	-keyout root_ca.key \
	-out root_ca.crt \
	-passout pass:$password

# Generate a signing request and key for the Panel Service
openssl req \
	-new \
	-newkey rsa:4096 \
	-nodes \
	-subj "$panel_service_subject" \
	-keyout panel_service.key \
	-out panel_service.csr

openssl rsa \
	-in panel_service.key \
	-out panel_service_nopass.key

# Create the cert extension file and sign the cert

echo "authorityKeyIdentifier=keyid,issuer" > panel_service.ext
echo "basicConstraints=CA:FALSE" >> panel_service.ext
echo "subjectAltName = @alt_names" >> panel_service.ext
echo "[alt_names]" >> panel_service.ext
echo "DNS.1 = localhost" >> panel_service.ext
if [ ! -z "$service_extra_dns" ]; then
	echo "DNS.2 = $service_extra_dns" >> panel_service.ext
fi
echo "IP.1 = 127.0.0.1" >> panel_service.ext
if [ ! -z "$service_extra_ip" ]; then
	echo "IP.2 = $service_extra_ip" >> panel_service.ext
fi

openssl x509 \
	-req \
	-CA root_ca.crt \
	-CAkey root_ca.key \
	-passin pass:$password \
	-in panel_service.csr \
	-out panel_service.crt \
	-days 365 \
	-CAcreateserial \
	-extfile panel_service.ext

#Import the panel service cert/key to a keystore for Spring

openssl pkcs12 \
	-export \
	-out panel_service.p12 \
	-name "panel_service" \
	-inkey panel_service.key \
	-in panel_service.crt \
	-password pass:$password

keytool \
	-importkeystore \
	-srckeystore panel_service.p12 \
	-srcstoretype PKCS12 \
	-srcstorepass $password \
	-destkeystore service_keystore.jks \
	-deststoretype JKS \
	-deststorepass $password

###

# Import the Root CA cert/key to a truststore for Spring

keytool \
	-import \
	-trustcacerts \
	-noprompt \
	-alias root_ca \
	-ext san=dns:localhost,ip:127.0.0.1 \
	-file root_ca.crt \
	-keystore truststore.jks \
	-storepass $password

# Create the Web client cert and key
openssl req \
	-new \
	-newkey rsa:4096 \
	-nodes \
	-subj "$web_client_subject" \
	-keyout web_client.key \
	-out web_client.csr

openssl x509 \
	-req \
	-CA root_ca.crt \
	-CAkey root_ca.key \
	-passin pass:$password \
	-in web_client.csr \
	-out web_client.crt \
	-days 365 \
	-CAcreateserial

# Export the certificate in PKCS12 format for authentication via a browser.

openssl pkcs12 \
	-export \
	-out web_client.p12 \
	-name "web_client" \
	-inkey web_client.key \
	-in web_client.crt \
	-password pass:$password

# Generate a signing request and key for the Panel Driver
openssl req \
	-new \
	-newkey rsa:4096 \
	-nodes \
	-subj "$panel_driver_subject" \
	-keyout panel_driver.key \
	-out panel_driver.csr

openssl rsa \
	-in panel_driver.key \
	-out panel_driver_nopass.key

# Create the cert extension file and sign the cert

echo "authorityKeyIdentifier=keyid,issuer" > panel_driver.ext
echo "basicConstraints=CA:FALSE" >> panel_driver.ext
echo "subjectAltName = @alt_names" >> panel_driver.ext
echo "[alt_names]" >> panel_driver.ext
echo "DNS.1 = localhost" >> panel_driver.ext
if [ ! -z "$driver_extra_dns" ]; then
	echo "DNS.2 = $driver_extra_dns" >> panel_driver.ext
fi
echo "IP.1 = 127.0.0.1" >> panel_driver.ext
if [ ! -z "$driver_extra_ip" ]; then
	echo "IP.2 = $driver_extra_ip" >> panel_driver.ext
fi

openssl x509 \
	-req \
	-CA root_ca.crt \
	-CAkey root_ca.key \
	-passin pass:$password \
	-in panel_driver.csr \
	-out panel_driver.crt \
	-days 365 \
	-CAcreateserial \
	-extfile panel_driver.ext

#Import the panel service cert/key to a keystore for Spring

# openssl pkcs12 \
# 	-export \
# 	-out panel_driver.p12 \
# 	-name "panel_driver" \
# 	-inkey panel_driver.key \
# 	-in panel_driver.crt \
# 	-password pass:$password

# keytool \
# 	-importkeystore \
# 	-srckeystore panel_driver.p12 \
# 	-srcstoretype PKCS12 \
# 	-srcstorepass $password \
# 	-destkeystore service_keystore.jks \
# 	-deststoretype JKS \
# 	-deststorepass $password