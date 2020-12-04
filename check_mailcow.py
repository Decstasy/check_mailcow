#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__      = "Dennis Ullrich"
__maintainer__  = "Dennis Ullrich"
__credits__     = ["Dennis Ullrich"]
__copyright__   = "Copyright 2020 by Dennis Ullrich"
__license__     = "GPL"
__version__     = "0.1"
__email__       = "github@decstasy.de"
__status__      = "Production"
__doc__         = 'Simple Icinga2 / Nagios plugin to check all running mailcow containers via API'

import argparse as ap
import nagiosplugin as np
import requests as rq
import logging

_log = logging.getLogger('nagiosplugin')

class MailcowContainers(np.Resource):
    def __init__(self, domain, key, ssl=True, verify=True):
        self.headers = {"Content-Type": "application/json", "X-API-Key": key}
        self.ssl = ("http","https")[ssl]
        self.url = self.ssl + "://" + domain + "/api/v1/get/status/containers"
        self.verify = verify
        self.containers = ""
        pass

    def get_containers(self):
        try:
            result = rq.get(self.url, headers=self.headers, verify=self.verify)
        except Exception as e:
            raise np.CheckError(
                'Failed to query API: {}'.format(e)
            )
        _log.debug('API Response: {}'.format(result.content))
        if result.status_code != 200:
            raise np.CheckError(
                'http status code was {}'.format(result.status_code)
            )
        return result

    def probe(self):
        containers = self.get_containers()
        # Sometimes the API returns something, which is not json serializable (╯°□°）╯︵ ┻━┻)
        try:
            self.containers = containers.json()
        except ValueError as e:
            raise np.CheckError(
                'API response is not json serializable! Error: {}, API Response: {}'.format(e,containers.content)
            )
        for container in self.containers:
            # Map "running" to 1 and everything else to 0
            yield np.Metric(container, (0,1)[self.containers[container]['state'] == "running"], min=1, context='MailcowContainers')

class MailcowContainerContext(np.Context):
    def evaluate(self, metric, resource):
        if metric.value == 0:
            return self.result_cls(np.Critical, metric=metric)
        if metric.value > 0:
            return self.result_cls(np.Ok, metric=metric)

    def describe(self, metric):
        if metric.value == 0:
            return metric.name + ' not running'
        return metric.name + 'runs properly'

    def performance(self, metric, resource):
        return np.Performance(metric.name, metric.value, '', 0, 0, metric.min, metric.max)

class MailcowSummary(np.Summary):
    def ok(self, results):
        return 'Everything is fine :)'

    def problem(self, results):
        return ', '.join(self.verbose(results))

@np.guarded
def main():
    argp = ap.ArgumentParser(description=__doc__)
    required = argp.add_argument_group('Required arguments')
    required.add_argument('-d', '--domain', action='store', required=True,
                        help='Mailcow server domain (e.g. mail.example.com)')
    required.add_argument('-k', '--apikey', action='store', required=True,
                        help='API secret key for your Mailcow instance')
    argp.add_argument('--insec', action='store_false', default=True,
                        help='Don\'t use SSL for API connection')
    argp.add_argument('--noverify', action='store_false', default=True,
                        help='Don\'t check server certificates for API connection')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                        help="-vvv is the limit, but feel free to use more")
    args = argp.parse_args()
    check = np.Check(
        MailcowContainers(args.domain, args.apikey, verify=args.noverify, ssl=args.insec),
        MailcowContainerContext('MailcowContainers'),
        MailcowSummary()
    )
    check.main(args.verbose)

if __name__ == '__main__':
    main()
