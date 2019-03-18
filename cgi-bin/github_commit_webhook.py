#!/web/pyfindmespot/pyfindmespot_env/bin/python
# -*- coding: utf-8 -*-

import cgi
import os
import sys
import json
import hmac
from hashlib import sha1
from subprocess import Popen, PIPE

import cgitb
cgitb.enable()


# some ideas
# https://github.com/carlos-jenkins/python-github-webhooks/blob/master/webhooks.py


# Implement ping
event = os.environ.get('HTTP_X_GITHUB_EVENT', 'ping')
if event == 'ping':
    print('Content-Type: application/json\n\n')
    print(json.dumps({'msg': 'pong'}))
    exit()


raw_payload = ''
payload = {}
try:
    raw_payload = sys.stdin.read()
    payload = json.loads(raw_payload)
except:
    pass

header_signature = os.environ.get('HTTP_X_HUB_SIGNATURE', '')
sha_name, signature, *_ = header_signature.split('=') + ['']

secret = "???"
mac = hmac.new(secret.encode('utf-8'), msg=raw_payload.encode('utf-8'), digestmod='sha1')
hexdigest = str(mac.hexdigest())

if not hmac.compare_digest(mac.hexdigest(), signature):
    print('Content-Type: application/json\n\n')
    print(json.dumps({'msg': 'pong'}))
    exit()

branch = (payload.get('ref', '') + '///').split('/', 3)[2]
name = payload['repository']['name'] if 'repository' in payload else None
if (event, branch, name) != ('push', 'master', 'pyfindmespot'):
    print('Content-Type: application/json\n\n')
    print(json.dumps({'msg': 'pong'}))
    exit()

cur_dir_path = os.path.dirname(os.path.realpath(__file__))
proc = Popen(os.path.join(cur_dir_path, 'pull_and_restart.sh'), stdout=PIPE, stderr=PIPE)
stdout, stderr = proc.communicate()
ran = {
    'returncode': proc.returncode,
    'stdout': stdout.decode('utf-8'),
    'stderr': stderr.decode('utf-8'),
}
print('Content-Type: application/json\n\n')
print(json.dumps(ran))
