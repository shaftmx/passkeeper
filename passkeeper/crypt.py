#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Gaël Lambert (gaelL) <gael.lambert@netwiki.fr>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gnupg
import logging
from os.path import join as os_join
from passkeeper.tools import *

LOG = logging.getLogger(__name__)

def encrypt(source, output, passphrase):
    gpg = gnupg.GPG()
    with open(source, 'rb') as f:
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
    with open(source, 'rb') as f:
        decrypted = gpg.decrypt_file(f,
            passphrase=passphrase,
            always_trust=True,
            output=output)
    return decrypted
