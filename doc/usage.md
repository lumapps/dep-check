# User Manual

## The configuration file

Don't forget to check out the [configuration file example](../dependency_config.yaml)

### Auto-build your configuration file

To build the configration file corresponding to your project, just run

    dep_check -b config_file.yaml ROOT_DIR

The file provided will only be a list of all the dependencies within your source files.
We recommend building your config file automatically, then editing it to match what you want.

### Writing your own configuration file

You can build your own configuration file, using wildcards. Here are the characters supported by the application :

* `*` corresponds to any string, including an empty one
* `?` corresponds to any single character
* `[abc]` corresponds to any character among 'a', 'b' or 'c'
* `[d-y]` corresponds to any character between 'd' and 'y'
* `[!d-y]` corresponds to any character which is **not** between 'd' and 'y'
* `[!abc]` corresponds to any character except 'a', 'b' or 'c'
* `mymodule%` corresponds to `mymodule` and all of its submodules

### Examples

    mymodule:
        - mymodule%
        - amodule.submodule.*
        - othermodul?_[0-9]

This will allow for `mymodule` to import:

* `mymodule`
* `mymodule.anything.moduleagain`
* `amodule.submodule.somemodule`
* `othermodulo_9`

Though, `mymodule` won't be able to import:

* `mymodule_07`
* `amodule`
* `amodule.submodule`
* `othermodulo_9.module`

*Note : if a `*` is alone on a line, it has to be between quotes :*

    mymodule:
        - '*'

## Checking your configuration

Once you've got your configuration file ready, simply run

    dep_check -c your_config_file.yaml ROOT_DIR

If nothing is printed, then congratulations! Everything is working great.

Otherwise, every error will be displayed as following:

    ERROR:root:module mymodule import othermodule but is not allowed to (rules: (set of rules for mymodule))

## Drawing a dependency graph

If you want to visualize your project dependencies as a graph, just run

    # You need to have graphviz installed to run this
    dep_check -g graph_file.svg ROOT_DIR

If you prefer having the graph in a dot file, then run

    dep_check -g graph_file.dot ROOT_DIR

*Note : if you generate a svg file, a dot file will be created in `/tmp/graph.dot`*
