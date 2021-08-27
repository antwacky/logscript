#!/usr/bin/env python3

import sh
import os
import re
import logging
import sys
import multiprocessing
import inspect
import json
import signal
import importlib
import glob
import pickle

class Rule:

     def __init__(self, rule):

         self.name = rule['name']
         self.glob = glob.glob(rule['glob'])
         self.occurences = rule['occurences']
         self.regex = re.compile(rule['regex'])
         self.script = rule['script']
         self.cache_key = rule['cache_key']

         return

class Cache:

    def __init__(self, cache_file, cache_dir='/etc/logscript/cache'):

        self.lock = multiprocessing.Lock()
        self.cache_dir = cache_dir
        self.cache_file = '{}/{}'.format(self.cache_dir, cache_file.replace(' ', ''))
        self.cache = []

        sh.mkdir('-p', self.cache_dir)

    def add(self, obj):

        with self.lock:

            self.cache.append(obj)

        return

    def load(self):

        try:
            self.cache = pickle.load(open(self.cache_file, 'rb'))

        except IOError:
            self.cache = []

        return

    def save(self):

        with self.lock:

            try:
                pickle.dump(self.cache, open(self.cache_file, 'wb'))

            except FileNotFoundError:
                log.warn('failed to save cache'.format(self.cache_file))

        return

class LogScript:

    def __init__(self, rule_directory='/etc/logscript/rules.d', script_directory='/etc/logscript/scripts.d'):

        self.procs = []
        self.tails = []

        self.rules = []
        self.scripts = {}

        self.rule_directory = rule_directory
        self.script_directory = script_directory

    def load_rules(self):

        rules = []
        for rule in os.listdir(self.rule_directory):

            try:
                rule = json.load(open('{0}/{1}'.format(self.rule_directory, rule)))

            except json.decoder.JSONDecodeError:
                log.exception('rule file {0} is invalid JSON'.format(rule))
                return

            rules.append(Rule(rule))

        self.rules = rules

        return

    def load_scripts(self):

        scripts = {}

        sys.path.insert(1, self.script_directory)

        for script in os.listdir(self.script_directory):
            script = script.split('.')[0]

            try:
                m = __import__(script)

            except SyntaxError:
                log.exception('script file {0}.py has syntax error'.format(script))
                return

            fs = inspect.getmembers(m, inspect.isfunction)

            for f in fs:
                scripts[f[0]] = f[1]

        self.scripts = scripts

        return

    def _worker(self, rule):

        signal.signal(signal.SIGINT, lambda *x: None)
        signal.signal(signal.SIGTERM, lambda *x: None)

        cache = Cache(rule.name)
        cache.load()
        occurences = 0

        try:
            tail = sh.tail('-n0', '-f', '-q', rule.glob, _iter=True, _bg=True, _bg_exc=False)
            self.tails.append(tail)

            for line in tail:

                match = rule.regex.match(line.strip())
                if match:

                    occurences += 1

                    if occurences != rule.occurences:
                        continue

                    log.info('rule "{0}" triggered'.format(rule.name))

                    if rule.cache_key:

                        variables = re.findall('(?P<var>\$\w+)', rule.cache_key)

                        key = rule.cache_key

                        for variable in variables:

                            try:
                                key = key.replace(variable, match.group(variable[1:]))

                            except IndexError:
                                log.warn('rule "{0}" invalid cache key {1}'.format(rule.name, key))
                                key = False
                                break

                        if key:

                            if key in cache.cache:

                                log.info('rule "{0}" ignored (found in cache)'.format(rule.name))
                                occurences -= 1
                                continue

                            else:
                                cache.add(key)

                    try:
                        result = self.scripts[rule.script](rule, line, match)
                        log.info('rule "{0}" responded with "{1}"'.format(rule.name, result))

                    except KeyError:
                        log.fatal('rule "{0}" triggered, but script does not exist'.format(rule.name))

                    except Exception as e:
                        log.exception('rule "{0}" triggered, but script failed with error'.format(rule.name))

                    finally:
                        occurences = 0

        except sh.SignalException_SIGTERM:
            cache.save()
            pass

        return

    def start(self):

        log.info('** starting logscript **')

        if len(self.rules) == 0:
            print('no rules defined in {0}'.format(self.rule_directory))
            sys.exit(1)

        for rule in self.rules:
            p = multiprocessing.Process(target=self._worker, daemon=True, args=(rule,))
            self.procs.append(p)
            p.start()

        for p in self.procs:
            p.join()

        return

    def stop(self, *args):

        log.info('** stopping gracefully **')

        for t in self.tails:
            t.terminate()

        return

if __name__ == '__main__':

    logging.getLogger("sh").setLevel(logging.WARNING)
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)

    handler = logging.FileHandler('/var/log/logscript.log')
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    ls = LogScript()

    signal.signal(signal.SIGTERM, ls.stop)

    try:
        ls.load_rules()
        ls.load_scripts()
        ls.start()
    except:
        log.exception('failed to start')
        sys.exit(1)
