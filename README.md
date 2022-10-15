# Automated BSD Installer generator

Usage:
* clean up after yourself:
	sudo make clean
* generate the iso image:
  with basic settings:
	sudo make
  for another version, than the default
	sudo make RELVER=12.3
  installing other than just the base.txz and kernel.txz onto the new system
	sudo make DISTRIBUTIONS='base.txz kernel.txz ports.txz'

## How it works
* Extracts the contents of the original FreeBSD installer iso file
* Generates an /etc/installerconfig file onto the work directory
* Clean up the usr/freebsd-dist directory, so the resulting .iso file will be smaller, and only contains those distribution files, what is defined in the DISTRIBUTIONS makefile variable on iso generation
* do some minor editing on the rc.local file, so the installation will not require any user interaction

### Why do I need to "generate" the installerconfig
First of all, I tried to make this as flexible as possible. Because of this I didn't wanted to hardcode the DISTRIBUTIONS setting into that file. You can generate the iso to your own flavour.
It strips the rest of the tarballs, and the DISTRIBUTIONS setting will represent your selection in the installerconfig file.
Second, that's the more interesting part:
As a post-install step it will run an rc script to do automated settings on your machine on its first boot.
In order to do that, sets the ifconfig_DEFAULT sysrc to DHCP.
The *setup_on_firstboot* script was moved to a separate file so, it's more manageable.
Another important gotcha: Do not try to move the shebang inside the here-is-the-document section.
The bsd installer chops the installerconfig into as many pieces as many shebangs it founds, which results if it founds another shebang in the installerconfig that section won't get into the actual script file which runs after the automated installation.
But, if I just printf the shebang line to the resulting script, than copy the rest, the bsdinstall won't chop the resulting config into 3 piece instead of two.

### Why do I need to patch the rc.local file
It would stop at the very beginning to ask about your terminal. I do not want any interaction during the install process.
Also, if you want to have a different partitioning scheme, you can solve that.
Eg. my taste is to not use mbr, just bsd slices on the disk.

If I want this simplified thing to work in a bhyve vm, I've just add this to my vm's config:
    bhyveload_args="-e custom.partitions=vtbd0_BSD -e custom.rootdev=ufs:/dev/vtbd0a"

Please not the Underscore in the parameters. Even if you could pass with a direct kenv parameter a space as part of the custom.partitions settings value, the vm-bhyve will separate it into pieces. My workaround for that is, that when the script reads out the kenv setting, replaces every underscore to spaces. In theory, you won't have underscores in the device names anyway.
But, because of this partitioning setup, the freshly installed system won't be able to boot on it's own, so I have to add a vfs.root.mountfrom setting to my loader.conf.
This is what the script also does during the installation, before the reboot.

Btw, though the security.bsd.allow_destructive_dtrace=0 is hardcoded into the default settings, feel free to remove as a post-installation step if you feel so.
I plan to move more security hardening default settings here.

### How will the setup_on_firstboot rc script know, what to do on the first boot?
As I wrote above, I tried to not hardcode anything, and make it as flexible as possible.
It will look for the 'extensions-path' setting in the dhcp lease file.
https://www.rfc-editor.org/rfc/rfc2132.html#page-10
Section 3.20 Extensions-path.
I use this to provide an url to fetch the rest of the installation instructions.

## Examples

Examples to actually use the automation to leverage the features of the resulting iso

### dnsmasq config

Add these lines to your dnsmasq config for those hosts where you want to provide this url:
    dhcp-option-force=bsdi,18,http://srv.dmz.intra/p.cgi
    dhcp-host=00:01:de:ad:be:ef,10.1.2.3,set:bsdi,host1
    dhcp-host=00:02:de:ad:be:ef,10.1.2.4,set:bsdi,host2
    
On the first boot, the host1 will fetch the following url:
http://srv.dmz.intra/p.cgi?mac=00:01:de:ad:be:ef&host=host1&ip=10.1.2.3

### The cgi

Check the examples directory for my solution.

The cgi tries to find a file based on the mac, hostname and ip address.
It has a similar mechanism like the syslinux's pxe variant does to find its own configuration file on the tftp server.
Just in my case, I not just try to remove one character from the full mac address all the time, but I do the same with the IP address as well. And as a fallback option, the hostname can be a simple underscore as well.
Check the example file, it's simpler to read, than explain the algorightm.

### An actual file I used as a postinstall step

It's quite simple:
Fetches my github ssh keys, and let me log in with my public ssh keys to the host as root.
Also installs sudo, and let me sudo to root unlimited.
So, from this point on, I can manage the freshly installed host via ansible.
Though, for that it could be a good idea, to add python to the installed packages as well. ;)

