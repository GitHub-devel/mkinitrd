#
# spec file for package mkinitrd
#
# Copyright (c) 2011 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild


Name:           mkinitrd
License:        GPL-2.0+
Group:          System/Base
#!BuildIgnore:  module-init-tools e2fsprogs udev reiserfs fop
BuildRequires:  asciidoc libxslt
Requires:       coreutils modutils util-linux grep gzip sed cpio udev file perl-Bootloader
Requires:       xz
%if 0%{?suse_version} > 1120
Requires:       sysvinit-tools sbin_init
%else
Requires:       sysvinit
%endif
AutoReqProv:    on
Version:        @@VERSION@@
Release:        3
Conflicts:      udev < 118
Requires:       dhcpcd
PreReq:         %fillup_prereq
Summary:        Creates an Initial RAM Disk Image for Preloading Modules
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
Source0:        mkinitrd.tar.bz2
# Note: the whole package is maintained in this git repository, please
# don't change it in the build service without sending the author a
# pull request or patch first. Otherwise, you risk that your changes will be
# silently overwritten by the next submission.
Url:            http://gitorious.org/opensuse/mkinitrd

%description
Mkinitrd creates file system images for use as initial RAM disk
(initrd) images.  These RAM disk images are often used to preload the
block device modules (SCSI or RAID) needed to access the root file
system.

In other words, generic kernels can be built without drivers for any
SCSI adapters that load the SCSI driver as a module.  Because the
kernel needs to read those modules, but in this case is not able to
address the SCSI adapter, an initial RAM disk is used.	The initial RAM
disk is loaded by the operating system loader (normally LILO) and is
available to the kernel as soon as the RAM disk is loaded.  The RAM
disk loads the proper SCSI adapter and allows the kernel to mount the
root file system.



Authors:
--------
    Steffen Winterfeldt <wfeldt@suse.de>
    Susanne Oberhauser <froh@suse.de>
    Bernhard Kaindl <bk@suse.de>
    Andreas Gruenbacher <agruen@suse.de>
    Hannes Reinecke <hare@suse.de>
    Alexander Graf <agraf@suse.de>

%prep
%setup

%build
%__cc $RPM_OPT_FLAGS -Wall -Os -o lib/mkinitrd/bin/run-init src/run-init.c
%__cc $RPM_OPT_FLAGS -Wall -Os -o lib/mkinitrd/bin/warpclock src/warpclock.c
make -C man
sed -i "s/@BUILD_DAY@/`env LC_ALL=C date -ud yesterday '+%Y%m%d'`/" sbin/mkinitrd
echo "Checking scripts:"
if ! bash -n sbin/mkinitrd; then
    exit 1
fi
for script in scripts/*.sh; do
    if ! bash -n $script; then
        exit 1;
	break;
    fi
done

%install
mkdir -p $RPM_BUILD_ROOT/usr/share/mkinitrd
mkdir -p $RPM_BUILD_ROOT/lib/mkinitrd/dev
mkdir -p $RPM_BUILD_ROOT/lib/mkinitrd/scripts
mkdir -p $RPM_BUILD_ROOT/lib/mkinitrd/setup
mkdir -p $RPM_BUILD_ROOT/lib/mkinitrd/boot
mkdir -p $RPM_BUILD_ROOT/etc/init.d
mkdir -p $RPM_BUILD_ROOT/var/adm/fillup-templates
cp -a scripts/*.sh $RPM_BUILD_ROOT/lib/mkinitrd/scripts/
cp -a lib/mkinitrd/bin $RPM_BUILD_ROOT/lib/mkinitrd/bin
make -C sbin DESTDIR=$RPM_BUILD_ROOT install
chmod -R 755 $RPM_BUILD_ROOT/lib/mkinitrd
install -D -m 644 man/mkinitrd.5 $RPM_BUILD_ROOT/%{_mandir}/man5/mkinitrd.5
install -D -m 644 man/mkinitrd.8 $RPM_BUILD_ROOT/%{_mandir}/man8/mkinitrd.8
install -D -m 644 man/lsinitrd.8 $RPM_BUILD_ROOT/%{_mandir}/man8/lsinitrd.8
mkdir -p $RPM_BUILD_ROOT/etc/rpm
cat > $RPM_BUILD_ROOT/etc/rpm/macros.mkinitrd <<EOF
#
# Update links for mkinitrd scripts
#
%install_mkinitrd   /usr/bin/perl /sbin/mkinitrd_setup
EOF
install -m 755 etc/boot.loadmodules $RPM_BUILD_ROOT/etc/init.d/
install -m 755 etc/purge-kernels.init $RPM_BUILD_ROOT/etc/init.d/purge-kernels
install -m 644 etc/sysconfig.kernel-mkinitrd $RPM_BUILD_ROOT/var/adm/fillup-templates/

%post
%{fillup_only -an kernel}
%{insserv_force_if_yast /etc/init.d/boot.loadmodules}
%{fillup_and_insserv -f -Y purge-kernels}

%postun
%insserv_cleanup

%posttrans
/sbin/mkinitrd_setup

%files
%defattr(-,root,root)
%dir /etc/rpm
%dir /usr/share/mkinitrd
%dir /lib/mkinitrd
%dir /lib/mkinitrd/dev
%dir /lib/mkinitrd/bin
%dir /lib/mkinitrd/scripts
%dir /lib/mkinitrd/boot
%dir /lib/mkinitrd/setup
%config /etc/rpm/macros.mkinitrd
/etc/init.d/boot.loadmodules
/etc/init.d/purge-kernels
/lib/mkinitrd/scripts/*.sh
/lib/mkinitrd/bin/*
/bin/lsinitrd
/sbin/mkinitrd
/sbin/mkinitrd_setup
/sbin/module_upgrade
/sbin/installkernel
/sbin/purge-kernels
/var/adm/fillup-templates/sysconfig.kernel-%name
%doc %{_mandir}/man5/mkinitrd.5.gz
%doc %{_mandir}/man8/mkinitrd.8.gz
%doc %{_mandir}/man8/lsinitrd.8.gz

%changelog
