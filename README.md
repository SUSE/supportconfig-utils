Utilities for analyzing `supportconfig` tarballs
===================================================

This repository contains utilities which make it easier to inspect
files gathered into a
[supportconfig](http://www.novell.com/communities/node/2332/supportconfig-linux)
tarball.

Contents
--------

* [Project goals](#project-goals)
* [Installation](#installation)
* [Configuration](#configuration)
* [Usage](#usage)
* [List of core utilities](#list-of-core-utilities)
* [Product-specific extensions](#product-specific-extensions)


Project goals
-------------

The goals of this project are as follows:

*   Make the process of analysing supportconfigs as quick and easy as
    possible.

*   Provide more automation around the analysis, so that engineers can
    spend more time focusing on figuring out the root cause of problems
    rather than on the mechanics of extracting useful information.

*   Be extensible, allowing inclusion of product-specific
    intelligence, so that each product team can automatically drill
    down into product-specific debug data as quickly as possible.

*   Support analysis of multiple (and potentially related)
    supportconfigs at the same time.  The [`tmux` terminal
    multiplexer](https://en.wikipedia.org/wiki/Tmux) is used to help
    with this.

*   Provide a rich user interface for navigating and analysing subsets
    of potentially many / large log files.  The superb log file
    navigator [`lnav`](http://lnav.org/) is used for this.  Other
    utilities are provided for slicing and dicing the logs in various
    ways before feeding them to `lnav` for viewing.


Installation
------------

**It's strongly recommended to [install these via
packages](https://software.opensuse.org/package/supportconfig-utils)**.
This will automatically take care of the setup and dependencies on
[`tmux-lib`](https://software.opensuse.org/package/tmux-lib) and
[`unpack`](https://software.opensuse.org/package/unpack).

It's possible to install manually, but there really isn't any point,
so support for that will be provided reluctantly, if at all.


Configuration
-------------

By default, new terminal sessions will be launched using
`xdg-terminal`, which in theory should open your preferred terminal
emulator application.  However if this doesn't work to your taste, it
can be overridden by placing something like

    SUPPORTCONFIG_UTILS_TMUX_TERMINAL="urxvt-256color -g 200x60 -e"

in either `~/.config/supportconfig-utils/tmux-window` or
`/etc/sysconfig/supportconfig-utils`.

In the future, other configuration options may be added.  PRs are of
course welcome!


Usage
-----

You can launch a supportconfig analysis session in a few different
ways:

1.  From your web browser, in a new terminal window

    Simply click a supportconfig tarball to download it, and [the
    application MIME
    handler](share/applications/supportconfig-tmux.desktop) should kick
    in and launch a new terminal window with a new `tmux` session
    inside it.  (You may have to click the file again once it's
    downloaded, depending on how your browser is configured.)

2.  From a CLI, in a new terminal window

    Run

        supportconfig-tmux-window my-supportconfig.tar.bz2

    on a supportconfig you've already downloaded.  If it's already
    unpacked, you can run it directly on the unpacked directory:

        supportconfig-tmux-window my-unpacked-supportconfig/

    Again, this will create a new `tmux` session.

3.  From a CLI, in the same terminal window

    If you want to reuse an existing terminal window, follow the
    instructions in step 2 above, but replacing
    `supportconfig-tmux-window` with `supportconfig-tmux`.

The `tmux` session will launch various terminal windows depending on
the contents of the supportconfig.  Some may immediately launch `lnav`
on log files which are commonly viewed during analysis sessions, and
others may display other useful information as a starting point, and/or
offer an interactive shell ready for performing further exploration.

Once the session is launched, there are various other utilities
provided which may come in handy in certain situations.  See below for
details on the full suite of tools.


List of core utilities
----------------------

### Utilities for unpacking supportconfigs

*   [`unpack-supportconfig`](bin/unpack-supportconfig) - a wrapper
    around `split-supportconfig` which unpacks the tarball, runs
    `split-supportconfig *.txt`, and optionally deletes the packed
    tarball.  Requires the
    [`unpack`](https://software.opensuse.org/package/unpack).  utility
    for handling the tarball unpacking.  If you followed the
    recommendation to install these utilities via a package then the
    dependency will be taken care of, otherwise you will need to
    install [the
    script](https://github.com/aspiers/shell-env/blob/master/bin/unpack)
    somewhere on your `$PATH` before use.

*   [`split-supportconfig`](bin/split-supportconfig) - **Generally
    there is no need to run this directly.  Use `unpack-supportconfig`
    instead!** It extracts snapshots of any config file / log file
    etc. which is embedded inside a `.txt` file within the
    supportconfig.  For example `plugin-susecloud.txt` contains many
    files such as `var/log/crowbar/install.log`, which will be
    extracted to `rootfs/var/log/crowbar/install.log`.

### Utilities for setting up analysis/debugging sessions

*   [`supportconfig-tmux-window`](bin/supportconfig-tmux-window) - a
    wrapper around `supportconfig-tmux` which launches it in a new
    terminal window.  This can be used as an application to handle
    files with a `application/x-supportconfig` MIME type (defined
    [here](share/mime/packages/suse-supportconfig.xml)), so that for
    example analysis sessions can be launched via a single click when
    downloading supportconfig tarballs from your browser.  If you
    followed the recommendation to install this from a package, the
    MIME handler will be set up automatically; otherwise, you'll have
    to run `setup-supportconfig-handler` yourself.

    (In reality, there is another wrapper
    [`supportconfig-tmux-safe`](bin/supportconfig-tmux-window) in the
    middle between those two, which ensures that any error occurring
    during the unpacking or setup of the analysis session remains
    visible so that the user can correct it.)

*   [`supportconfig-tmux`](bin/supportconfig-tmux) - a wrapper around
    `unpack-supportconfig` which additionally creates a new `tmux`
    session with a window for viewing each of the log files which you
    most commonly look at.  There is also a dependency on [this simple
    `tmux`
    library](https://software.opensuse.org/package/tmux-lib)
    which should be installed into `~/.tmux.d`.

### Utilities for viewing log files

*   [`lnav2`](bin/lnav2) - a wrapper around lnav which adds some
    handy extra options / features


Product-specific extensions
---------------------------

The above utilities are designed to be extensible, so that extra
intelligence and automation can be added in order to further
facilitate analysis and debugging of particular SUSE products.

Plugins live in the [`plugins/`](plugins/) subdirectory.

### SUSE OpenStack Cloud

SUSE OpenStack Cloud plugins live in the
[`plugins/SOC/`](plugins/SOC/) subdirectory.

It is first worth noting that SUSE OpenStack Cloud includes [its own
plugin for
`supportconfig`](https://github.com/SUSE-Cloud/supportutils-plugin-suse-openstack-cloud/)
which gathers extra product-specific information into a supportconfig
tarball run on any node with the product installed.  The extensions
listed here take advantage of that extra information.

#### Crowbar-specific extensions (SOCC)

**WARNING:** some of these are probably ugly hacks which were coded in
a hurry.  Please [help make them better](CONTRIBUTING.md) ;-)

*   Reconnaissance / information gathering

    *   [`crowbar-MACs`](plugins/SOC/bin/crowbar-MACs) - prints a host
        (MAC) -> alias mapping from a Crowbar admin node supportconfig
        in YAML format.  This is used for informational display but
        can also be used by
        [`crowbar-IPs`](plugins/SOC/bin/crowbar-IPs) and
        [`rename-crowbar-logs`](plugins/SOC/bin/rename-crowbar-logs)
        (see below).

    *   [`crowbar-IPs`](plugins/SOC/bin/crowbar-IPs) - prints an IP ->
        alias mapping from a Crowbar admin node supportconfig in YAML
        format.  Requires a `MACS.yml` file generated by
        [`crowbar-MACs`](plugins/SOC/bin/crowbar-MACs).

*   Logfile preparation / normalization

    *   [`rename-crowbar-logs`](plugins/SOC/bin/rename-crowbar-logs) -
        rename one or more files or directories starting with "nts_d"
        followed by a MAC address, so that they include Crowbar node
        aliases.  Requires a `MACS.yml` file generated by
        [`crowbar-MACs`](plugins/SOC/bin/crowbar-MACs).

    *   [`postprocess-crowbar-logs`](plugins/SOC/bin/postprocess-crowbar-logs)
        improve readability / navigability of logs by replacing
        certain strings both inside the logs and in the filenames with
        more human-friendly or concise equivalents.  For example MAC
        addresses corresponding to hostnames are replaced with their
        Crowbar alias (if any), and `neutron-openvswitch` is
        abbreviated to `OVS`.

*   Logfile viewing

    *   [`crowbar-regexps`](plugins/SOC/bin/crowbar-regexps) - outputs
        a useful regexp which can be pasted into an `lnav` filter for
        a useful search or filter.

    *   [`crowbar-lnav-admin`](plugins/SOC/bin/crowbar-lnav-admin) -
        uses lnav to display a timeline of significant events on the
        Crowbar admin server.

    *   [`lnav-chef-sync-marks`](plugins/SOC/bin/lnav-chef-sync-marks) -
        show all synchronization points between Crowbar nodes in a
        cluster.

    *   [`lnav-crowbar-logs`](plugins/SOC/bin/lnav-crowbar-logs) -
        post-process, chronologically merge, and filter a bunch of
        SOCC logs in order to perform analysis on potentially
        significant events.  Expects a `log-files.yml` file detailing
        the list of logs to examine; see
        [`log-files.yml.sample`](plugins/SOC/etc/log-files.yml.sample)
        for an example of what this should look like.  The keys in the
        YAML map represent groups of log files, and are given as CLI
        arguments to `lnav-crowbar-logs` in order to select which
        groups of logs to view, e.g.

            lnav-crowbar-logs crowbar chef

        would launch `lnav` on all Crowbar/Chef logs, whereas

            lnav-crowbar-logs neutron_server neutron_agents

        would launch `lnav` on all neutron logs.

    *   [`lnav-SOCC-filters.txt`](plugins/SOC/etc/lnav-SOCC-filters.txt) -
        some `lnav` filters which filter SOCC logs for interesting
        events.  This is used by `lnav-logs` if you specify the `-f`
        option.

#### CLM-specific extensions

There aren't any Ardana / CLM extensions yet, but [PRs are warmly
welcomed](CONTRIBUTING.md) ;-)
