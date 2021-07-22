import requests
import json
import boto3

#these headers are general, change them according to api's

headers_post = {'content-type': 'application/json'}
headers_put ={'accept': 'application/json','content-type': 'application/json'}

#extracting file from s3 bucket
s3client = boto3.client('s3')
bucketName = "bucketname"
file_to_read = "file path without bucket name"

fileobj = s3client.get_object(Bucket = bucketName, Key = file_to_read)

filedata = fileobj['Body'].read().decode('utf-8')
filedata_json=json.loads(filedata)
datalake = filedata_json["dataDescription"] #will change according to structure, data is stored in file

#iterating through all the tables of datalake
for datalake_table in datalake:
    table_name=datalake_table["metaConfigs"]["spectrumTableName"]
    datalake_column_details=datalake_table["inputConfigs"]["schemaDefinition"]["schemaJson"]["columns"]

    # mapping datalake columns, with key=column name and value=description
    table_columns_datalake={}
    for column in datalake_column_details:
        table_columns_datalake[column["columnName"]]=column["documentation"]  #will change according to structure, data is stored in file
            

    #extracting the table from amundsen with name=table_name 

    payload_table={"page_index": 0, "search_request": {"type": "AND", "filters": {"table": [table_name],"schema":["galaxydb"]}}, "query_term": ""}
    tables_info=requests.post("http://localhost:5001/search_table",data=json.dumps(payload_table), headers=headers_post)
    tables_json=json.loads(tables_info.text)
    #target_table_details=tables_json["results"]
    
    if not tables_json["results"]:
        continue

    table_key=tables_json["results"][0]["key"] #will change according to structure, data is returned
    column_names_array=tables_json["results"][0]["column_names"] #will change according to structure, data is returned
    for column_name in column_names_array:
        
        if(column_name in table_columns_datalake.keys()):
            payload_update_description={"description": table_columns_datalake[column_name]}
            r=requests.put("http://localhost:5002/table/{}/column/{}/description".format(table_key,column_name),data=json.dumps(payload_update_description),headers=headers_put)
            
    
















