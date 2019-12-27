#!/usr/bin/env python3

import requests
import json
import argparse
import datetime 
import re

debug_on = False
dry_run = False
leave_unused_line_speed = 0

# sabnzdb
sabznzdb_api_url = 'http://URL/sabnzbd/api?output=json&apikey=API_KEY'
sabznzdb_api_url_set_speed = sabznzdb_api_url + '&mode=config&name=speedlimit&value='
sabznzdb_api_url_get_queue = sabznzdb_api_url + '&mode=queue&start=START&limit=LIMIT&search=SEARCH'
sabznzdb_api_url_get_config = sabznzdb_api_url + '&mode=get_config'
sabznzdb_max_line_speed=6200

# Tautulli
tautulli_api_url = f"http://URL/api/v2?apikey=API_KEY&cmd=get_activity"


def get_args():
    global tautulli_api_url
    global sabznzdb_api_url
    global sabznzdb_api_url_set_speed
    global sabznzdb_api_url_get_queue
    global sabznzdb_api_url_get_config
    global debug_on
    global dry_run
    global leave_unused_line_speed

    parser = argparse.ArgumentParser(description='Process some input.')

    parser.add_argument('--tautulli_url', required=True, help='Pass the url for your Tautulli server')
    parser.add_argument('--sabnzdb_url', required=True, help='Pass the url for your SABnzdb server')
    parser.add_argument('--tautulli_api_key', required=True, help='Pass the api_key for your Tautulli server')
    parser.add_argument('--sabnzdb_api_key', required=True, help='Pass the api_key for your SABnzdb server')
    parser.add_argument('--leave_unused_line_speed', default=0, help='Leave some internet for other things (KB)')
    parser.add_argument('--dry_run', action='store_true', help='Don\'t actually change the speed')
    parser.add_argument('--debug', '-d', action='store_true', help='Turn on debugging messages')

    args = parser.parse_args()


    tautulli_api_url = f"http://{args.tautulli_url}/api/v2?apikey={args.tautulli_api_key}&cmd=get_activity"
    sabznzdb_api_url = f"http://{args.sabnzdb_url}/sabnzbd/api?output=json&apikey={args.sabnzdb_api_key}"
    sabznzdb_api_url_set_speed = sabznzdb_api_url + '&mode=config&name=speedlimit&value='
    sabznzdb_api_url_get_queue = sabznzdb_api_url + '&mode=queue&start=START&limit=LIMIT&search=SEARCH'
    sabznzdb_api_url_get_config = sabznzdb_api_url + '&mode=get_config'

    leave_unused_line_speed = int(args.leave_unused_line_speed)

    if args.dry_run:
        dry_run=True
        debug_on=True

    if args.debug:
        debug_on=True
        debug("Turning on Debugging")
        debug(f"Leaving {leave_unused_line_speed}KB unused")

    return args

def debug(*argv):
    if debug_on:
        print( str(datetime.datetime.now().strftime("%Y%m%d%H%M%S")) + ': ', end='') 
        for k in argv:
            print(k, end='')
        print('')
    return

def get_sabnzdb_queue():
    r = requests.get(sabznzdb_api_url_get_queue)
    return json.loads(r.text)['queue']

def get_sabnzdb_config():
    global sabznzdb_max_line_speed

    r = requests.get(sabznzdb_api_url_get_config)
    bandwidth_max=json.loads(r.text)['config']['misc']['bandwidth_max']
   
    x = re.search("(.*?)M$", bandwidth_max)
    if x:
        debug("Speed in MB: ", x.group(1))
        sabznzdb_max_line_speed=(x.group(1)*1024)


    x = re.search("(.*?)K$", bandwidth_max)
    if x:
        debug("Speed in KB: ", x.group(1))
        sabznzdb_max_line_speed=(x.group(1))


    x = re.search("(.*?)B$", bandwidth_max)
    if x:
        debug("Speed in Bytes: ", x.group(1))
        sabznzdb_max_line_speed=(x.group(1)/1024)


    # sabznzdb_max_line_speed=int(float())
    debug ("Max speed in SABnzdb: ", str(sabznzdb_max_line_speed) )

def set_sabnzdb_speed(key='30'):
    if not dry_run:
        r = requests.get(sabznzdb_api_url_set_speed + str(key))
        status=json.loads(r.text)['status']
        debug(f"Set speed to {int(key/1024)}KB: {status}")
    else:
        debug(f"Would have set the speed to {int(key/1024)}KB")

def get_tautulli():
    ret_val = {}
    r = requests.get(tautulli_api_url)
    response=json.loads(r.text)['response']['data']

    ret_val['wan_bandwidth']=response['wan_bandwidth']
    debug("Current Wan Bandwidth: ", ret_val['wan_bandwidth'])

    return (ret_val)


if __name__ == '__main__':
    args = get_args()

    response = get_tautulli()
    config = get_sabnzdb_config()

    queue = get_sabnzdb_queue()
    current_speed = int(float(queue['speedlimit_abs'])/1024)

    new_speed = (int(sabznzdb_max_line_speed) - int(response['wan_bandwidth']) - int(leave_unused_line_speed))*1024

    if not current_speed == int(new_speed/1024):
        set_sabnzdb_speed(key=new_speed)
    else:
        debug("Speeds are the same, not changing")

    
    debug("Finished Successfully")
    exit(0)