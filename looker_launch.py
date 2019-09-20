#!/usr/bin/python
# encoding: utf-8

from workflow import Workflow, ICON_WEB, ICON_WARNING, PasswordNotFound
from workflow.notify import notify
import sys
import subprocess
import os
import requests

def main(wf):
    wf.logger.debug(wf.args)

    # Get query from Alfred 
    if len(wf.args):
        query = wf.args[0]
    else:
        query = ''

    # Splitting query
    query = query.split()
    if len(query) > 0:
        query_0 = query[0]
    else:
        query_0 = None

    if len(query) > 1:
        query_1 = query[1]
    else:
        query_1 = None

    if query_0 == 'token':
        wf.save_password('looker_token', query_1)
        notify('Looker', 'Saved Looker API Token')

    elif query_0 == 'secret':
        wf.save_password('looker_secret', query_1)
        notify('Looker', 'Saved Looker API Secret')

    elif query_0 == 'host':
        wf.save_password('looker_host', query_1)
        notify('Looker', 'Saved Looker Host: ' + query_1)

    elif query_0 == 'logout':
        wf.delete_password('looker_token')
        wf.delete_password('looker_secret')
        wf.delete_password('looker_host')
        notify('Looker', 'You are logged out - instance has been removed.')

    elif query_0 == 'debug':
        wf.logger.info(wf.settings)
        wf.logger.info(os.path.dirname(requests.__file__))
        wf.logger.info(requests.get("https://www.howsmyssl.com/a/check").text)
        notify("Opening the folder that contains debug logs")
        wf.open_cachedir()

    elif query_0.startswith('http'):
        # open Looker link
        subprocess.call(['open', query_0])

    else:
        notify('Looker', 'Something went wrong. Try again!')


if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))