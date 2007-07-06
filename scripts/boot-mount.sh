#!/bin/bash
#%requires: resume
#%programs: /sbin/fsck $rootfsck
#%modules: $rootfsmod
#%if: ! "$root_already_mounted"
#%dontshow
#
##### mounting of the root device
##
## When all the device drivers and other systems have been successfully
## activated and in case the root filesystem has not been mounted yet,
## this will do it and fsck it if neccessary.
##
## Command line parameters
## -----------------------
##
## rw		mount the root device read/write
## ro		mount the root device read-only
## 

[ "$( ( set -u; echo $rw >/dev/null; echo 1 ) 2>/dev/null )" = "1" ] && read_write=1
[ "$( ( set -u; echo $ro >/dev/null; echo 1 ) 2>/dev/null )" = "1" ] && read_write=

# And now for the real thing
if ! udev_discover_root ; then
    echo "not found -- exiting to /bin/sh"
    cd /
    PATH=$PATH PS1='$ ' /bin/sh -i
fi

if [ -z "$rootfstype" ]; then
    rootfstype=$(/lib/udev/vol_id -t $rootdev)
    [ $? -ne 0 ] && rootfstype=
    [ -n "$rootfstype" ] && [ "$rootfstype" = "unknown" ] && $rootfstype=
fi

# check filesystem if possible
if [ -z "$rootfstype" ]; then
    echo "invalid root filesystem -- exiting to /bin/sh"
    cd /
    PATH=$PATH PS1='$ ' /bin/sh -i
elif [ -x "$rootfsck" ]; then
    # fsck is unhappy without it
    echo "$rootdev / $rootfstype defaults 1 1" > /etc/fstab
    # Display progress bar if possible 
    fsckopts="-V -a"
    [ "`/sbin/showconsole`" = "/dev/tty1" ] && fsckopts="$fsckopts -C"
    # Check external journal for reiserfs
    [ "$rootfstype" = "reiserfs" -a -n "$journaldev" ] && fsckopts="-j $journaldev $fsckopts"
    fsck -t $rootfstype $fsckopts $rootdev
    # Return the fsck status
    ROOTFS_FSCK=$?
    export ROOTFS_FSCK
    ROOTFS_FSTYPE=$rootfstype
    export ROOTFS_FSTYPE
    if [ $ROOTFS_FSCK -gt 1 -a $ROOTFS_FSCK -lt 4 ]; then
        # reboot needed
        echo "fsck succeeded, but reboot is required."
        echo "Rebooting system."
        /bin/reboot -d -f
    elif [ $ROOTFS_FSCK -gt 3 ] ; then
        echo "fsck failed. Mounting root device read-only."
        read_write=
    else
        if [ "$read_only" ]; then
            echo "fsck succeeded. Mounting root device read-only."
            read_write=
        else
            echo "fsck succeeded. Mounting root device read-write."
            read_write=1
        fi
    fi
fi

opt="-o ro"
[ -n "$read_write" ] && opt="-o rw"

# mount the actual root device on /root
echo "Mounting root $rootdev"
# check external journal
[ "$rootfstype" = "xfs" -a -n "$journaldev" ] && opt="${opt},logdev=$journaldev"
[ "$rootfstype" = "reiserfs" -a -n "$journaldev" ] && opt="${opt},jdev=$journaldev"
[ -n "$rootflags" ] && opt="${opt},$rootflags"
[ -n "$rootfstype" ] && opt="${opt} -t $rootfstype"
mount $opt $rootdev /root
if [ $? -ne 0 ] ; then
    echo "could not mount root filesystem -- exiting to /bin/sh"
    cd /
    PATH=$PATH PS1='$ ' /bin/sh -i
fi