# -*- coding: utf-8 -*-
import hashlib

def generateETagbyString(raw_string):
    raw_string_in_byte_format = raw_string.encode('utf-8')
    generated_etag = hashlib.md5(raw_string_in_byte_format).hexdigest()
    if len(generated_etag)> 17:
        return generated_etag[0:17]
    else:
        return generated_etag

def test():
    file_key1="11324234_file.mp3"
    hash_value1 = generateETagbyString(file_key1)
    print(hash_value1)
    print(type(hash_value1))

    file_key2 = "21324234_file.mp3"
    hash_value2 = generateETagbyString(file_key2)
    print(hash_value2)
    print(type(hash_value2))

if __name__=="__main__":
    test()