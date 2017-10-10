#!/usr/bin/env python

import requests
import base64
import json
import sys
import os
from colors import red, yellow, green, blue
import requests.packages.urllib3

requests.packages.urllib3.disable_warnings()

new_repo = sys.argv[1]
org = "gearsofleo"
base_url = "https://hub.docker.com/v2"

try:
    if os.environ["DOCKERHUB_API"]:
        creds = base64.b64decode(os.environ.get('DOCKERHUB_API')).split(":")
        data = {"username": creds[0], "password": creds[1]}
except KeyError:
   print yellow("DOCKERHUB_API env var not set!")
   sys.exit()

def get_token(data):
    """ Retrieve the token used for auth """
    header = {'Content-Type': 'application/json'}
    try:
        r = requests.post(base_url + "/users/login/", headers=header, data=json.dumps(data), stream=True)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print red("Retrieving token failed: {}").format(err)
        sys.exit(1)
    header['Authorization'] = 'JWT ' + str(r.json()["token"])
    print green("Token retrieved.")
    return header

def get_repos():
    """ Checks if $newrepo exists and bails out if it does, otherwise returns all the repos"""
    page = 1
    repos = []
    while (page != 0):
        param = { 'page_size': 1000, 'page': page }
        try:
            r = requests.get(base_url + "/repositories/" + org + "/", headers=token, params=param)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print red("Retrieving repos failed: {}").format(err)
            sys.exit(1)
        readable_json = r.json()
        next_page = str(r.json()['next'])
        for i in readable_json['results']:
            repos.append(str(i['name']))
        if (next_page != "None"):
            page += 1
        else:
            page = 0
    print "Found %s repositories" % (len(repos))
    if new_repo in repos:
        print green("Repository {0} already exists.").format(new_repo)
        sys.exit()
    else:
        print blue("Repo doesn't exist.")
    return repos

def create_private_repo(reponame, desc=None, fulldesc=None):
    """ Creates $newrepo """
    payload = {
        'description': desc or '',
        'full_description': fulldesc or '',
        'is_private': 'true',
        'name': reponame,
        'namespace': org
    }
    try:
        r = requests.post(base_url + "/repositories/", data=json.dumps(payload), headers=token)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print red("Creating new repo failed: {}").format(err)
        sys.exit(1)
    print green("Repo created.")
    return r

def get_groups(header):
    """ Retrieves all the groups and groupIDs """
    param = { 'page_size': 10000 }
    try:
        r = requests.get(base_url + "/orgs/" + org + "/groups/", headers=header, params=param)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print red("Retrieving groups failed: {}").format(err)
        sys.exit(1)
    return r.json()['results']

def set_perms(header):
    """ Hardcoded groupIDs and perms """
    payload = [
        {'group_id': '36124', 'permission': 'admin'},
        {'group_id': '41497', 'permission': 'write'},
        {'group_id': '45777', 'permission': 'read'},
        {'group_id': '36180', 'permission': 'write'}
    ]
    for group_perms in payload:
        try:
            r = requests.post(base_url + "/repositories/" + org + "/" + new_repo + "/groups/", json=group_perms, headers=header)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print red("Setting perms failed: {}").format(err)
            sys.exit(1)
    print green("All perms set.")


print blue("Getting the auth token...")
token = get_token(data)
print blue("Checking if repo already exists...")
get_repos()
print blue("Creating the new repo...")
create_private_repo(new_repo)
print blue("Setting perms for the new repo...")
set_perms(token)
print green("You're good to go!")
