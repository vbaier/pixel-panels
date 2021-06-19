from setuptools import setup
from os.path import exists


def is_rpi():
    return exists("/sys/firmware/devicetree/base/model")


def specialize_dependencies():
    common_dependencies = ["pytz",
                           "numpy",
                           "Pillow",
                           "matplotlib"]
    rpi_dependencies = ["rpi-ws281x"]

    dependencies = common_dependencies

    if is_rpi():
        dependencies = dependencies + rpi_dependencies

    return dependencies


# Metadata goes in setup.cfg. These are here for GitHub's dependency graph.
setup(
    name="Pixelpanels",
    install_requires=specialize_dependencies(),
)
