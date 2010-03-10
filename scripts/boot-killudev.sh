#!/bin/bash
#
#%stage: setup
#%provides: killprogs
#
#%dontshow
#
##### kill udev
##
## Kills udev. It will be started from the real root again.
##
## Command line parameters
## -----------------------
##

# kill udevd, we will run the one from the real root
/sbin/udevsettle
kill $(pidof udevd)

