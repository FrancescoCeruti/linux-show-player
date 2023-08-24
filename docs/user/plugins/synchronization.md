# Synchronization

The goal of this plugin is to allow multiple LiSP sessions, running on different
computers, to be synchronized during a show (no edit synchronization). The sessions must be identical.

## How to use

The plugin usage is simple, you only need to add the remote sessions you want to "control" as a host,
this can be done via `Tools > Synchronization > Mange connected peers`

```{image} ../_static/synchronization_hosts.png
:alt: Manage synchronization hosts
```

On the left you can find the connected hosts, on the right the following buttons:

* **Discover hosts:** search for other active LiSP sessions in the network
* **Manually add host:** manually add a host, using its IP address
* **Remove selected host:** remove the selected host
* **Remove all hosts:** remove all the hosts

To easily retrieve the (local) IP address `Tools > Synchronization > Show your IP`
will display the current IP address of your computer.

Once a session is connected, direct actions on cues will be replicated onto it.<br>
Two or more sessions can be mutually connected.
