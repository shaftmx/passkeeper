#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import subprocess
from shutil import copy2 as copy
from os.path import join

LOG = logging.getLogger(__name__)

def white(texte):
    return "\033[37m%s\033[0m" % texte

def grey(texte):
    return "\033[30m%s\033[0m" % texte
     
def grey_strong(texte):
    return "\033[1;30m%s\033[0m" % texte
     
def blue(texte):
    return "\033[34m%s\033[0m" % texte

def red(texte):
    return "\033[31m%s\033[0m" % texte

def green(texte):
    return "\033[32m%s\033[0m" % texte

def pink(texte):
    return "\033[35m%s\033[0m" % texte

def yellow(texte):
    return "\033[33m%s\033[0m" % texte

def cyan(texte):
    return "\033[36m%s\033[0m" % texte

def create_dir(path, dry_run=False):
    if dry_run:
        LOG.warning('Create directory : %s' % path)
    else:
        if not os.path.isdir(path):
            LOG.info('Create directory : %s' % path)
            os.makedirs(path)

def run_cmd(cmd, dry_run=False):
    if dry_run:
        LOG.warning('Exec command %s' % cmd)
    else:
        LOG.debug('Exec command %s' % cmd)
        output = subprocess.call(cmd, shell=True)
        if output != 0:
            LOG.critical('Command ERROR %s return code : %d' % (cmd, output))
            raise Exception('Unable to execute command')


