import hashlib

class Hashes:
    @staticmethod
    def get_hash_value(text, hash_type)->str:
        hash_obj = hashlib.new(hash_type)
        hash_obj.update(str(text).encode())
        hash_hex = hash_obj.hexdigest()
        return hash_hex

    @staticmethod
    def get_available_algorithms():
        return hashlib.algorithms_available