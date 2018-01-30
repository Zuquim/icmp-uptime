#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class Essentials:
    def __init__(self):
        try:
            with open('setup.conf', 'r') as syspath:
                output = syspath.read().strip()
                out = ''
            for line in output.strip().splitlines():
                if not line.strip().startswith("#"):
                    out += line.rstrip() + '\n'
            o = out.strip().splitlines()
            self.rrd_path = o[0].split(' := ')[1]
            self.host_list = o[1].split(' := ')[1].strip().split()
            self.daemon_username = o[2].split(' := ')[1].split('|')[0]
            self.daemon_groupname = o[2].split(' := ')[1].split('|')[1]
            if not self.rrd_path.endswith('/'):
                self.rrd_path = self.rrd_path + '/'
        except FileNotFoundError:
            print('\nError[1]: setup.conf file not found!\n')
            with open('setup.conf.sample', 'r') as syspath:
                print(syspath.read().strip())
            exit(1)
