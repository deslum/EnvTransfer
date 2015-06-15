# -*- coding: utf-8 -*-
from __init__ import __version__
from exception import function_exception
from zipfile import ZipFile
from json import loads
import webbrowser
import settings
import urllib2
import help
import sys
import os


arguments = {'auth', 'upload', 'download'}


def save_token(token):
    settings.TOKEN = token
    with open(settings.token_file, 'wb') as token_file:
        token_file.write(token)


def find_file():
    if os.path.isfile(settings.token_file):
        with open(settings.token_file, 'rb') as token_file:
            settings.TOKEN = token_file.read(32)


def post(code):
    data = ''.join([
        'grant_type=authorization_code&code=', code,
        '&client_id=', settings.ID,
        '&client_secret=', settings.ID_PASS])

    headers = {
        'Host': 'oauth.yandex.ru',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': len(data),
        'User-Agent': 'EnvTransfer ' + __version__}

    request = urllib2.Request(
        'https://oauth.yandex.ru/token', data, headers)

    return urllib2.urlopen(request)


def get(url):
    oauth = 'OAuth ' + settings.TOKEN
    request = urllib2.Request(url)
    request.add_header('Authorization', oauth)

    return urllib2.urlopen(request).read()


@function_exception
def auth():
    url = ''.join([
        'https://oauth.yandex.ru/authorize?',
        'response_type=code',
        '&client_id=', settings.ID,
        '&state=EnvTransfer'])

    webbrowser.open(url)
    code = raw_input('Enter your code:')
    json = post(code).read()

    token = loads(json)['access_token'].encode('ascii')
    save_token(token)


@function_exception
def upload_file(name):
    url = ''.join([
        'https://cloud-api.yandex.net/',
        'v1/disk/resources/upload?',
        'path=', name,
        '&overwrite=true'])

    json = get(url)
    url = loads(json)['href'].encode('ascii')

    with open(name, 'rb') as read_file:
        data = read_file.read()

    req = urllib2.Request(url, data)
    req.get_method = lambda: 'PUT'
    urllib2.urlopen(req)


@function_exception
def download_file(name):
    url = ''.join([
        'https://cloud-api.yandex.net/',
        'v1/disk/resources/download?',
        'path=', name])

    json = get(url)
    url = loads(json)['href'].encode('ascii')

    res = urllib2.urlopen(url)
    with open(name, 'wb') as save_file:
        save_file.write(res.read())


@function_exception
def get_archive(name, path):
    with ZipFile(name, 'w') as archive:
        for root, dirs, files in os.walk(path):
            for file_name in files:
                if file_name in name:
                    continue
                archive.write(os.path.join(root, file_name))


@function_exception
def extract_archive(name):
    out_path = os.getcwd()
    with ZipFile(name, 'r') as zipfile:
        for name in zipfile.namelist():
            zipfile.extract(name, out_path)


def start():
    if len(sys.argv) > 1 and sys.argv[1] in arguments:
        find_file()
        command = sys.argv[1]
        if command in 'auth':
            auth()
        elif command in 'upload':
            abspath = os.getcwd().split('/')[-1].lower()
            file_name = "".join([abspath, '.zip'])
            get_archive(file_name, '.')
            upload_file(file_name)
        elif command in 'download':
            msg = 'Enter your environment name (example: myenv.zip): '
            file_name = raw_input(msg.lower())
            download_file(file_name)
            extract_archive(file_name)
    else:
        help.show()

__name__ == '__main__' and sys.exit(start())
