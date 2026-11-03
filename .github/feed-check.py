#!/usr/bin/env python3
"""Checks the day's world file before it goes out as the app's feed.

Usage: feed-check.py NEW.json PUBLISHED.json
Exits with 1 when the new file is not a world snapshot the app can read, or is older than the published one.
"""
import datetime
import json
import re
import sys


def fail(msg):
    print('FEED CHECK FAILED: ' + msg)
    sys.exit(1)


new_path, pub_path = sys.argv[1], sys.argv[2]
raw = open(new_path, 'rb').read()
if len(raw) > 150_000:
    fail('the file is %d bytes; the limit is 150000' % len(raw))
try:
    w = json.loads(raw.decode('utf-8'))
except ValueError as e:
    fail('not valid UTF-8 JSON: %s' % e)
if not isinstance(w, dict):
    fail('the top level is not an object')
if w.get('lang') != 'en':
    fail('lang is not "en" (a snapshot wrapped in "data" fails here too)')
as_of = str(w.get('asOf', ''))
if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', as_of):
    fail('asOf is not YYYY-MM-DD')
today = datetime.datetime.now(datetime.timezone.utc).date()
if datetime.date.fromisoformat(as_of) > today + datetime.timedelta(days=1):
    fail('asOf %s is in the future' % as_of)
if not isinstance(w.get('label'), str) or not w['label']:
    fail('label is missing')
idx = w.get('idx')
if not isinstance(idx, dict):
    fail('idx is missing')
for k in ('frNEU', 'brent', 'eurusd', 'cell', 'air', 'suezShare'):
    v = idx.get(k)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
        fail('idx.%s is not a positive number' % k)
if not isinstance(w.get('risk'), dict):
    fail('risk is missing')
if not isinstance(w.get('briefing'), list) or not w['briefing']:
    fail('the briefing is empty')
if not isinstance(w.get('events'), list):
    fail('events are missing')
try:
    pub = json.load(open(pub_path, encoding='utf-8'))
except (OSError, ValueError):
    pub = {}
if str(pub.get('asOf', '')) > as_of:
    fail('asOf %s is older than the published %s' % (as_of, pub['asOf']))
print('FEED CHECK PASS: %s, %d bytes, %d briefing items, %d events' % (w['label'], len(raw), len(w['briefing']), len(w['events'])))
