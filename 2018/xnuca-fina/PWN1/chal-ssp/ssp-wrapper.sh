#!/bin/sh
su ctf -c "ulimit -c 0 && ulimit -v 100000 && ulimit -t 45 && ulimit -m 200000 && ./ssp && exit"
exit 0
#su ctf -c "ulimit -a"
