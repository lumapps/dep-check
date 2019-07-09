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

### Adding options

Don't forget to check out the [graph configuration example](../graph_config.yaml)

The graph you'll get may seem unreadable if your project is pretty big. If that's the case, you can add options to the graph you want to draw, using a YAML file :

    dep_check -g graph_file.svg -o graph_config.yaml ROOT_DIR

Here are the different options:

#### Fold a module

You can chose to 'fold' one or more modules, which will bring together all of their submodules into the module(s), making the graph way more readable.

To do so, you'll have to add a "fold_modules" in your graph config file:

    fold_modules:
        - root.amodule
        - root.module.submodule

#### Hide a module

You can also chose to hide entirely a module, which will remove it from the dependency graph, along with its submodules.

To do so, you'll have to add a "hide_modules" in your graph config file:

    hide_modules:
        - root.amodule

**Make sure the name of the module you want to fold/hide start at the root of your project** (e.g. 'root.amodule' and not 'amodule')

#### Add color

You can change the nodes and/or background color of the graph, using 'node_color' and 'bgcolor' options: ([Here are the colors you can use](https://www.graphviz.org/doc/info/colors.html))

    node_color: crimson
    bgcolor: gold

*Note: if not defined, the nodes are white and the background is transparent.*

#### Add layers

You can add layers to your graph, grouping modules as you want (e.g. according to Clean Architecture layers).

To do so, you'll have to add a "layers" in your graph config file. Then for each layer you want, you have to inform the color of the nodes, and the list of modules in your layer.

*Note: each module you'll write will include its submodules. If you write `root.module` in a layer's list of modules, all of its submodules will be added in the layer as well*

    layers:
        my_first_layer:
            color: green
            modules:
                - root.module.submodule
                - root.othermodule
        my_second_layer:
            color: blue
            modules:
                -root.amodule

All of the modules which are not in a layer will be displayed normally.
