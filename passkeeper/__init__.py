#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from os.path import join as join_os
from os.path import dirname
from os.path import relpath as relative_path
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
        self.git.add_gitignore(['*.ini', '/*.raw'])

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

	# Write default raw
        create_dir(join_os(self.directory, 'default.raw'))
        sample_raw = ("""-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCA
-----END RSA PRIVATE KEY-----""")
        LOG.debug('Write sample file default raw')
        with open(join_os(self.directory, 'default.raw', 'ssh_id.rsa'), 'w') as f:
            f.write(sample_raw)

        self.encrypt()
        self.cleanup_ini()


    def encrypt(self, commit_message='Update encrypted files'):
        LOG.info('Encryption')
        passphrase = getpass()
        passphrase_confirm = getpass('Confirm: ')
        if passphrase != passphrase_confirm:
            LOG.critical('Password and confirm are different')
            return False

        create_dir(join_os(self.directory, self.encrypted_dir))

        LOG.info('Encrypt files :')
        # Encrypt files
        for fname in os.listdir(self.directory):
            file_path = os_join(self.directory, fname)
            # Handle ini file
            if (fname.endswith('.ini')
            and os.path.isfile(file_path)):
                LOG.info('Encrypt file %s' % fname)
                git_relative_encrypted_file_path = join_os(self.encrypted_dir,
                                                 '%s.passkeeper' % fname)
                encrypted_file_path = join_os(self.directory,
                                              git_relative_encrypted_file_path)
                encrypted = encrypt(source=file_path,
                        output=encrypted_file_path,
                        passphrase=passphrase)
                LOG.info(encrypted.status)
                self.git.add([git_relative_encrypted_file_path])
            # Handle .raw directory
            if (fname.endswith('.raw')
            and os.path.isdir(file_path)):
                for root, dirs, files in os.walk(file_path, topdown=False):
                    for name in files:
                        # /git/foo.raw/file
                        root_raw_file_path = os.path.join(root, name)
                        # foo.raw/file
                        git_relative_file_path = relative_path(root_raw_file_path, self.directory).lstrip('/')
                        LOG.info('Encrypt file %s' % git_relative_file_path)

                        # encrypt/foo.raw/file.passkeeper
                        git_encrypted_relative_file_path = join_os(self.encrypted_dir,
                                                         '%s.passkeeper' % git_relative_file_path)
                        # /git/encrypt/foo.raw/file.passkeeper
                        root_encrypted_file_path = join_os(self.directory,
                                                      git_encrypted_relative_file_path)

                        # /git/encrypt/foo.raw
                        root_encrypted_dirname_path = dirname(root_encrypted_file_path)

                        create_dir(root_encrypted_dirname_path)
                        encrypted = encrypt(source=root_raw_file_path,
                                output=root_encrypted_file_path,
                                passphrase=passphrase)
                        LOG.info(encrypted.status)
                        self.git.add([git_encrypted_relative_file_path])

        self.git.commit('%s' % commit_message)
        return True


    def decrypt(self):
        passphrase = getpass()

        LOG.info('Decrypt files :')
        source_dir = os_join(self.directory, self.encrypted_dir)

        for root, dirs, files in os.walk(source_dir, topdown=False):
            for name in files:
                file_path = join_os(root, name)
                relative_file_path = relative_path(file_path, source_dir).lstrip('/')

                if (name.endswith('.passkeeper')
                and os.path.isfile(file_path)):
                    LOG.info('Decrypt file %s' % relative_file_path)
                    decrypted_file_path = join_os(self.directory,
                                                  re.sub('.passkeeper$', '', relative_file_path))
                    create_dir(path=dirname(decrypted_file_path))
                    decrypted = decrypt(source=file_path,
                            output=decrypted_file_path,
                            passphrase=passphrase)
                    LOG.info(decrypted.status)


    def _remove_old_encrypted_files(self):
        "remove old passkeeper files"
        root_dir = os_join(self.directory, self.encrypted_dir)
        for root, dirs, files in os.walk(root_dir, topdown=False):
            for efname in files:
                # /git/encrypt/foo/bar.passkeeper
                root_file_path = os_join(root, efname)
                # encrypt/foo/bar.passkeeper
                git_relative_encrypted_file_path = relative_path(path=root_file_path, start=self.directory)
                LOG.debug('Check %s.' % git_relative_encrypted_file_path)

                # /git/foo/bar
                orig_file_path = os_join(self.directory, re.sub('.passkeeper$', '',
                                                                relative_path(path=root_file_path, start=root_dir)))
                if not os.path.isfile(orig_file_path):
                    req = raw_input("File %s will be deleted because origin file hasn't been found, are you sure (y/n)\n" % git_relative_encrypted_file_path)
                    if req == "y":
                        LOG.info('File %s will be deleted because origin file hasn t been found.' % git_relative_encrypted_file_path)
                        # shred file and then git remove because git remove automaticaly empty dirs
                        run_cmd('shred %s' % root_file_path)
                        self.git.force_remove([git_relative_encrypted_file_path])
                        self.git.commit('Remove file %s' % git_relative_encrypted_file_path)
                    else:
                        LOG.info('File %s has been concerved.' % git_relative_encrypted_file_path)



    def cleanup_ini(self):
        "Shred all ini files and remove old passkeeper files"

        # Remove old passkeeper files
        self._remove_old_encrypted_files()
        # Remove ini files
        for fname in os.listdir(self.directory):
            file_path = os_join(self.directory, fname)
            if (fname.endswith('.ini')
            and os.path.isfile(file_path)):
                LOG.info('Clean file %s' % fname)
                run_cmd('shred --remove %s' % file_path)
            elif (fname.endswith('.raw')
            and os.path.isdir(file_path)):
                LOG.info('Clean directory %s' % fname)
                shred_dir(file_path)



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
