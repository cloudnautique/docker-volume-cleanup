#!/usr/bin/python

import json
import os
import shutil
import subprocess
import re
import argparse
import logging
import sys

FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger("docker_volume_cleanup")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def get_volumes(vol_dir):
    if os.path.isdir(vol_dir):
        volumes = os.walk(os.path.join(vol_dir, '.')).next()[1]
    else:
        logger.error("Volume Directory: {0} does not exist".format(vol_dir))
        volumes = []

    logger.debug("Volumes: {0}".format(', '.join(volumes)))

    return volumes


def get_attached_container_volumes():
    containers_info = json.loads(
        subprocess.check_output('docker ps -a -q --no-trunc | xargs docker inspect', shell=True))
    volumes = [v for container in containers_info for v in container.get('Volumes', {}).values()]

    logger.debug("Volumes: {0}".format(', '.join(volumes)))

    return volumes


def delete_volumes(no_op=False):
    dockerdir = '/var/lib/docker'
    volumesdir = os.path.join(dockerdir, 'volumes')

    all_volumes = get_volumes(volumesdir)
    container_volumes = get_attached_container_volumes()

    for volume in all_volumes:
        if not re.match('[0-9a-f]{64}', volume):
            logger.info('{0} is not a valid volume identifier, skipping...'.format(volume))
            continue

        volume_metadata = json.load(open(os.path.join(volumesdir, volume, 'config.json')))

        if volume_metadata['Path'] in container_volumes:
            logger.info('Volume still attached to container. Not clearing up volume {0}'.format(volume))
            continue

        if not no_op:
            logger.info('Deleting volume {0}'.format(volume))

            # skip bind mounts...
            if not volume_metadata['IsBindMount']:
                rm_volume_data(volume_metadata['Path'])

            rm_volume_meta(os.path.join(volumesdir, volume))

        else:
            logger.info('[NO-OP] Deleting volume {0}'.format(volume))


def rm_volume_data(volume_data_path):
    logger.info('Removing Volume Data: {0}'.format(volume_data_path))
    try:
        subprocess.check_call(["rm", "-rf", volume_data_path])
    except:
        logger.error("error while processing {0}".format(volume_data_path))


def rm_volume_meta(volume_meta_path):
    logger.info('Removing Volume Metadata: {0}'.format(volume_meta_path))
    shutil.rmtree(volume_meta_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--noop", help="do a dry run", action="store_true")
    parser.add_argument("--loglevel", help="DEBUG, INFO[default], WARN, ERROR, CRIT")
    args = parser.parse_args()

    if args.loglevel:
        allowed = ["DEBUG", "INFO", "WARN", "ERROR", "CRIT"]
        if args.loglevel in allowed:
            logger.setLevel(args.loglevel)
        else:
            print("Invalid log setting {0} not in {1}".format(args.loglevel, ', '.join(allowed)))
            sys.exit(1)
    else:
        logger.setLevel("INFO")

    if args.noop:
        delete_volumes(no_op=True)
    else:
        delete_volumes()
