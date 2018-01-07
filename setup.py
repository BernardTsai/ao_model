from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name                 = "ao",
    version              = "0.0.0",
    description          = "LCM with the help of a model based descriptor",
    url                  = "http://github.com/btsai/ao_model",
    classifiers          = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3"],
    keywords             = "model lifecycle automation descriptor",
    author               = "Bernard Tsai",
    author_email         = "bernard@tsai.eu",
    license              = "Apache License",
    packages             = ["ao","ao.model","ao.cli"],
    entry_points         = {
        'console_scripts': [
            'generator=ao.cli.generator:main',
            'validator=ao.cli.validator:main'
            'splitter=ao.cli.splitter:main'
        ]
    },
    package_dir          = {"ao": "ao" },
    package_data         = {"ao": ["data/schemas/V0.1.1/*","data/templates/V0.1.1/*","data/test/V0.1.1/*"] },
    install_requires     = ["pyyaml","jsonschema","jinja2"],
    include_package_data = True,
    zip_safe             = False)
