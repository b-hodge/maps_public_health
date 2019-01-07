import csv
import argparse
import re

def get_cli_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv")
    parser.add_argument("output_csv")
    return parser.parse_args()

def fourToFive(s):
    if len(s) == 4:
        return '0' + s
    else:
        return s

def get_unique_judgements(vals, pat_date):
    known_tuples = dict()
    known_tuples[(pat_date, '06510')] = ['']
    
    date_pattern = re.compile('\d+/\d+/\d+')
    zip_pattern = re.compile('\d{4,5}')
    
    this_date = None
    this_zip = None

    for val in vals:
        if date_pattern.match(val):
            if not this_zip:
                this_date = val
        elif zip_pattern.match(val):
            if this_date:
                this_zip = fourToFive(val)
        elif this_date and this_zip:
            if val.strip().lower() == 'y' or val.strip().lower() == 'n':
                if (this_date, this_zip) not in known_tuples:
                    known_tuples[(this_date, this_zip)] = []
                known_tuples[(this_date, this_zip)].append(val.lower())
                this_date = None
                this_zip = None
            else:
                this_date = None
                this_zip = None    
    
    answers = dict()
    for key in known_tuples:
         this_list = known_tuples[key]
         if 'y' in this_list:
             answers[key] = 'y'
         else:
             answers[key] = 'n'

    if pat_date == '':
        del answers[(pat_date, '06510')]
    
    return answers
   

def gen_new_row(row):
    new_row = dict()

    vals = row.values()
    
    answers = get_unique_judgements(vals, row['PAT Date'])
        
    # do the easy stuff
    new_row['UID'] = row['UID ']
    new_row['ZIP Code'] = fourToFive(row['ZIP Code'])
    new_row['PCP Zipcode'] = fourToFive(row['PCP Zipcode '])
    
    # EKG
    new_row['PCP Nec?'] = ''
    new_row['PCP Date'] = ''
    for (date, zipcode) in answers:
        if (date == row['EKG'] and zipcode == fourToFive(row['EKG Zipcode'])) or (date == row['EKG 2'] and zipcode == fourToFive(row['EKG Zipcode 2'])) or (date == row['EKG 3'] and zipcode == fourToFive(row['EKG Zipcode 3'])):
            if zipcode == new_row['PCP Zipcode']:
                new_row['PCP Nec?'] = answers[(date, zipcode)]
                new_row['PCP Date'] = date
                del answers[(date, zipcode)]
                break

    # PAT
    new_row['PAT Date'] = row['PAT Date']
    if new_row['PAT Date']:
        new_row['PAT Zipcode'] = '06510'
    else:
        new_row['PAT Zipcode'] = ''
    
    if (new_row['PAT Date'], new_row['PAT Zipcode']) in answers:
        new_row['PAT Nec?'] = answers[(new_row['PAT Date'], new_row['PAT Zipcode'])]
        del answers[(new_row['PAT Date'], new_row['PAT Zipcode'])]
    else:
        new_row['PAT Nec?'] = ''
    
    i = 1
    for key in answers:
        this_date = key[0]
        this_zip = key[1]
        new_row['trip' + str(i) + ' date'] = this_date
        new_row['trip' + str(i) + ' zip'] = fourToFive(this_zip)
        new_row['trip' + str(i) + ' nec?'] = answers[key]
        i += 1
    
    return new_row
    

def main():
    args = get_cli_args()

    new_rows = []

    with open(args.input_csv) as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            new_row = gen_new_row(row)
            new_rows.append(new_row)
    
    new_rows_sorted = sorted(new_rows, key=lambda x: len(x), reverse=True)
    keys = new_rows_sorted[0].keys()
    
    with open(args.output_csv, 'w') as output_file:
        writer = csv.DictWriter(output_file, keys)
        writer.writeheader()
        writer.writerows(new_rows)

if __name__ == '__main__':
    main()


