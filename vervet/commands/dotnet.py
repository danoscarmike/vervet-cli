import csv
import requests

from datetime import datetime
from pathlib import Path
from tqdm import tqdm

# import util


LANGUAGE = '.NET'
SEARCH_TERM = 'Google.Cloud'


def dotnet():
    reg_page_list = nuget_search(SEARCH_TERM)
    downloads_dir = str(Path.home()) + '/vervet-output/'
    now_str = datetime.now().strftime('%Y%m%d-%H%M%S')
    outfile = now_str + '_dotnet.csv'
    with open(downloads_dir + outfile, 'w') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['package_name', 'version', 'prerelease',
                         'publish_date', 'listed', 'language'])

        for reg_page in tqdm(reg_page_list):
            catalog_entry_list = nuget_registration(reg_page)

            for catalog_entry in catalog_entry_list:
                [package_name,
                 version,
                 publish_date,
                 listed,
                 prerelease,
                 ] = nuget_catalog_entry(catalog_entry)
                writer.writerow([package_name, version, publish_date, listed,
                                 prerelease, LANGUAGE])
    return outfile


# @util.handle_requests_error
def nuget_search(search_term):
    """
    Returns a list of tuples (package_name, registration index urls)
    """
    response = requests.get('https://api-v2v3search-0.nuget.org/query?q=' +
                            search_term + '&prerelease=true&take=200')
    print('\n.NET: making request to NuGet Search Service...{}'.format(
          response.status_code))
    response_json = response.json()
    print('NuGet returned {} hits on search term: "{}".'.format(
          response_json['totalHits'], search_term))
    google_packages = [package['@id'] for package in response_json['data']
                       if 'Google Inc.' in package['authors']]
    print('Of the {} results, {} were authored by \'Google Inc.\''.format(
          response_json['totalHits'], len(google_packages)))

    return google_packages


# @util.handle_requests_error
def nuget_registration(reg_index_url):
    """
    Returns list of catalogEntry urls
    """
    response = requests.get(reg_index_url)
    response_json = response.json()
    reg_pages = response_json['items']
    # Refer to NuGet API docs for a discussion on NuGet API registration
    # pages and leaves. The items array is not always provided.
    # TODO: when items _not_ in items hit the @id url and navigate that
    # TODO: validate assumption that last entry in list is the most recent
    # event
    
    catalog_entry_list = []
    for page in reg_pages:
        if 'items' in page:
            for leaf in page['items']:
                catalog_entry_list.append(leaf['catalogEntry']['@id'])
    return catalog_entry_list


# @util.handle_requests_error
def nuget_catalog_entry(catalog_entry_url):
    """
    Returns package metadata
    """
    response = requests.get(catalog_entry_url)
    response_json = response.json()

    if 'published' in response_json:
        publish_date = response_json['published']
    else:
        publish_date = None

    if 'listed' in response_json:
        listed = response_json['listed']
    else:
        listed = None

    if 'isPrerelease' in response_json:
        prerelease = response_json['isPrerelease']
    else:
        prerelease = None

    return [response_json['id'],
            response_json['version'],
            prerelease,
            publish_date,
            listed,
            ]
