import argparse
import json
import csv
import requests
import sys

DISTANCE_MATRIX_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
output = dict()

def get_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_csv')
    parser.add_argument('output_csv')
    return parser.parse_args()

def ingest_rows(input_csv, intra_zip_map):
    tasks = dict()
    with open(input_csv) as infile:
        for line in infile:
            splits = line.strip().split(',')

            # Skip the header row
            if splits[0] == 'patient UID':
                continue
            else:
                key = splits[0]
                if key:
                    origin_list = list()
                    home = splits[1]
                    if '-' in home:
                        home = home.split('-')[0]
                    if len(home) < 5:
                        home = '0' + home
                    origin_list.append('USA ' + home)

                    destination_list = list()
                    i = 1
                    for s in splits[2:]:
                        if s.strip() and s.strip() != '0':
                            if '-' in s:
                                if key == '4586':
                                    print(s)
                                s = s.split('-')[0]
                                if key == '4586':
                                    print(s)
                            if len(s) < 5:
                                s = '0' + s
                            if s.strip() == home.strip():
                                if key == '1335':
                                    print(s)
                                sub_key = 'dist' + str(i)
                                if key not in output:
                                    output[key] = dict()
                                output[key][sub_key] = str(intra_zip_map[s.strip()]) + ' mi'
                            else:
                                destination_list.append('USA ' + s)
                        else:
                            sub_key = 'dist' + str(i)
                            # print(key)
                            # print(sub_key)
                            if key not in output:
                                output[key] = dict()
                            output[key][sub_key] = 'MISSING'
                        i += 1
                    tasks[key] = (origin_list, destination_list)

    return tasks

def make_request(origin_list, destination_list):
    print(origin_list)
    url = DISTANCE_MATRIX_URL

    url += '&origins='
    url += '|'.join(origin_list)

    url += '&destinations='
    url += '|'.join(destination_list)
    url += '&key=AIzaSyBkTsroJvyzVBL5L2iv41C_Q-FTe_SGZbA'

    print(url)
    r = requests.get(url)
    return r.json()

def parse_results(key, response_json, origin_list, destination_list, intra_zip_map):
    to_fill = []
    if key in output:
        for i in range(1, 10):
            sub_key = 'dist' + str(i)
            if sub_key not in output[key]:
                to_fill.append(sub_key)
    else:
        output[key] = dict()
        to_fill = ['dist1', 'dist2', 'dist3', 'dist4', 'dist5', 'dist6', 'dist7', 'dist8', 'dist9']

    try:
        for sub_key, element in zip(to_fill, response_json['rows'][0]['elements']):
            try:
                assert sub_key not in output[key]
                output[key][sub_key] = element['distance']['text'].replace(',','')
            except KeyError:
                print(response_json)
                output[key][sub_key] = 'ERROR'
    except IndexError:
        print(response_json)



    # print(response_json)
    # origin = origin_list[0].strip()
    # for d in destination_list:
    #     if d.strip() == origin:
    #         print(d)
    # i = 1
    # for element in response_json['rows'][0]['elements']:
    #     output_key_string = 'dist' + str(i)
    #     try:
    #         dist = element['distance']['text']
    #         if dist == '1 ft':
    #             this_zip = origin_list[0].split(' ')[1]
    #             if output_key_string not in output[key]:
    #                 output[key][output_key_string] = str(intra_zip_map[this_zip]) + ' mi'
    #             # output.append(str(intra_zip_map[this_zip]) + ' mi')
    #         else:
    #             if output_key_string not in output[key]:
    #                 output[key][output_key_string] = element['distance']['text']
    #             # output.append(element['distance']['text'])
    #     except KeyError:
    #         print(response_json)
    #         if key not in output:
    #             output[key] = dict()
    #         if output_key_string not in output[key]:
    #             output[key][output_key_string] = 'ERROR'
    #         # output.append('ERROR')
    #     i += 1

def write_output(output_csv):
    # First, find out how long the header needs to be
    max_length = 0
    for key in output:
        this_length = len(output[key])
        if this_length > max_length:
            max_length = this_length

    # Now build the header row
    header_row = ['patient']
    for i in range(1, max_length + 1):
        header_row.append('dist' + str(i))

    with open(output_csv, 'w') as outfile:
        outfile.write(','.join(header_row) + '\n')

        for key in sorted(output):
            this_output = []
            this_output.append(key)
            for j in range(1, len(output[key]) + 1):
                print(key)
                print(len(output[key]))
                print(output[key])
                this_row = output[key]
                sub_key = 'dist' + str(j)
                try:
                    this_output.append(this_row[sub_key])
                except KeyError:
                    print('Tried to access a sub key that didnt exist. Exiting')
                    print(key)
                    print(sub_key)
                    sys.exit(1)
            outfile.write(','.join(this_output) + '\n')

def main():
    args = get_cli_args()

    intra_zip_map = dict()
    with open('resources/zipcodes-longest-dist.txt') as infile:
        for line in infile:
            split_line = line.split(' ')
            zip_code = split_line[0]
            dist = split_line[1]
            intra_zip_map[zip_code] = float(dist) / 6.0

    # tasks is a dict, where the keys are patient IDs and each value is a list of tuples of the form:
    #   ([origin1, origin2, ..., originX], [destination1, destination2, ..., destinationY])
    tasks = ingest_rows(args.input_csv, intra_zip_map)

    for key in tasks:
        task = tasks[key]
        origin_list, destination_list = task
        response_json = make_request(origin_list, destination_list)
        parse_results(key, response_json, origin_list, destination_list, intra_zip_map)

    write_output(args.output_csv)

if __name__ == '__main__':
    main()
