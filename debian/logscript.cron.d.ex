#
# Regular cron jobs for the logscript package
#
0 4	* * *	root	[ -x /usr/bin/logscript_maintenance ] && /usr/bin/logscript_maintenance
