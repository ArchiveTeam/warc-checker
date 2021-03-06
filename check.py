#!/usr/bin/python

import warc
import requests
import string
import sys

available_api = 'http://archive.org/wayback/available'

def is_in_wb(url, ts):
    r = requests.get(available_api, params={'url': url, 'timestamp': ts})
    json = r.json()
    return json['archived_snapshots']['closest']['timestamp'] == ts

def get_info(record):
    return (record['WARC-Target-URI'], string.translate(record['WARC-Date'], None, '-:TZ'),)

def content_type(record):
    return True

filter_index = 0
def filter_rec(record):
    return True
    global filter_index
    filter_index += 1
    return ((filter_index % 4) == 0)

f = warc.open(sys.argv[1])
found = 0
total = 0
missing = []
busted = []
for record in f:
    if record['WARC-Type'] != 'response':
        # don't check for requests or anything else, just responses
        continue
    if not filter_rec(record):
        # statistical sampling i guess, to save time
        continue
    total += 1
    (url, ts,) = get_info(record)
    print url
    try:
        if is_in_wb(url, ts):
            found += 1
            print "YUP"
        else:
            missing.append(url)
    except:
        busted.append(url)
        continue

print found, total
print "missing:", missing
print "busted:", busted

if (total == found):
    print "ALL THERE"

# tolerate a 20% failure rate
if len(missing) == 0:
    if len(busted) < 0.2*total:
        sys.exit(0)

sys.exit(total - found)
