
import hashlib
def get_hash_value(in_str, in_digest_bytes_size=64, in_return_type='digest'):
    """해시값을 구한다 
    Parameter: in_str: 해싱할문자열, in_digest_bytes_size: Digest바이트크기, 
               in_return_type: 반환형태(digest or hexdigest or number) """
    assert 1 <= in_digest_bytes_size and in_digest_bytes_size <= 64
    blake  = hashlib.blake2b(in_str.encode('utf-8'), digest_size=in_digest_bytes_size)
    if in_return_type == 'hexdigest': return blake.hexdigest()
    elif in_return_type == 'number': return int(blake.hexdigest(), base=16)
    return blake.digest()
