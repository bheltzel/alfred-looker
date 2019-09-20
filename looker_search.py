#!/usr/bin/python
# encoding: utf-8

from workflow import Workflow, ICON_WEB, ICON_WARNING, ICON_ACCOUNT, ICON_SWITCH, PasswordNotFound
from workflow.notify import notify
import sys
import urllib
import datetime

SETTINGS = [
    {
        'title': 'Looker Host',
        'autocomplete': '> host',
        'arg': 'host',
        'icon': ICON_ACCOUNT
    },
    {
        'title': 'Looker Token',
        'autocomplete': '> token',
        'arg': 'token',
        'icon': ICON_ACCOUNT
    },
    {
        'title': 'Looker Secret',
        'autocomplete': '> secret',
        'arg': 'secret',
        'icon': ICON_ACCOUNT
    },
    {
        'title': 'Debug',
        'autocomplete': '> Debug',
        'arg': 'debug',
        'icon': ICON_SWITCH
    }
]

def conn(host, my_token, my_secret):
    from lookerapi import LookerApi

    my_host = 'https://%s.looker.com:19999/api/3.0/' % (host)
    looker = LookerApi(host=my_host, token=my_token, secret=my_secret)
    if looker is None:
        notify('Alfred - Looker', 'Connection to Looker failed!')
        exit()

    return looker

def get_object_url(instance_url, object_id, use_classic = False):
    if use_classic == True:
        return "%s/%s" % (instance_url, object_id)
    else:
        return "%s/one/one.app#/sObject/%s/view" % (instance_url, object_id)

def main(wf):
    host = 'demo'
    wf.logger.debug(wf.args)

    # Get query from Alfred
    if len(wf.args):
        query = wf.args[0]
    else:
        query = ''

    # Splitting query
    query_split = query.split()
    if len(query_split) > 0:
        query_0 = query_split[0]
    else:
        query_0 = None

    if len(query_split) > 1:
        query_1 = query_split[1]
    else:
        query_1 = None

    # Trimming full query
    query = query.strip()

    try:
        looker_host = wf.get_password('looker_host')
        looker_token = wf.get_password('looker_token')
        looker_secret = wf.get_password('looker_secret')
    except PasswordNotFound:
        looker_host = None
        looker_token = None
        looker_secret = None

    if query_0 == '>':

        for s in SETTINGS:
            if query_1 is None or s['arg'].startswith(query_1.lower()):
                
                if query_1 == 'token' or query_1 == 'secret' or query_1 == 'host':
                    if len(query) > 8:
                        query_2 = query_split[2]
                    else:
                        query_2 = ''
                        
                    wf.add_item(
                        title=s['title'],
                        arg=s['arg'] + ' ' + query_2,
                        icon=s['icon'],
                        autocomplete=s['autocomplete'],
                        valid=True
                    )
                else:
                    wf.add_item(
                        title=s['title'],
                        arg=s['arg'],
                        icon=s['icon'],
                        autocomplete=s['autocomplete'],
                        valid=True
                    )

    elif looker_token is None:
        wf.add_item(
            'No configuration for Looker.',
            'Type "lkr > host" ; "lkr > token" ; "lkr > secret", to set your Looker account.',
            valid=False,
            icon=ICON_WARNING,
            autocomplete= '> token'
        )

    elif query_0 is not None and len(query)>1:
        looker = conn(looker_host, looker_token, looker_secret)
        if looker is None:
            wf.add_item(
                "Looker connection failed."
            )
        else:
            results_dashboards = looker.search_dashboards(query_0)

            if results_dashboards:
                for record in results_dashboards:
                    sub = "sub"
                    ico = "dashboard.png"
                    url = "https://%s.looker.com/dashboards/%s" % (host, str(record['id']))

                    if 'view_count' in record:
                        if record['view_count'] > 0:
                            view_count = str("{:,}".format(record['view_count']))
                        else:
                            view_count = '0'
                    else:
                        view_count = '0'
                    sub = str(record['space']['name']) + ' --- ' + view_count + ' views'    
                    # if 'updated_at' in record:
                    #     sub += ' --- Last updated: ' + str(record['updated_at'])
                    # else:
                    #     # days_ago = abs(datetime.datetime.strptime(record['created_at'], '%Y-%m-%dT%H:%M:%S.%f') - datetime.datetime.now()).days
                    #     sub += ' --- Created: ' + str(days_ago)
                    wf.add_item(
                        title=str(record['title']).encode('ascii', 'replace'),
                        subtitle=sub,
                        arg=url,
                        valid=True,
                        icon=ico
                    )

            results_looks = looker.search_looks(query_0)

            if results_looks:
                for record in results_looks:
                    sub = "sub"
                    ico = "look.png"
                    url = "https://%s.looker.com/looks/%s" % (host, str(record['id']))

                    if 'view_count' in record:
                        if record['view_count'] > 0:
                            view_count = str("{:,}".format(record['view_count']))
                        else:
                            view_count = '0'
                    else:
                        view_count = '0'
                    sub = str(record['space']['name']) + ' --- ' + view_count + ' views'    
                    # if 'updated_at' in record:
                    #     sub += ' --- Last updated: ' + str(record['updated_at'])
                    # else:
                    #     # days_ago = abs(datetime.datetime.strptime(record['created_at'], '%Y-%m-%dT%H:%M:%S.%f') - datetime.datetime.now()).days
                    #     sub += ' --- Created: ' + str(days_ago)
                    wf.add_item(
                        title=record['title'].encode('ascii', 'replace'),
                        subtitle=sub,
                        arg=url,
                        valid=True,
                        icon=ico
                    )

            if len(results_looks) == 0 and len(results_dashboards) == 0:
                wf.add_item(
                    "No result for: %s" % query
                )
    else:
        wf.add_item(
            "Type at least two characters to search on Looker."
        )

    wf.send_feedback()
    return 0

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))