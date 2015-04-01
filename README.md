Pass keeper
============

[![Build Status](https://travis-ci.org/shaftmx/passkeeper.svg)](https://travis-ci.org/shaftmx/passkeeper)

This is a very simple password keeper based on `ini` file and symmetric `gpg` encryption.

**Features :**

  * Local git versionning
  * Store all information you want in ini file format
  * Search pattern in all ini file and print matching section
  * Encrypt or decrypt ini file with gpg and symmetric passphrase
  * Delete ini file after encryption with shred

Quick usage
===========

**Init a new passkeeper directory :**

```
passkeeper-cli --directory /opt/mypasskeeper --init
```

This will generate a default encrypted file : `encrypted/default.ini.passkeeper` and init local `git` repository in `/opt/mypasskeeper`.


**Lets decrypt our ini files :**

```
passkeeper-cli --directory /opt/mypasskeeper --decrypt
```

Now you can find all encrypted ini file in `/opt/mypasskeeper` directory in our case `default.ini`. 

**Add new ini file :**

```
touch /opt/mypasskeeper/server.ini
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


Setup
======

```
pip install git+git://github.com/shaftmx/passkeeper \
-r https://raw.githubusercontent.com/shaftmx/passkeeper/master/requirements.txt
```
