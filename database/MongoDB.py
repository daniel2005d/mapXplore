from db import DataBase
from pymongo import MongoClient

class MongoDB(DataBase):

    def _get_cursor(self):
        client = MongoClient(self.host, 27017)
        db = client[self._database]
        return db
    
    def _get_columns_from_table(self, tablename:str):
        db = self._get_cursor()
        collection = db[tablename]
        columns=[]
        key_names = collection.aggregate([
                # Convertir el documento en un array de pares clave-valor
                {"$project": {"keys": {"$objectToArray": "$$ROOT"}}},
                # Extraer los nombres de las claves
                {"$project": {"keys": "$keys.k"}},
                # Unir los nombres de las claves en un solo array
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
