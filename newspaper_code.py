import urllib.request
import re
import os
import shutil

##регулярки для поиска url, названия и даты
regExtractItems = re.compile('<div class="newspaper">.*?<div class="k2Pagination">', re.DOTALL)
regUrlTitle = re.compile('<h3 class="catItemTitle">.*?</h3>', re.DOTALL)
regDate = re.compile('[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9][0-9]', re.DOTALL)

##регулярки для очистки лишнего
cleanTag = re.compile('<.*?>', re.DOTALL)
cleanUrlTitle = re.compile('\t\t\t<a href="', re.DOTALL)
cleanUrlTitle2 = re.compile('\t  \t</a>\n\t  \t\t  </h3>', re.DOTALL)
cleanNotASCII = re.compile('[&nbsp;]|[&laquo;]|[&raquo;]|[&mdash;]', re.DOTALL)
cleanLines = re.compile('\n')
cleanSlash = re.compile('/', re.DOTALL)

##регулярки для обработки текста новости
regExtractText = re.compile('<div class="itemFullText ftt">.*?</div>', re.DOTALL)
changePlain = re.compile('plain', re.DOTALL)

def crowler():
    for page_num in range(0,13,12): ## заменить среднее число (13) на 25969
        req = urllib.request.Request('http://www.elabuga-rt.ru/ru/the-news.html?start=' + str(page_num))
        try:
            with urllib.request.urlopen(req) as response:
               page_code = response.read().decode('utf-8')
               dictDB = createDict(page_code)
               article_processing(dictDB)
        except:
            print('could not process page')
           

def createDict(page_code): ##ключи словаря - ссылки на статьи, значения - массив с инф-ей о статье 0)название 1)полная дата 2)год 3)месяц
    allItems = regExtractItems.findall(page_code)
    dictDB = {}
    for el in allItems:
        UrlTitle = regUrlTitle.findall(el)
        Date = regDate.findall(el)
        for index, url in enumerate(UrlTitle):
            strUrlTitle = str(UrlTitle[index])
            splitUrlTitle = strUrlTitle.split('">')
            strUrl = cleanUrlTitle.sub('', str(splitUrlTitle[1]))
            strTitle = cleanUrlTitle2.sub('', str(splitUrlTitle[2]))          
            strDate = str(Date[index])
            splitDate = strDate.split('.')
            dictDB[strUrl] = [strTitle, strDate, splitDate[2], splitDate[1]]
    return dictDB

def article_processing(dictDB):
    for url in dictDB:
        req = urllib.request.Request('http://www.elabuga-rt.ru/' + url)
        try:
            with urllib.request.urlopen(req) as response:
               article_code = response.read().decode('utf-8')
               text = regExtractText.findall(article_code)
               strText = str(text[0])
               strText = cleanTag.sub('', strText)
               strText = cleanNotASCII.sub('', strText)
               strText = cleanLines.sub(' ', strText)
               dest, filename = record(strText, dictDB[url], url)
               mystemmer(dest,filename)
        except:
            print('Could not extract text')


def record(strText, data, url):
    dest = os.path.join('plain', data[2], data[3])
    filename = cleanSlash.sub('', url)
    filename = filename + '.txt'
    if os.path.exists(dest) != True:
        os.makedirs(dest)
    with open(os.path.join(dest, filename), 'w', encoding = 'utf-8') as file:
        file.write(strText)
    with open('metadata.csv', 'a', encoding = 'utf-8') as meta:
        path = os.path.join(dest, filename)
        meta.write(path +'	author	sex	birthday	'+data[0]+'	'+data[1]+'	публицистика	genre_fi	type	topic	chronotop	нейтральный	н-возраст	н-уровень	районная	'+'http://www.elabuga-rt.ru/'+url+'	'+'Новая Кама'+'	publisher	'+data[2]+'	газета	Россия	Елабуга	ru')
    return dest, filename

def mystemmer(dest, filename):
    listFilename = filename.split('.')
    outputPlainMystem = changePlain.sub('mystem-plain', dest)
    outputXMLMystem = changePlain.sub('mystem-xml', dest)
    if os.path.exists(outputPlainMystem) != True:
        os.makedirs(outputPlainMystem)
    if os.path.exists(outputXMLMystem) != True:
        os.makedirs(outputXMLMystem)
    os.system('C:\mystem.exe ' + os.path.join(dest,filename) + ' ' + os.path.join(outputPlainMystem, listFilename[0]))
    os.system('C:\mystem.exe --format xml ' + os.path.join(dest,filename) + ' ' + os.path.join(outputXMLMystem, listFilename[0]))
    
     
crowler()
        
        
        
        
