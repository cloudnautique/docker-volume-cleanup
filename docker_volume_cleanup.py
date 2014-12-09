#!/usr/bin/python

import json
import os
import shutil
import subprocess
import re
import argparse

def get_volumes(vol_dir):
    return os.walk(os.path.join(vol_dir, '.')).next()[1]


def get_attached_container_volumes():
    containers_info = json.loads(subprocess.check_output('docker ps -a -q --no-trunc | xargs docker inspect', shell=True))
    volumes = [ v for container in containers_info for v in container['Volumes'].values() ]
    return volumes


def delete_volumes(no_op=False):
    dockerdir = '/var/lib/docker'
    volumesdir = os.path.join(dockerdir, 'volumes')

    all_volumes = get_volumes(volumesdir)
    container_volumes = get_attached_container_volumes()

    for volume in all_volumes:
        if not re.match('[0-9a-f]{64}', volume):
            print volume + ' is not a valid volume identifier, skipping...'
            continue

        volume_metadata = json.load(open(os.path.join(volumesdir, volume, 'config.json')))

        if volume_metadata['Path'] in container_volumes:
            print 'Volume still attached to container. Not clearing up volume ' + volume
            continue

        if not no_op:
            print 'Deleting volume ' + volume 
            rm_volume_data(volume_metadata['Path'])
            rm_volume_meta(os.path.join(volumesdir, volume))

        else:
            print '[NO-OP] Deleting volume ' + volume 


def rm_volume_data(volume_data_path):
    print 'Removing Volume Data: ' + volume_data_path
    shutil.rmtree(volume_data_path)

def rm_volume_meta(volume_meta_path):
    print 'Removing Volume Metadata: ' + volume_meta_path
    shutil.rmtree(volume_meta_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--noop", help="do a dry run", action="store_true")
    args = parser.parse_args()

    if args.noop:
        delete_volumes(no_op=True)
    else:
        delete_volumes()
