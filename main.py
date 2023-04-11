import time
import json

from bs4 import BeautifulSoup
import requests
import configparser


# The next step is to run csv.py to convert the json file into csv

# read config.txt
parser = configparser.ConfigParser()
parser.read('config.txt')
class_category = parser.get('config', 'organization_type')
is_active = parser.get('config', 'is_active')
name = parser.get('config', 'search_term')

url_parser = configparser.ConfigParser()
url_parser.read('url.txt')
config_url = url_parser.get('url', 'link')
config_token = url_parser.get('url', 'token')


# Initialize empty json file for processing data
file_name = 'webscrape_' + class_category + '.json'
with open(file_name, 'w') as empty_json:
    json.dump([], empty_json, indent=4)
    empty_json.close()

# Initialize empty json file for raw html data
html_data = 'webscrape_' + class_category + '_raw_html.json'
with open(html_data, 'w') as empty_json:
    json.dump([], empty_json, indent=4)
    empty_json.close()


def get_class_from_category(string):
    mapping = {
        'Conf/Union/Div': 1,
        'Congregation': 2,
        'School': 3,
        'Conf/Union/Div Sub-Orgs': 4,
        'Medical': 5,
        'Media': 6,
        'Publishing': 7,
        'Foreign': 8,
        'Unknown': 9,
        'Congregation Sub-Orgs': 10
    }

    return mapping.get(string, 0)


form_data = {
    'name': name,
    'class': get_class_from_category(class_category),
    'authenticity_token': config_token,
    'is_active': is_active,
    'commit': 'Search',
}


def get_urls_list(html):
    links = []
    soup = BeautifulSoup(html, 'lxml')
    url_list = soup.find_all('tr', class_='results-line-1')
    for url in url_list:
        links.append(url.a['href'])
    return links


def write_json_data(data_dict):
    # read file
    with open(file_name, "r") as read:
        data = json.load(read)

    # update json object
    data.append(data_dict)

    # write json file
    with open(file_name, 'w') as write:
        json.dump(data, write, indent=4)


def write_json_data_raw(raw_html):
    # read file
    with open(html_data, "r") as read:
        data = json.load(read)

    # update json object
    data.append(raw_html)

    # write json file
    with open(html_data, 'w') as write:
        json.dump(data, write, indent=4)


def scrape_data_from_url_page(url):
    time.sleep(5)

    full_url = config_url + url
    server = requests.post(full_url)
    status_code = server.status_code

    if status_code == 429:

        print("Encountered status code 429, waiting for 20s for next request...")
        time.sleep(20)
        server = requests.post(full_url)

    html = server.text
    soup = BeautifulSoup(html, 'lxml')

    for linebreak in soup.find_all('br'):
        linebreak.replaceWith("~")

    write_json_data_raw(html)

    # Get Data and Transfer to Txt File
    title = soup.find('span', id='title')
    fields = soup.find_all('td', class_='field')
    labels = soup.find_all('label')

    field_array = []

    for field in fields:
        if field.a is not None:
            field_array.append(field.a['href'] + " " + field.text)
        else:
            field_array.append(field.text)

    label_array = []

    for label in labels:
        label_array.append(label.text)

    data_dict = {'title': title.text}

    for i in range(len(label_array)):
        data_dict[label_array[i]] = field_array[i]

    print(data_dict)
    write_json_data(data_dict)


def get_results_page(page):
    string_number = page.__str__()
    url = config_url + '/en/search?page=' + string_number + '&type=a'

    time.sleep(5)  # avoid 429 too many requests - 5s seems to be the most optimal
    server = requests.post(url, data=form_data)
    status_code = server.status_code

    # handle 429 code
    if status_code == 429:
        print("Encountered status code 429, waiting for 20s for next request...")
        time.sleep(20)
        server = requests.post(url, data=form_data)

    search_results_html = server.text

    url_list = get_urls_list(search_results_html)

    for url in url_list:
        scrape_data_from_url_page(url)

    return len(url_list)


def go_to_next_page():
    page = 1

    while get_results_page(page) > 0:
        print("Page " + page.__str__())
        page += 1


go_to_next_page()
