#-*- coding:utf-8 -*-
#from googletrans import Translator
import os
import _thread
import shutil

import http.client
import hashlib
import urllib
import urllib.request
import random
import json
import multiprocessing

import sys
typ = sys.getfilesystemencoding()

# reload(sys)
# sys.setdefaultencoding( "utf-8" )
#
# translator = Translator()
# print(translator.translate('今天天气不错', dest='ja').text)


appid = '20180921000210513' #你的appid
secretKey = 'uoej6WaG7nTURSZw5tHW' #你的密钥

pool=multiprocessing.Pool(processes=10)#限制并行进程数为3

def transbaidu(querystr, to_l="zh", from_l="en"):

    httpClient = None
    myurl = '/api/trans/vip/translate'
    q = querystr
    fromLang = from_l
    toLang = to_l
    salt = random.randint(32768, 65536)

    sign = appid + q + str(salt) + secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode(encoding='UTF-8'))
    sign = m1.hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.request.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        bytes = response.read()
        rs = bytes.decode(encoding='utf-8')
        rs = (json.loads(rs)['trans_result'][0])['dst']
        print(rs)
        return rs
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()

def wirtefile(path, content):
    """
    写入文件
    """
    with open(path, 'w') as f:
            # str_content = content.replace(u'\xa9', u'')
            f.write(content)
            f.close()

def readfile(path):
    """
    读取文件
    """
    file_path_no_ext, file_extension = os.path.splitext(path)
    with open(path, 'r') as f:
        content = f.read()
        f.close()
        content = parseTrans(content)
        #file_path_no_ext += '_bak.php'
        wirtefile(path, content)

def translate(querystr, to_l="zh", from_l="en"):
    '''for google tranlate by doom
    '''
    C_agent = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.165063 Safari/537.36 AppEngine-Google."}
    flag = 'class="t0">'
    tarurl = "http://translate.google.com/m?hl=%s&sl=%s&q=%s \
        " % (to_l, from_l, querystr.replace(" ", "+"))
    request = urllib.request.Request(tarurl, headers=C_agent)
    page = str(urllib.request.urlopen(request).read().decode(typ))
    target = page[page.find(flag) + len(flag):]
    target = target.split("<")[0]
    return target


def parseTrans(content):
    if content is None:
        return
    contentnew = ''
    rows = str.split(content,'\n')
    for line in rows:
        try:
            print('reading line: '+line)
            kvs = str.split(line,'=')
            if kvs and len(kvs) == 2:
                key = kvs[0]
                value = kvs[1]
                #print(value)
                if len(value) > 3:
                    value = value[2:len(value)-2] #remove front end ';
                    print('translate ...  ' + value)
                    value =  transbaidu(value) #translate(value)
                    if len(value) > 0:
                        print('translateend:' + value)
                        linenew = "{0}    =   '{1}';\n".format(key,value)
                        contentnew += linenew
                        pass
            else:
                contentnew += line + '\n'
                pass
        except Exception as e:
            print(e)
            pass

    return contentnew

def parselanguage(filePath='/Users/tansheng/Documents/git/opencart_language/admin', lancode = 'zh'):
    #'/Users/tansheng/Documents/web/3.0.2.0-OpenCart/upload/admin/language/en-gb/catalog/attribute_group.php'
    if os.path.isfile(filePath):
        file_path_no_ext, file_extension = os.path.splitext(filePath)
        if file_extension == '.php':
            readfile(filePath)
    elif os.path.exists(filePath):
        print('parse dir:'+ filePath)
        for fileName in os.listdir(filePath):
            fullpath = os.path.join(filePath, fileName)
            if fileName == 'language' and os.path.isdir(fullpath):
                path = fullpath
                langdircopy = ''
                for langdir in os.listdir(path):
                    if langdir == lancode:
                        fileNameLanguageDir = os.path.join(path, lancode)
                        shutil.rmtree(fileNameLanguageDir)
                    pass
                for langdir in os.listdir(path):
                    if langdir != lancode and os.path.isdir(os.path.join(path, langdir)):
                        langdircopy = os.path.join(path, lancode)
                        shutil.copytree(os.path.join(path, langdir), langdircopy)
                        break
                    pass
                if langdircopy and len(langdircopy) > 0:
                    parselanguagefile(langdircopy)
            elif os.path.isdir(fullpath):
                parselanguage(fullpath)

    pass

def parselanguagefile(filePath):
    if os.path.isfile(filePath):
        file_path_no_ext, file_extension = os.path.splitext(filePath)
        if file_extension == '.php':
            print('languagefile:'+filePath)
            args = [filePath]
            #_thread.start_new_thread(readfile,tuple(args))
            readfile(filePath)
            #pool.map(self.readfile, args)
    elif os.path.exists(filePath):
        print('parse language dir:' + filePath)
        for fileName in os.listdir(filePath):
            fullpath = os.path.join(filePath, fileName)
            parselanguagefile(fullpath)

if __name__ == "__main__":
    #filePath = sys.argv[1]
    parselanguage()

