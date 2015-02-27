import csv
import json

labels = ("Start Date/Time","End Date/Time","Location","Qty","Item","Item Comment","first","last","email","Sign Up Comment","Phone","PhoneType")
csv_f = open('volunteers.csv', 'r')
csvfile = csv.DictReader(csv_f, labels)
output = []
scholars = set()
for r in csvfile:
  print r
  if r['email'] not in scholars:
    row = {
        'name': '%s %s' % (r['first'], r['last']),
        'email': r['email']
    }
    output.append(row)
    scholars.add(r['email'])
json.dump(output, open('volunteers.json', 'w'), indent=2, sort_keys=False)
