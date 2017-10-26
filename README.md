# Tracing Summit 2017

Here is the content of my presentation at the Tracing Summit 2017.

Aside from the presentation, you will find an example demonstrating
an example of a Babeltrace 2 component implemented in Python. The
component is imaginatively named `sink.demo.stacktrace`.

## Using `sink.demo.stacktrace`

### Building the software

In order to retrieve the function names from the addresses recorded in the
LTTng trace, the binary must contain DWARF debug information and the
compiler must instrument the various functions' entry and exit points.

Make sure to build your binary with the following `CFLAGS`:

`CFLAGS="-finstrument-functions -g"`

While the component will work even if the binary has no DWARF information, it
will only be able to display function names which are exported (public symbols).

### Tracing the software

This component depends on two events produced by LTTng-ust:
* `lttng_ust_cyg_profile_fast:func_entry`
* `lttng_ust_cyg_profile_fast:func_exit`

LTTng provides the `liblttng-ust-cygprofile-fast.so` shared object utility
in order to trace these events on the functions' entry and exit.
For more information, see the LTTng official documentation which has a
[dedicated section](https://lttng.org/docs/v2.10/#doc-liblttng-ust-cyg-profile)
on this mechanism.

#### Setup a tracing session

```
$ lttng create my_tracing_session
$ lttng enable-event --userspace --all
$ lttng add-context --userspace --type ip --type vpid
$ lttng start
```

#### Launch the program you want to trace

We will launch the `ls` utility, built with the debug information enabled.

`LD_PRELOAD="liblttng-ust-cyg-profile-fast.so" ls`

#### Stop and destroy the tracing session

```
$ lttng stop
$ lttng destroy
```

### Displaying a callstack

In order for `babeltrace` to see our new component, we need to make it aware
of the path in which it is saved. The `--plugin-path` option is used to add a
path to babeltrace's search path.

Let's list the plugins found by `babeltrace` and make sure we see our demo
component.

`$ babeltrace list-plugins --plugin-path ~/EfficiOS/confs/Tracing.Summit.2017/`

[![asciicast](https://asciinema.org/a/7KOvSQGJuoUWkGKtfTzrLozKs.png)](https://asciinema.org/a/7KOvSQGJuoUWkGKtfTzrLozKs)

Now we simply need to instruct babeltrace to
* Look for our plug-in in the appropriate path
* Insert a `filter.lttng-utils.debug-info` filter in the graph so that the function name, source filename and line number are added to the trace
* Use our new component, `sink.demo.stacktrace` as a sink

```
$ babeltrace --debug-info --plugin-path ~/EfficiOS/confs/Tracing.Summit.2017/ \
  --component sink.demo.stacktrace ~/lttng-traces/stacktrace-20171025-170540/
```

[![asciicast](https://asciinema.org/a/144340.png)](https://asciinema.org/a/144340)
