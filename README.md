# Log Script

Logscript is a Python daemon that parses logs and fires events based on rules.

## Rules

Rules are stored in /etc/logscript/rules.d

They are json formatted as follows:

```
{
  "name": "test",
  "glob": "/var/log/test.log",
  "regex": "^\\d$",
  "occurences": 1,
  "script": "helloworld"
}
```

**name**: A name for the rule, recorded in logs when triggered
**glob**: Glob match for log files the rule applies to
**regex**: Regex pattern to look for, standard JSON special characters
**occurences**: Number of times the rule must match before triggering
**script**: The script to run when the rule triggers

## Scripts

Scripts are stored in /etc/logscript/scripts.d

They are Python scripts and are executed as such.

The filename is not relevant (although must be a .py Python file).

The 'script' referred to in a rule references the function name within the script file, and not the script filename itself.

For the example rule given earlier, a function named helloworld must be defined in any script file as below:

```
def helloworld(rule, line):

    print('hello world')
```

Scripts are passed two variables:

**rule**: The full rule object
**line**: The log line that triggered the rule

These can then be used as required within the script (for example, adding the log line to an incident ticket).

## Installation

Install dependencies

```
sudo apt install python3-sh
```

Then...

On Debian, just install the deb package:

```
sudo dpkg -i python3-logscript_0.0.1-1_all.deb
```

This will create a systemd service which can be used as follows:

```
systemctl start python3-logscript
systemctl stop python3-logscript
systemctl restart python3-logscript
```

On other systems, you'll need to put the source somewhere, create the following directories:

```
/etc/logscript/rules.d
/etc/logscript/scripts.d
```

Then run as follows:

```
python logscript
```

## Distribution

The program was packaged into a debian package as shown below:

```
python setup.py sdist
dh_make -p logscript_0.0.1 -f dist/logscript-0.0.1.tar.gz -e pagey101@hotmail.co.uk
vi debian/changelog
vi debian/control
echo 'dist/logscript-0.0.1.tar.gz' > debian/source/include-binaries
dpkg-buildpackage
```

To make modifications:

Extract the distribution archive

```
tar -xvzf dist/logscript-0.0.1.tar.gz
```

Make the necessary changes.

Generate the build configuration

```
dh_make -p logscript_0.0.2 -f dist/logscript-0.0.1.tar.gz -e <your_email>
```

Update Debian files:

1. Edit debian/control and add details of changes
2. Edit debian/changelog and update 'unknown' with your GPG key identity

Rebuild the package

```
dpkg-buildpackage -b
```

This will generate a new debian package which can be installed.
