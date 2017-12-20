import re
import urllib
import os
from flask import Flask
from flask import render_template, request, redirect, url_for
from pymystem3 import Mystem

Links = re.compile('<a class="uu" href="ru-index\.html\?l=.*?f=.*?">.*?<\/a>', re.DOTALL)
CleanLink = re.compile('<a class="uu" href="')
CleanLink1 = re.compile('">.*?<\/a>')
table_out = re.compile('<table cellpadding="3" cellspacing="0" border="0" style="border:1px dotted;border-color:#999999;">.*?<\/table>', re.DOTALL)
words_out = re.compile('<tr valign="top".*?<\/tr>')
modern_out = re.compile('')
cleanTag = re.compile('<.*?>', re.DOTALL)
addspace = re.compile('<td></td>')
addyati = re.compile('&#1123;')
addi = re.compile('&#1110;')
fiti = re.compile('&#1139;')
dotandcomma = re.compile('')
cleanstress = re.compile('\'')
Skopje = re.compile('<table><caption>Right Now</caption><tbody>.*?<\/tbody><\/table>', re.DOTALL)

def dict_parser(page_code, dorev_dict):
    table = table_out.findall(page_code)
    clean_table = addspace.sub(' ', table[0])
    clean_table = cleanTag.sub('', clean_table)
    clean_table = cleanstress.sub('', clean_table)
    clean_table = addblyati.sub('ѣ', clean_table)
    clean_table = addi.sub('і', clean_table)
    clean_table = fiti.sub('ѳ', clean_table)
    words_raw = clean_table.split('&nbsp;')
    words = []
    for i,el in enumerate(words_raw):
        if (el != '') and (len(el)>2) and (i>8):
            words.append(el.lower())
    for el in words:
        par = el.split()
        dorev_dict[par[0]] = par[1]
    

def dict_crowler():
    dorev_dict = {}
    for i in range (0,10):
        req = urllib.request.Request('http://www.dorev.ru/ru-index.html?l=c'+str(i))
        with urllib.request.urlopen(req) as response:
            page_code = response.read().decode('windows-1251')
            dict_parser(page_code, dorev_dict)
    letters = ['a','b','c','d','e','f']
    for i in range (0,6):
        req = urllib.request.Request('http://www.dorev.ru/ru-index.html?l=c'+letters[i])
        with urllib.request.urlopen(req) as response:
            page_code = response.read().decode('windows-1251')
            dict_parser(page_code, dorev_dict)
    for i in range (0,10):
        req = urllib.request.Request('http://www.dorev.ru/ru-index.html?l=d'+str(i))
        with urllib.request.urlopen(req) as response:
            page_code = response.read().decode('windows-1251')
            dict_parser(page_code, dorev_dict)
    for i in range (3,6):
        req = urllib.request.Request('http://www.dorev.ru/ru-index.html?l=d'+letters[i])
        with urllib.request.urlopen(req) as response:
            page_code = response.read().decode('windows-1251')
            dict_parser(page_code, dorev_dict)
    return dorev_dict

##dorev_dict = dict_crowler()

def transliterator(input_text):
    mystem = Mystem()
    analyzed = mystem.analyze(input_text)
    result_text = ''
    for word in analyzed:
        try:
            raw = word['text']
            lemma = word['analysis'][0]['lex']
            gr = word['analysis'][0]['gr']
            attr = gr.split('=')
            const = attr[0].split(',')
            unconst = attr[1].split(',')
        except:
            continue
        low_raw = raw.lower()
        if (const[0] == 'CONJ') or (const[0] == 'INTJ')or (const[0] == 'PART')or (const[0] == 'PR'):
            result_word = raw
        else:
            try:
                result_word = dorev_dict[low_raw]
                continue
            except:
                try:
                    dorev_lemma = dorev_dict[lemma]
                    result_word = ''
                    for i,letter in enumerate(low_raw):
                        if dorev_dict[lemma][i] == 'і':
                            result_word += 'і'
                        else:
                            if dorev_dict[lemma][i] == 'ѣ':
                                result_word += 'ѣ'
                            else:
                                if dorev_dict[lemma][i] == 'ѳ':
                                    result_word += 'ѳ'
                                else:
                                    result_word += letter                      
                    continue
                except:
                    result_word = raw  
        if raw[0] == '[А-Я]':
            result_word.capitalize()
        result_text += result_word
    return result_text

app = Flask(__name__)

@app.route('/')
def index():
    req = urllib.request.Request('https://weather.com/weather/today/l/42.00,21.43')
    with urllib.request.urlopen(req) as response:
        page_code = response.read().decode('utf-8')
        weather = Skopje.findall(page_code)
        weather_data = cleanTag.sub(' ', weather[0])
    return render_template('index.html', weather = weather_data)

@app.route('/pagetranslit')
def pagetranslit():
    req = urllib.request.Request('https://lenta.ru/')
    with urllib.request.urlopen(req) as response:
        page_code = response.read().decode('utf-8')
        input_text = cleanTag.sub('', page_code)
        result_text = transliterator(input_text)
    return render_template('pagetranslit.html', result = result_text)

@app.route('/result', methods=['GET', 'POST'])
def result():
    input_string_raw = request.args.get('input_word')
    input_string = input_string_raw.lower()
    result_text = transliterator(input_string)
    return render_template('result.html', result = result_text)

if __name__ == '__main__':
    app.run()
