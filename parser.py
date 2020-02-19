import csv
import json
import pandas as pd 
import schedule
import time
import firebase_admin
from firebase_admin import credentials, firestore


cred = credentials.Certificate('ServiceAccountKey.json')
default_app = firebase_admin.initialize_app(cred)
db = firestore.client()

# no. of documents already parsed
global doc_count, doc_ref
doc_count = 0
# time_ = time.time()
def parse():
    global doc_count, doc_ref
    data = open('./mission_flight/test_raw_data.txt', encoding='utf-8', errors='ignore')
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    content = data.readlines()
    # print(len(content))
    coordinates = []
    index_line = 0
    for each_line in content:
        try:
            _, link, _ = each_line.split("'")

            _, location = link.split("=")
            _, coords = location.split(":")
            lat_, long_ = coords.split(",")
            
            if is_number(lat_) and is_number(long_):
                lat_ = float(lat_)
                long_ = float(long_)
                # checking for valid coordinates
                if (lat_ >= -90 and lat_ <= 90) and (long_ >= -180 and long_ <= 180):
                    if (lat_ >= 11 and lat_ <= 12) and (long_ >= 75 and long_ <= 77):
                        if [lat_, long_] not in coordinates[-1:]:
                            coordinates.append([lat_, long_])
                            index_line += 1
        except:
            pass
    parse_coordinates = []
    
    for index, coord in enumerate(coordinates[:-1]):
        if (abs(coord[0] - coordinates[index + 1][0]) <= 0.004 and (abs(coord[1] - coordinates[index + 1][1]) <= 0.004)):
            parse_coordinates.append(coord)
    # print(parse_coordinates)
    
    coord_list = []
    
    for coord in parse_coordinates:
        coord_dict = {}
        coord_dict["LAT"] = coord[0]
        coord_dict["LONG"] = coord[1]
        coord_list.append(coord_dict)
        
    # print(coord_list)

    
    doc_ref = db.collection(u'main_coordinates')
    for index, element in enumerate(coord_list):
        # add if already exists check
        if index >= doc_count:
            element["index"] = index
            doc_ref.add(element)
            doc_count += 1
    print('.', end='')
    
def delete_collection(coll_ref, batch_size=1):
    docs = coll_ref.limit(batch_size).stream()
    deleted = 0

    for doc in docs:
        doc.reference.delete()
        time.sleep(1)
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)
    
def main():
        
    delete_collection(doc_ref, batch_size=1)
    parse()
    time.sleep(10)
    
    
parse()
time.sleep(10)


schedule.every(10).seconds.do(main)

while True:

    schedule.run_pending()
    time.sleep(1)
    


