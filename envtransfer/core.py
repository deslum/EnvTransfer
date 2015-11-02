# -*- coding: utf-8 -*-
from urllib2 import Request, urlopen, build_opener, HTTPHandler
from exception import function_exception
from webbrowser import open as wbopen
from settings import config
from zipfile import ZipFile
from json import loads
from help import show
import sys
import os


arguments = {'auth', 'upload', 'download'}

def save_config():
    with open('settings.py','w') as f:
        f.write('config={}'.format(str(config)))


def get(url):
    header = headers={"Authorization": "OAuth {}".format(config['TOKEN'])}
    request = Request(url, headers = header)
    response = urlopen(request).read()
    return response


def auth():
    request = Request('https://oauth.yandex.ru/authorize?response_type=code&client_id={}&state=EnvTransfer'.format(config['ID'])) 
    url = urlopen(request).geturl()
    wbopen(url)
    code = raw_input('Enter your code:')
    if code:
        data = 'grant_type=authorization_code&code={}&client_id={}&client_secret={}'.format(code, config['ID'], config['ID_PASS'])
        request = Request('https://oauth.yandex.ru/token', headers = {"Host": "oauth.yandex.ru",
                                                "Content-type": "application/x-www-form-urlencoded", "Content-Length": len(data)})
        response = urlopen(request, data)
        config['TOKEN'] = response.read().split('"')[7]
        if config['TOKEN']:
            save_config()


def upload_file(name):
    request = 'https://cloud-api.yandex.net/v1/disk/resources/upload?path={}&overwrite=true&fields=href'.format(name)
    string = get(request)
    with open(name, 'rb') as read_file:
        data = read_file.read()
    opener = build_opener(HTTPHandler)
    url = loads(string)['href'].encode('ascii')
    request = Request(url, data=data)
    request.add_header('Content-Type', 'application/binary')
    request.get_method = lambda: 'PUT'
    opener.open(request)


def download_file(name):
    request = 'https://cloud-api.yandex.net/v1/disk/resources/download?path={}&fields=href'.format(name)
    string = get(request)
    url = loads(string)['href']
    response = urlopen(url)
    data = response.read()
    with open(name, 'wb') as save_file:
        save_file.write(data)


def get_archive(name, path):
    with ZipFile(name, 'w') as archive:
        for root, dirs, files in os.walk(path):
            for file_name in files:
                if not file_name in name:
                    archive.write(os.path.join(root, file_name))



def extract_archive(name):
    with open(name, 'rb') as file_handle:
        zipfile = ZipFile(file_handle)
        for name in zipfile.namelist():
            out_path = os.getcwd()
            zipfile.extract(name, out_path)
        zipfile.close()


def start():
    if len(sys.argv) > 1 and sys.argv[1] in arguments:
        find_file()
        command = sys.argv[1]
        if command in 'auth':
            auth()
        elif command in 'upload':
            abspath = os.getcwd().split('/')[-1].lower()
            file_name = '{}.zip'.format(abspath)
            get_archive(file_name, '.')
            upload_file(file_name)
        elif command in 'download':
            file_name = raw_input('Enter your environment name (example: myenv.zip): ').lower()
            download_file(file_name)
            extract_archive(file_name)
    else:
        help.show()