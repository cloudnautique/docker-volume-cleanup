# Deprecated, Docker 1.7 changed the volume structure. Checkout [rancher/sherdock](https://github.com/rancher/sherdock) if you want to clean out orphaned volumes.

## Clean up Orphaned Docker Volumes

### Overview

This was created to clean up volumes on a Drone CI host that were left behind after builds. The script is
modified from the gist [eliasp/7720943](https://gist.github.com/eliasp/7720943)

### Container Usage

This app can be run as a docker container. 

```
docker build --rm -t volume-cleanup .
docker run -d -v /var/lib/docker:/var/lib/docker -v /var/run/docker.sock:/var/run/docker.sock
```

The container runs `cron -L 15 && tail -F /var/log/docker_volume_cleanup.py` and runs every 5 minutes.

To adjust, just change the interval modify the crontabs/root file with the desired intervals.


### Command Usage


Dry Run
```
docker_volume_cleanup.py --noop
```

Clean up

```
docker_volume_cleanup.py
```

Adjust log level

```
docker_volume_cleanup.py --loglevel [ 'DEBUG', 'INFO'(default), 'WARN', 'ERROR', 'CRIT' ]
```

