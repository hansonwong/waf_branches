#!/bin/bash

mother_sn=W3TMM26V

mother_dev=sda
child_dev=sdb

/root/clone_disk/sh/mkcheck.sh $mother_dev $child_dev $mother_sn

