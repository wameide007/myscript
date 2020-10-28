import time,json,base64,hmac,requests
from urllib import parse

AccessKeyID='xxx'
AccessKeySecret = 'xxx'
url='https://cr.cn-hangzhou.aliyuncs.com/repos/xxx/pos/tags?Page=1&PageSize=10'
url_para=(parse.urlparse(url))


def get_canon_headers(headers):
    canon_keys = []
    for k in headers:
        if k.startswith('x-acs-'):
            canon_keys.append(k)
    canon_keys = sorted(canon_keys)
    canon_header = ''
    for k in canon_keys:
        canon_header += '%s:%s\n' %(k, headers[k])
    return canon_header

def get_signature(AccessKeySecret,Content_Type,Date,headers,canon_resource):
    canon_headers = get_canon_headers(headers)
    #sign_string=method+'\n'+accept+'\n'+content_md5+'\n'+content_type+'\n'+date+'\n'+CanonicalizedHeaders+CanonicalizedResource
    sign_string='%s\n%s\n%s\n%s\n%s\n%s%s' %('GET',Content_Type,'','',Date,canon_headers,canon_resource)
    # sign_hmac=hmac.new(AccessKeySecret.encode('utf-8'),sign_string.encode('utf-8'),'sha1')
    # signature =base64.b64encode(signature_hmac.digest()).decode('utf-8')
    sign_hmac=hmac.new(bytes(AccessKeySecret,'utf-8'), bytes(sign_string,'utf-8'),'sha1')
    signature=base64.encodebytes(sign_hmac.digest()).strip().decode('utf-8')
    return signature

def get_headers(AccessKeyID,AccessKeySecret,url):
    canon_resource = parse.urlparse(url).path+'?'+parse.urlparse(url).query
    Content_Type = 'application/json'
    Date=time.strftime('%a, %d %b %Y %H:%M:%S GMT',time.gmtime())
    headers = {
        'Date': Date,
        'Accept': Content_Type,
        'x-acs-signature-method': 'HMAC-SHA1',
        'x-acs-signature-version': '1.0',
        'x-acs-version': '2016-06-07'
    }
    signature=get_signature(AccessKeySecret,Content_Type,Date,headers,canon_resource)
    headers['Authorization'] = 'acs '+AccessKeyID+":"+signature
    return headers

def get_namespace(AccessKeyID,AccessKeySecret,url):
    headers=get_headers(AccessKeyID,AccessKeySecret,url)
    rsp = requests.get(url, headers=headers)
    namespaces=json.loads(rsp.text)['data']['namespaces']
    return namespaces


headers=get_headers(AccessKeyID,AccessKeySecret,url)
rsp = requests.get(url, headers=headers)
print (rsp.status_code)
print (rsp.text)
