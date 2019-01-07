# Input is a newline-separated list of ZIP codes
# Prints a list of ZIP codes and their miidpoint lat / long to stdout

import requests
import argparse

GEOCODE_URL = 'https://maps.googleapis.com/maps/api/geocode/json?address=USA+06512&key=AIzaSyAisfdc4BXXv8fzte0VpptDSdqHvLybpzg'

def get_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('infile')
    return parser.parse_args()

def get_midpoint(zc):
    r = requests.get(GEOCODE_URL.replace('06512', zc))
    rjson = r.json()
    location = rjson['results'][0]['geometry']['location']
    return str(location['lat']) + ' ' + str(location['lng'])

def main():
    args = get_cli_args()
    zip_codes = []
    with open(args.infile) as infile:
        for line in infile:
            zip_codes.append(line.strip())

    for zc in zip_codes:
        print(zc + ' ' + get_midpoint(zc))
if __name__ == '__main__':
    main()
