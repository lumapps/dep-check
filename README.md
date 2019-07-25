# dep-check

[![image](https://img.shields.io/pypi/v/dep-check.svg)](https://pypi.python.org/pypi/dep-check) [![CircleCI](https://circleci.com/gh/lumapps/dep-check/tree/master.svg?style=svg)](https://circleci.com/gh/lumapps/dep-check/tree/master)

## Version: Pre-alpha

dep-check is a Python dependency checker. First write rules on which module can import what, then **dep-check** will parse each source file to verify that everything is in order. You can also draw a dependency graph for your project.

**Free software:** MIT license

## Supported languages

* [Python](https://www.python.org/)
* [Go](https://golang.org/)

By default, the tool will assume it's python.

## Installation

To install **dep-check**, run this command in your terminal:

    pip install dep-check

This is the preferred method to install **dep-check**, as it will always
install the most recent stable release.

If you don't have [pip](https://pip.pypa.io) installed, this [Python installation guide](http://docs.python-guide.org/en/latest/starting/installation/) can guide you through the process. You can also see [other installation methods](https://github.com/lumapps/dep-check/blob/master/doc/installation.md).

## Usage

### Build your config file

First, you have to build your configuration file:

    dep_check build <ROOT_DIR> [-o config.yaml] [--lang LANG]

Argument | Description | Optional | Default
-------- | ----------- | -------- | -------
ROOT_DIR | The root directory of your project, containing you source files |:x:| *N/A*
-o | The output file you want (yaml format) |:heavy_check_mark:| dependency_config.yaml

By default, the config will be written in *dependency_config.yaml*.

This will only list the imports of each module. we recommand you to edit it using different wildcards to write rules on wich module can import what:

    ---

    dependency_rules:
    '*':
        - dep_check.models
        - dep_check.dependency_finder
        - dep_check.checker

    dep_check.infra.io:
        - dep_check.use_cases%
        - jinja2
        - yaml

    dep_check.infra.std_lib_filter:
        - dep_check.use_cases.interfaces

    dep_check.use_cases%:
        - dep_check.use_cases.app_configuration
        - dep_check.use_cases.interfaces

    dep_check.main:
        - '*'

    lang: python
    local_init: false

* `*` corresponds to any string, including an empty one
* `mymodule%` corresponds to `mymodule` and all of its submodules

*To see all the supported wildcards, and some examples, go check the [User Manual](https://github.com/lumapps/dep-check/blob/master/doc/usage.md#writing-your-own-configuration-file)!*

### Check your config

Once your config file is ready, just run

    dep_check check <ROOT_DIR> [-c config.yaml] [--lang LANG]

By default, the config will be read in *dependency_config.yaml*.

If nothing is printed, then congratulations! Everything is working great.

Otherwise, every error will be displayed as following:

    ERROR:root:module mymodule import othermodule but is not allowed to (rules: (set of rules for mymodule))

Furthermore, every unused rule in your configuration file will be displayed as a warning:

    WARNING:root:rule not used  mymodule: amodule.*

### Draw a dependency graph

You can draw a dependency graph by running

    # You need to have graphviz installed to run this
    dep_check graph <ROOT_DIR> [-o file.svg/dot] [-c config.yaml] [--lang LANG]

You can add a lot of options in a config file to customize your graph (hide some modules, add layers etc.). Go check the [User Manual](https://github.com/lumapps/dep-check/blob/master/doc/usage.md#adding-options)

## Contributing

If you want to make a contribution, be sure to follow the [Contribution guide](https://github.com/lumapps/dep-check/blob/master/doc/contributing.md) for more informations and some examples.

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) and the
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) project template

## Authors & contributors

Check out all the [Authors and contributors](https://github.com/lumapps/dep-check/blob/master/doc/authors.md) of this project!
