import requests
import json
import boto3
import re

#these headers are general, change them according to api's

headers_post = {'content-type': 'application/json'}
headers_put ={'accept': 'application/json'}

#extracting file from s3 bucket
s3client = boto3.client('s3')
bucketName = "bucketname"
file_to_read = "file path without bucket name"

fileobj = s3client.get_object(Bucket = bucketName, Key = file_to_read)

filedata = fileobj['Body'].read().decode('utf-8')
filedata_json=json.loads(filedata)
datalake= filedata_json["etlConfigs"] #will change according to structure, data is stored in file

tag_to_update="latest_version"
tag_to_delete="latest_version"

#removing tag tag_to_delete 

for i in range(100):#total page index not known, therefore an arbitary value
    #start to get table with given tag

    payload_table={"page_index": i, "search_request": {"type": "AND", "filters": {"tag": [tag_to_delete]}}, "query_term": ""}
    tables_info=requests.post("http://localhost:5001/search_table",data=json.dumps(payload_table), headers=headers_post)
    tables_json=json.loads(tables_info.text)

    if not tables_json["results"]: #out of the loop , if no tables are there
        break

    table_key=tables_json["results"][0]["key"]   #will change according to structure, data is returned
    requests.delete("http://localhost:5002/table/{}/tag/{}".format(table_key,tag_to_delete))
 

latest_tables=[]  #contains table name that are latest

#getting all the tables that are latest version
for table in datalake:
    table_name=table["metaConfigs"]["spectrumTableName"]    #will change according to structure, data is stored in file
    version=table["metaConfigs"]["version"] #will change according to structure, data is stored in file

    base_name=re.search(".+\D+(?=\d+)",table_name).group()
    latest_version_number=re.search("\d*$",version).group()

    latest_version_table_name=base_name+latest_version_number

    latest_tables.append(latest_version_table_name)


for table_name in latest_tables:

    #extracting the table with table_name=table_name 
    payload_table={"page_index": 0, "search_request": {"type": "AND", "filters": {"table": [table_name],"schema":["galaxydb"]}}, "query_term": ""}
    tables_info=requests.post("http://localhost:5001/search_table",data=json.dumps(payload_table), headers=headers_post)
    tables_json=json.loads(tables_info.text)
    
    if not tables_json["results"]:
        continue

    table_key=tables_json["results"][0]["key"] #will change according to structure, data is returned
    r=requests.put("http://localhost:5002/table/{}/tag/{}".format(table_key,tag_to_update),headers=headers_put)
    












