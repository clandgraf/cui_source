
from setuptools import setup

setup(
    name =             "cui_source",
    version =          "0.0.1",
    author =           "Christoph Landgraf",
    author_email =     "christoph.landgraf@googlemail.com",
    description =      "Display Source Files in cui",
    license =          "BSD",
    url =              "https://github.com/clandgraf/cui_source",
    packages =         ['cui_source'],
    install_requires = ['pygments']
)
