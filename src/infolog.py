#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import atexit
import json
import os

from datetime import datetime
from threading import Thread
from urllib.request import Request, urlopen

_format = '%Y-%m-%d %H:%M:%S.%f'
_file = None
_run_name = None
_slack_url = None


def init(file_path, run_name, slack_url=None):
  global _file, _run_name, _slack_url
  if os.path.exists(file_path):
    os.remove(file_path)
  _close_logfile()
  _file = open(file_path, 'a')
  _file.write(
    '\n-----------------------------------------------------------------\n')
  _file.write('Starting new {} training run\n'.format(run_name))
  _file.write(
    '-----------------------------------------------------------------\n')
  _run_name = run_name
  _slack_url = slack_url
  _file.flush()


def log(msg, end='\n', slack=False, print_flag=True):
  if print_flag:
    print(msg, end=end)
  if _file is not None:
    _file.write('[%s]  %s\n' % (datetime.now().strftime(_format)[:-3], msg))
  if slack and _slack_url is not None:
    Thread(target=_send_slack, args=(msg,)).start()
  _file.flush()


def _close_logfile():
  global _file
  if _file is not None:
    _file.close()
    _file = None


def _send_slack(msg):
  req = Request(_slack_url)
  req.add_header('Content-Type', 'application/json')
  urlopen(req, json.dumps({
    'username': 'tacotron',
    'icon_emoji': ':taco:',
    'text': '*%s*: %s' % (_run_name, msg)
  }).encode())


atexit.register(_close_logfile)
