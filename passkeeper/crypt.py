#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gnupg
import logging
from os.path import join as os_join
from passkeeper.tools import *

LOG = logging.getLogger(__name__)

def encrypt(source, output, passphrase):
    gpg = gnupg.GPG()
    with open(source, 'r') as f:
        encrypted = gpg.encrypt_file(
            f,
            recipients=None,
            symmetric='AES256',
            armor=True,
            passphrase=passphrase,
            output=output)
        return encrypted


def decrypt(source, output, passphrase):
    gpg = gnupg.GPG()
    with open(source, 'r') as f:
        decrypted = gpg.decrypt_file(f,
            passphrase=passphrase,
            always_trust=True,
            output=output)
        return decrypted
