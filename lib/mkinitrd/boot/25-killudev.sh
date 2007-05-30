#!/bin/bash
#%requires: vendor
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
kill $(pidof udevd)

