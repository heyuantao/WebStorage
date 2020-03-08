# -*- coding: utf-8 -*-
import hashlib
from collections import Iterable

#所有的参数都为字符串
class DownloadKeyCrypto:

    def __init__(self):
        pass

    #secret为预共享密钥,为一个单独的密钥
    def sign(self,key,realname,timestamp,secret):
        combined_str = key + realname + timestamp + secret
        combined_byte = combined_str.encode('utf-8')
        combined_hash =hashlib.md5(combined_byte).hexdigest()
        return combined_hash

    # secret为预共享密钥,可能是一个密钥也可以是一个密钥列表
    def valid(self,key,realname,timestamp,secret_or_secret_list,sign):
        if isinstance(secret_or_secret_list, list):
            for one_secret in secret_or_secret_list:
                combined_str = key + realname + timestamp + one_secret
                combined_byte = combined_str.encode('utf-8')
                combined_hash = hashlib.md5(combined_byte).hexdigest()
                if combined_hash ==sign:
                    return True
            return False
        else:
            combined_str = key + realname + timestamp + secret_or_secret_list
            combined_byte = combined_str.encode('utf-8')
            combined_hash = hashlib.md5(combined_byte).hexdigest()
            if combined_hash == sign:
                return True
            else:
                return False

downloadkeycrpyto = DownloadKeyCrypto()