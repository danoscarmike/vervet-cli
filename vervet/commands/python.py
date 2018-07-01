import csv
import requests

from datetime import datetime
from dateutil.parser import parse
from pathlib import Path
from tqdm import tqdm
from xml.etree import ElementTree

# import util


LANGUAGE = 'Python'
SEARCH_TERM = 'google-cloud-'
OWNERS = ['Google Cloud Platform',
          'Google Inc',
          'Google, Inc.',
          'Google LLC']


def python():
    package_list = pypi_search(SEARCH_TERM)
    downloads_dir = str(Path.home()) + '/vervet-output/'
    now_str = datetime.now().strftime('%Y%m%d-%H%M%S')
    outfile = now_str + '_python.csv'
    with open(downloads_dir + outfile, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['package_name',
                         'version',
                         'dev_status',
                         'publish_date',
                         'language'
                         ])

        for package in tqdm(package_list):
            package_info_json = pypi_json(package)
            dev_status = get_dev_status(package_info_json)
            if owner_is_author(OWNERS, package_info_json):
                for k, v in package_info_json['releases'].items():
                    version = k
                    if len(v) > 0:
                        publish_date = parse(v[0]['upload_time'])
                    else:
                        publish_date = None
                    writer.writerow([package,
                                     version,
                                     dev_status,
                                     publish_date,
                                     LANGUAGE
                                     ])

    return outfile


# @util.handle_requests_error
def pypi_search(search_term):
    simple_index = 'https://pypi.python.org/simple/'
    response = requests.get(simple_index)
    print('\nPython: making request to PyPI Simple API.')
    tree = ElementTree.fromstring(response.content)
    search_results = []
    for a in tree.iter('a'):
        if search_term in a.text:
            package_name = a.attrib['href'].strip('/').split('/')[1]
            search_results.append(package_name)
    print('PyPI returned {} hits on search term: "{}".'.format(
          len(search_results), search_term))
    return search_results


# @util.handle_requests_error
def pypi_json(package):
    response = requests.get('https://pypi.org/pypi/' + package + '/json')
    return response.json()


def get_dev_status(package_info_json):
    dev_status_classifiers = {
        'Development Status :: 1 - Planning': 'Planning',
        'Development Status :: 2 - Pre-Alpha': 'Pre-Alpha',
        'Development Status :: 3 - Alpha': 'Alpha',
        'Development Status :: 4 - Beta': 'Beta',
        'Development Status :: 5 - Production/Stable': 'GA',
        'Development Status :: 6 - Mature': 'GA (Mature)',
        'Development Status :: 7 - Inactive': 'Inactive',
    }

    if 'classifiers' in package_info_json['info']:
        for classifier in package_info_json['info']['classifiers']:
            if classifier.startswith('Development Status ::'):
                return dev_status_classifiers[classifier]


def owner_is_author(owners, package_info_json):
    if any(owner in package_info_json['info']['author'] for owner in owners):
        return True
    else:
        return False
