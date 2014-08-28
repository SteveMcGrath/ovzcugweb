#!/bin/bash
###############################################################################
#                             Physical2OpenVZ                                 #
###############################################################################
# Version 0.1
# Written By: Steven McGrath
# 
# Version History
# ---------------
# * 0.1 - Initial Version

## Default Params
vz_base="/vz"
username="root"
exclude_file="/tmp/p2vps-excludes"
set -f
excludes='.bash_history /boot /dev/* /mnt/* /tmp/* /proc/* /sys/* /usr/src/* /etc/sysconfig/network-scripts/ifcfg-eth*'
set +f

function usage() {
    echo "Usage Info Goes here!"
}


function arg_parse() {
    local param value
    while [ "$1" != "" ];do
        param=$(echo $1 | awk -F= '{print $1}')
        value=$(echo $1 | awk -F= '{print $2}')
        case $param in 
            -h | --help) 
                usage
                exit
                ;;
            -b | --base) 
                vz_base=$value
                ;;
            -e | --exclude-file)
                exclude_file=$value
                ;;
            *) 
                echo "ERROR: Unknown Parameter \"$param\""
                usage
                exit 1
                ;;
        esac
        shift
    done
}


function migrate() {
    local ctid host ctdata
    ctid=$1
    host=$2
    ctdata=$vz_base/migration/$ctid
    if [ ! -f $exclude_file ];then
    #   echo '[!] No Exclude file exists!  Please specify one'
        echo "[W] Could not find $exclude_file, so I'm creating a default one..."
        set -f
        for item in $excludes;do
            echo "$item" >> $exclude_file
        done
        set +f
    fi
    echo '[*] Mounting Ploop Sparse Image...'
    mkdir -p $ctdata
    mount -t ploop $vz_base/private/$ctid/root.hdd/DiskDescriptor.xml $ctdata

    echo '[*] Rsyncing Data from Physical box...'
    rsync -arpz --numeric-ids --exclude-from "$exclude_file" root@$host:/ $ctdata/

    echo '[*] Performing some cleanup...'
    sed -i -e '/getty/d' $vz_base/migration/$ctid/etc/inittab       # Remove Gettys from inittab
    ln -sf /proc/mounts $ctdata/etc/mtab                            # Link mtab to /proc/mounts
    cp $ctdata/etc/fstab $ctdata/etc/fstab.physical-old             # Remove the old fstab
    grep devpts $ctdata/etc/fstab.physical-old > $ctdata/etc/fstab  # Copy over devpts Entries from old fstab

    echo '[*] Unmounting sparse image...'
    umount $ctdata
    rm -rf $ctdata

    echo '[*] Complete!'
}

arg_parse
echo -n "CTID of the existing container that we will be syncing into: ";read CTID
echo -n "Physical host address : ";read ADDRESS 
echo -e "\n"
migrate $CTID $ADDRESS

echo -en "\nStart $CTID right now? (Y/n): ";read ok
if [ "$ok" == "n" -o "$ok" == "N" ];then
    exit 1
else
    vzctl start $CTID
    echo '[*] Started Container... Please disable un-needed services.'
    echo '    For some examples, visit:'
    echo '      https://openvz.org/Physical_to_container#.2Fetc.2Finit.d_services'
fi