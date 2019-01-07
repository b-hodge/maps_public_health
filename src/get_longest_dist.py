import argparse
import requests

DISTANCE_MATRIX_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address=USA+06512&key=AIzaSyAsEZry3l_SoS263hFYysoE9RPf9h6b5LI'

def get_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    return parser.parse_args()

def make_request(origin_list, destination_list):
    url = DISTANCE_MATRIX_URL

    url += '&origins='
    url += '|'.join(origin_list)

    url += '&destinations='
    url += '|'.join(destination_list)
    url += '&key=AIzaSyCSPt9cGZgF0EMB_COcXgYkhux9UnqtOPM'

    # print(url)
    r = requests.get(url)
    return r.json()

def get_longest_dist(zc):
    r = requests.get(GEOCODE_URL.replace('06512', zc))
    rjson = r.json()
    # print(rjson)
    bounds = rjson['results'][0]['geometry']['viewport']
    assert len(bounds) == 2
    pairs = []
    for direction in bounds:
        pairs.append(str(bounds[direction]['lat']) + ',' + str(bounds[direction]['lng']))
    assert len(pairs) == 2
    origin_list = []
    dest_list = []
    origin_list.append(pairs[0])
    dest_list.append(pairs[1])
    res = make_request(origin_list, dest_list)
    return res['rows'][0]['elements'][0]['distance']['text']

def main():
    args = get_cli_args()
    zip_codes = []
    with open(args.infile) as infile:
        for line in infile:
            zip_codes.append(line.strip())

    for zc in zip_codes:
        print(zc + ' ' + get_longest_dist(zc))

if __name__ == '__main__':
    main()
