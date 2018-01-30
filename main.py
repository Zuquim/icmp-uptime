#!/usr/bin/env python3
# -*- coding: utf-8 -*

import Configurer
import subprocess
import os
import rrdtool
from daemon import runner
import time
import grp
import pwd

conf = Configurer.Essentials()
rrd_path = conf.rrd_path
host_list = conf.host_list
d_user = conf.daemon_username
d_group = conf.daemon_groupname


def ping(host):
    output = subprocess.Popen(
        ["ping", "-c", "5", "-W", "1", host],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    out, error = output.communicate()
    return out


def status(result):
    state = None
    for line in result.decode().strip().splitlines():
        if 'packets transmitted' in line:
            if '100.0%' == line.strip().split()[6]:
                print(str(time.time()) + '\tLost conn')
                state = False
            else:
                print(str(time.time()) + '\tOK')
                state = True
    if state is None:
        print('Error[2]: Inconsistent ping output.')
        exit(2)
    else:
        return state


def update(file_path, host):
    # now = int(time.time())
    # According to docs, it is possible to use 'N' in place of now (time.time())
    if status(ping(host)) is True:
        # rrdtool.update(file_path, str(now) + ':1')
        rrdtool.update(file_path, 'N:1')
    else:
        # rrdtool.update(file_path, str(now) + ':0')
        rrdtool.update(file_path, 'N:0')


class Daemon(object):
    def __init__(self):
        """Initialize Daemon."""
        self.stdin_path = '/dev/null'
        self.stdout_path = '/tmp/rrdpinger_stdout.log'
        self.stderr_path = '/tmp/rrdpinger_stderr.log'
        self.pidfile_path = '/tmp/rrdpinger_daemon.pid'
        self.pidfile_timeout = 8

    @staticmethod
    def run():
        for host in host_list:
            full_path = rrd_path + host + '/icmp_uptime.rrd'
            if os.path.exists(full_path) is False:
                print('RRD not found. Making one: ' + full_path)
                rrdtool.create(full_path,
                               'DS:status:GAUGE:600:U:U',
                               'RRA:AVERAGE:0.5:1:600',
                               'RRA:AVERAGE:0.5:6:700',
                               'RRA:AVERAGE:0.5:24:775',
                               'RRA:AVERAGE:0.5:288:797')
        while 1:
            for host in host_list:
                full_path = rrd_path + host + '/icmp_uptime.rrd'
                update(full_path, host)
            time.sleep(60)  # Change to 300 for production env


if __name__ == '__main__':
    app = Daemon()
    daemon_runner = runner.DaemonRunner(app)
    daemon_gid = grp.getgrnam(d_group).gr_gid
    daemon_uid = pwd.getpwnam(d_user).pw_uid
    daemon_runner.daemon_context.gid = daemon_gid
    daemon_runner.daemon_context.uid = daemon_uid
    daemon_runner.do_action()
