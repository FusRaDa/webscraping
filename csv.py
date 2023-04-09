import configparser
import json
from itertools import chain

# After running this script, import with Excel

# Excel settings: Delimited -> set delimiter as comma only, and finish!

parser = configparser.ConfigParser()
parser.read('config.txt')
class_category = parser.get('config', 'organization_type')

# Enter name of json file you want to turn into csv
json_file_name = 'webscrape_' + class_category + '.json'
json_file = json.load(open(json_file_name, 'r'))

# Initialize empty txt file
txt_file_name = 'webscrape' + class_category + '.txt'
txt_file = open(txt_file_name, "w", encoding='utf-16')


def get_all_keys():
    array = []
    all_keys = list(set(chain.from_iterable(sub.keys() for sub in json_file)))
    for label in all_keys:
        array.append(label)
    array.sort(key=str.lower)
    return array


search_keys = get_all_keys()

# You may edit headers here or on Excel
copy_search_keys = search_keys.copy()
copy_search_keys[0] = "Facebook"
print(copy_search_keys)

# write headers first
for key in copy_search_keys:
    txt_file.write((key + ", "))

txt_file.write("\n")

for data in json_file:
    for key in search_keys:
        try:
            txt_file.write(data[key].replace('\r\n', '').replace('\n', '').replace(',', '') + ",")
        except KeyError:
            txt_file.write("N/A,")
    txt_file.write("\n")

txt_file.close()
