from fastapi import FastAPI, HTTPException, Request, Response, Depends
from fastapi.openapi.utils import get_openapi
from pymongo import MongoClient
import pymongo 
import os
from urllib.parse import unquote

app = FastAPI()

def get_database():   
    CONNECTION_STRING = "mongodb://"+str(os.environ["MONGO_USER"])+":"+str(os.environ["MONGO_PASSWORD"])+"@"+str(os.environ["MONGO_SERVER"])
    client = MongoClient(CONNECTION_STRING,int(os.environ["MONGO_PORT"]))
    return client[str(os.environ["MONGO_DB_NAME"])]
    
# Get the database   
dbname = get_database()    

@app.post("/{obj}/multi", tags=["Realtime"])
async def multi(obj: str, request: Request):   
    payload = await request.body()
    payload = payload.decode("utf-8") 
    payload = unquote(payload)
    payload = payload.replace(";@%",".*")
    payload = payload.replace("%",".*")
    filter = {}

    
    if 'LIKE' in payload:                
        #Ex: id LIKE=%
        #Ex: interface LIKE=%&queue_name=60
        #Ex: id LIKE=100;@%    
        field_name1 = payload.split(" ")[0]   #interface     
        value1      = payload.split(" ")[1]   # LIKE=%&queue_name=60
        params      = value1.split("&")       # ['LIKE=%','queue_name=60']
        
        #If query has too many values to filter like "interface LIKE=%&queue_name=60"
        for item in params:
            key = item.split('=')[0]
            value = item.split('=',1)[1]
            if key == 'LIKE' and value == '.*':
                filter[field_name1]={'$regex': '.*'}
            elif key == 'LIKE' and value != '.*': 
                filter[field_name1]={'$regex': value}
            else:
                filter[key] = value
    
    elif '<==' in payload:
        #Ex: expiration_time <==1638149149
        field_name = payload.split(' <==')[0]        
        value      = payload.split(' <==')[1]
        filter[field_name]={'$lte':value}
    elif '!==' in payload:
        #Ex: contact !==
        field_name = payload.split(' !==')[0]        
        value      = payload.split(' !==')[1]           
        filter[field_name]={'$ne':value}
    else:        
        #Ex: id=101@mydomain.com
        field_name = payload.split('=')[0]        
        value      = payload.split('=')[1]        
        filter[field_name]={'$eq':value}


    print('Filter applied:\n',filter)
    projection = {"_id":0} 
    cursor = dbname[obj].find(filter,projection)
    data = ''
    for item in cursor:
        for key in item:                
            data = data+str(key)+'='+str(item[key])+'&'
        data = data + '\n'      
    print(data)                               
    return Response(content=data,status_code=200,media_type='text/html')
    
    
@app.post("/{obj}/single", tags=["Realtime"])
async def single(obj: str, request: Request):   
    payload = await request.body()
    payload = payload.decode("utf-8") 
    payload = unquote(payload)
    field_name = payload.split('=')[0]
    value      = payload.split('=')[1]
    values = {}
    values['$eq']=value
    filter = {str(field_name):values}
    print('Filter applied:\n',filter)
    projection = {"_id":0} 
    cursor = dbname[obj].find(filter,projection)
    data = ''
    for item in cursor:
        for key in item:                
            data = data+str(key)+'='+str(item[key])+'&'
        data = data + '\n'                                    
    return Response(content=data,status_code=200,media_type='text/html')
    

@app.post("/{obj}/store", tags=["Realtime"])
async def single(obj: str, request: Request):   
    payload = await request.body()
    payload = payload.decode("utf-8") 
    payload = unquote(payload)
    document = {}
    
    for item in payload.split('&'):
        key = item.split('=')[0]
        value = item.split('=',1)[1]
        if key in ['expiration_time','qualify_frequency']:
            value = int(value)
        if key in ['qualify_timeout']:
            value = float(value)
        document[key]=value


    print('Document to be inserted: \n',document)
    cursor = dbname[obj].insert_one(document)                                          
    return Response(content=str(1),status_code=200,media_type='text/html')
    

@app.post("/{obj}/destroy", tags=["Realtime"])
async def single(obj: str, request: Request):   
    payload = await request.body()
    payload = payload.decode("utf-8") 
    payload = unquote(payload)    
    document = {}
    fieldname = payload.split('=')[0]
    value = payload.split('=')[1]
    value = value.replace('&','')
    document[fieldname]=value
    print('Document to be deleted: \n',document)
    cursor = dbname[obj].delete_one(document)
    deleted = cursor.deleted_count                                          
    return Response(content=str(deleted),status_code=200,media_type='text/html')    


@app.post("/{obj}/update", tags=["Realtime"])
async def single(obj: str, request: Request, id: str):   
    payload = await request.body()
    payload = payload.decode("utf-8") 
    payload = unquote(payload)    
    filter = {"id":str(id)}
    document = {}

    for item in payload.split('&'):
        key = item.split('=')[0]
        value = item.split('=',1)[1]
        if key in ['expiration_time','qualify_frequency']:
            value = int(value)
        if key in ['qualify_timeout']:
            value = float(value)
        document[key]=value    

    print('Document to be updated: \n',document)
    print('Filter applied: \n',filter)
    cursor = dbname[obj].update_one(filter,{'$set':document})
    return Response(content=str(1),status_code=200,media_type='text/html')


