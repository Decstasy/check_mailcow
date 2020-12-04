# check_mailcow
A documentation will follow soon.
It's a simple Icinga2 / Nagios plugin to check all running mailcow containers via API.

## Requirements
* python 3
* nagiosplugin (via pip)

## Usage
```
check_mailcow.py [-h] -d DOMAIN -k APIKEY [--insec] [--noverify] [-v]

Required arguments:
  -d DOMAIN, --domain DOMAIN
                        Mailcow server domain (e.g. mail.example.com)
  -k APIKEY, --apikey APIKEY
                        API secret key for your Mailcow instance

optional arguments:
  -h, --help            show this help message and exit
  --insec               Don't use SSL for API connection
  --noverify            Don't check server certificates for API connection
  -v, --verbose         -vvv is the limit, but feel free to use more
  ```
