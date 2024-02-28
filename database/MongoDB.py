from db import DataBase
from pymongo import MongoClient
from model.result import Result
from model.query import Query
from config.settings import Settings
from typing import List
import re


class MongoDB(DataBase):

    @property
    def principal_database(self)->str:
        return ""
    
    def _get_cursor(self):
        client = MongoClient(self.host, 27017)
        db = client[self._database]
        return db
    
    def _get_columns_from_table(self, tablename:str):
        db = self._get_cursor()
        collection = db[tablename]
        columns=[]
        key_names = collection.aggregate([
                {"$project": {"keys": {"$objectToArray": "$$ROOT"}}},
                {"$project": {"keys": "$keys.k"}},
                {"$group": {"_id": None, "keys": {"$addToSet": "$keys"}}}
            ])
        
        for key in key_names:
            columns.append(key["keys"][0])
        
        return columns[0] if len(columns)>0 else []
    
    def insert_data(self, tablename, data, columns=None):
        
        db = self._get_cursor()
        collection = db[tablename]
        
        hash = self._gethash(data)
        exists = collection.count_documents({self._hashcolumn:hash})
        if exists == 0:
            document = {}
            for index, column in enumerate(columns):
                document[column] = data[index]
            
            if self._hashcolumn not in document:
                document[self._hashcolumn] = hash

            collection.insert_one(document)
    
    def search_tables(self, filter:str,operator:str='ilike', logic_operator:str='or') -> Result:
        result = Result(headers=['tables'])
        db = self._get_cursor()
        rows = db.list_collection_names(filter={"name":{"$regex":f"{filter}"}})
        for row in rows:
            result.rows.append([row])

        return result
    def search_columns(self, filter:str,operator:str='ilike', logic_operator:str='or') -> Result:
        result = Result(headers=['table_name','column_name'])
        db = self._get_cursor()
        regex = re.compile(re.escape(filter), re.IGNORECASE)
        for collection_name in db.list_collection_names():
            rows = db[collection_name].find({})
            for row in rows:
                for key in row:
                    if regex.search(key):
                        result.rows.append([collection_name, key])
        
        return result

    def execute_query(self, query:str):
        results = []
        db = self._get_cursor()
        collection = db[query["tablename"]]
        sentence = query["qry"]
        rows = collection.find(sentence)
        for row in rows:
            results.append(row)
        
        return results if len(results)>0 else None

    def create_query_to_all_values(self, value_to_find, operator='$or') -> List[Query]:
        db = self._get_cursor()
        queries:List[Query] = []
        
        for collection_name in db.list_collection_names():
            collection_data = db[collection_name].find_one()
            if collection_data:

                query ={operator: [
                    {key: {"$regex": value_to_find, "$options": "i"}} 
                    for key in db[collection_name].find_one().keys()
                    if key != '_id' and key != Settings.checksum_column
                    ]}
            
                queries.append(Query(word=value_to_find, sentence={"tablename":collection_name, "qry":query}, tablename=collection_name))

        return queries
        




