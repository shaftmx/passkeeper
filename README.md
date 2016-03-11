Pass keeper
============

[![Build Status](https://travis-ci.org/shaftmx/passkeeper.svg?branch=master)](https://travis-ci.org/shaftmx/passkeeper)

This is a very simple password keeper based on `ini` file and symmetric `gpg` encryption.

**Features :**

  * Local git versionning
  * Store all information you want in `.ini` file format
  * Search pattern in all `.ini` file and print matching section
  * Encrypt or decrypt ini file with gpg and symmetric passphrase
  * Delete ini file after encryption with shred
  * Encrypt/Delete file in a `.raw` directory

Overview
==========

![Archi](https://raw.githubusercontent.com/shaftmx/passkeeper/master/docs/archi.png)

  * 1. Passkeeper take care of `.ini` files and files in `.raw` directories
  * 2. Passkeeper ask you a password to encrypt your files. 
  * 3. All files are encrypted with standard `openpgp`.
  * 4. Encrypted files are put in the `encrypted` directory.
  * 5. And then Encrypted files are archived in a local git with a `git commit`

Quick usage
===========

**Init a new passkeeper directory :**

```
passkeeper-cli --directory /opt/mypasskeeper --init
```

This will generate a default encrypted file : `encrypted/default.ini.passkeeper`, a raw directory named `default.raw`. 
and init local `git` repository in `/opt/mypasskeeper`.

Basic usage :

  * `.ini` file : in the root directory push all your information in ini file format. Login, password, urls, ... all `.ini` file are parsed when you run passkeeper with `--search`.
  * `.raw` dir : in each `.raw` directory, you can add file like ssh key, ssl cert, ... All files in this directory will be encrypted.

**Lets decrypt our ini files :**

```
passkeeper-cli --directory /opt/mypasskeeper --decrypt
```

Now you can find all encrypted ini file in `/opt/mypasskeeper` directory in our case `default.ini`. 

**Add new files :**

```
# Add simple ini file
touch /opt/mypasskeeper/server.ini
# Add my ssh key
mkdir /opt/mypasskeeper/ssh.raw
touch /opt/mypasskeeper/ssh.raw/id_rsa
```

Simply add new ini file in your passkeeper directory. I recomment you to create a ini file for each item category and one section by item.

**Search pattern in all ini file :**

```
passkeeper-cli --directory /opt/mypasskeeper --search foo
[foo]
name = foo access
type = web
url = http://foo.com
password = bar
login = foo
comments = foo is good website
```

`Search` print with color all section where your pattern match. Matching is done on section name and all value in this section.

**Encrypt / close your ini file :**
```
passkeeper-cli --directory /opt/mypasskeeper --encrypt
```

All ini file are encrypted with standard `gnupg symmetric` mode. All ini file are `shred` and a commit make local `git commit`.

You also can use `clean` function if you just open (decrypt) files and doesn't do modification. Just want to close passkeeper (delete all decrypted files).

```
  passkeeper-cli --directory /opt/mypasskeeper --clean
```

It's better to use `clean` than manually `rm` files because it will apply `shred` on each files.


Setup
======

```
pip install git+git://github.com/shaftmx/passkeeper \
-r https://raw.githubusercontent.com/shaftmx/passkeeper/master/requirements.txt
```
