#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from os.path import join as join_os
import logging
from passkeeper.tools import *
from passkeeper.git import *
from passkeeper.crypt import *
from getpass import getpass
import ConfigParser

LOG = logging.getLogger(__name__)


class Passkeeper(object):

    def __init__(self, directory):
        self.directory = directory
        self.git = Git(self.directory)
        self.encrypted_dir = 'encrypted'

    def init_dir(self):
        LOG.info('Init directory %s' % self.directory)
        create_dir(self.directory)

        self.git.init()
        self.git.add_gitignore(['*.ini'])

        # Write default template file
        sample_file = ("""[foo]
name = foo access
type = web
url = http://foo.com
password = bar
login = foo
comments = foo is good website
""")

        LOG.debug('Write sample file default.ini')
        with open(join_os(self.directory, 'default.ini'), 'w') as f:
            f.write(sample_file)

        self.encrypt()
        self.cleanup_ini()

    def encrypt(self, commit_message='Update encrypted files'):
        passphrase = getpass()
        passphrase_confirm = getpass('Confirm: ')
        if passphrase != passphrase_confirm:
            LOG.critical('Password and confirm are different')
            return False

        create_dir(join_os(self.directory, self.encrypted_dir))

        LOG.info('Encrypt files :')
        for fname in os.listdir(self.directory):
            file_path = os_join(self.directory, fname)
            if (fname.endswith('.ini')
            and os.path.isfile(file_path)):
                LOG.info('Encrypt file %s' % fname)
                git_relative_file_path = join_os(self.encrypted_dir,
                                                 '%s.passkeeper' % fname)
                encrypted_file_path = join_os(self.directory,
                                              git_relative_file_path)
                encrypted = encrypt(source=file_path,
                        output=encrypted_file_path,
                        passphrase=passphrase)
                LOG.info(encrypted.status)
                self.git.add([git_relative_file_path])
        self.git.commit('%s' % commit_message)
        return True

    def cleanup_ini(self):
        "Shred all ini files"
        for fname in os.listdir(self.directory):
            file_path = os_join(self.directory, fname)
            if (fname.endswith('.ini')
            and os.path.isfile(file_path)):
                LOG.info('Clean file %s' % fname)
                run_cmd('shred --remove %s' % file_path)

    def flush_history(self):
        """
        Flush the git history

        Destroy .git directory by shred all files and init git again.
        This allow to clear git history and to insure more security

        :Example:

        >>> flush_history()
        Clean file master
        Clean file HEAD
        Clean file exclude
        ...
        Dépôt Git vide initialisé dans /opt/mypasskeeper/.git/
        master (commit racine) 9e4a2a0] Clean git History

        .. seealso:: shred_dir(), git.init(), git.add(), git.commit()
        """
        shred_dir(os_join(self.directory, '.git'))
        self.git.init()
        self.git.add([self.encrypted_dir, '.gitignore'])
        self.git.commit('Clean git History')

    def decrypt(self):
        passphrase = getpass()

        LOG.info('Decrypt files :')
        source_dir = os_join(self.directory, self.encrypted_dir)
        for fname in os.listdir(source_dir):
            file_path = os_join(source_dir, fname)
            if (fname.endswith('.passkeeper')
            and os.path.isfile(file_path)):
                LOG.info('Decrypt file %s' % fname)
                decrypted_file_path = join_os(self.directory,
                                              fname.rstrip('.passkeeper'))
                decrypted = decrypt(source=file_path,
                        output=decrypted_file_path,
                        passphrase=passphrase)
                LOG.info(decrypted.status)

    def search(self, pattern):
        LOG.info('Search in files :')
        pattern = pattern.lower()
        config = ConfigParser.RawConfigParser()

        # Load files
        for fname in os.listdir(self.directory):
            file_path = os_join(self.directory, fname)
            if (fname.endswith('.ini')
            and os.path.isfile(file_path)):
                LOG.info('Loading file %s' % fname)
                config.read(file_path)
        # Search
        re_prep = re.compile(pattern)
        matching_sections = []
        for section in config.sections():

            # Section name match ?
            match = re_prep.search(section.lower())
            if match is not None:
                matching_sections.append(section)
                continue

            for option, value in config.items(section):
                # Value match ?
                match = re_prep.search(value.lower())
                if match is not None:
                    matching_sections.append(section)
                    break

        return config, matching_sections

    def print_sections(self, config, matching_sections, pattern):
        # Color matching pattern
        sed = re.compile('(.*)(%s)(.*)' % re.escape(pattern), re.IGNORECASE)
        for section in matching_sections:
            print '[%s]' % pink(sed.sub('%s%s%s' % (pink('\g<1>'),
                                                    red('\g<2>'),
                                                    pink('\g<3>')),
                                section))
            for option, value in config.items(section):
                print '%s = %s' % (green(option),
                                   white(sed.sub('%s%s%s' % (white('\g<1>'),
                                                             red('\g<2>'),
                                                             white('\g<3>')),
                                         value)))
            print ''
