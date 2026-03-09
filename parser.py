import re
import os
from urllib import request
from bs4 import BeautifulSoup


class parser:
    def __init__(self):
        page = self.fetchPage()
        self.n, self.e = self.parseNumbers(page)
        self.date = self.parseDate(page)

    def getDate(self):
        if self.date is None:
            return None
        return self.date

    def getNumbers(self):
        if self.n is None:
            return None
        if len(self.n) != 7:
            return None
        return self.n

    def getExtraNumbers(self):
        if self.e is None:
            return None
        if len(self.e) != 1:
            return None
        return self.e

    def fetchPage(self):
        with request.urlopen("https://yle.fi/tekstitv/txt/471_0001.htm") as f:
            return f.read().decode("utf-8")

    def parseDate(self, page):
        if page is None:
            print ("page is None")
            return None
        soup = BeautifulSoup(page, 'html.parser')
        resDiv = soup.findAll('div', {'class': 'boxbox'})
        if len(resDiv) != 1:
            print ("page does not contain <div class='boxbox'> element")
            return None
        preDiv = resDiv[0].findAll('pre')
        if len(preDiv) != 1:
            print ("One <pre> element should be found")
            return None
        #23.8.2025 KIERROS 34
        p = re.compile('\d{1,2}.\d{1,2}.\d{4}')
        matches = p.findall(preDiv[0].text)
        if len(matches) == 0:
            print ("could not find date in span", preDiv[1].text)
            return None
        return self.toDateStr(matches[0])

    def toDateStr(self, date):
        p = re.compile('\d+')
        matches = p.findall(date)
        if len(matches) != 3:
            return None
        if int(matches[0]) < 10:
            day = '0' + str(matches[0])
        else:
            day = str(matches[0])
        if int(matches[1]) < 10:
            month = '0' + str(matches[1])
        else:
            month = str(matches[1])
        year = str(matches[2])
        return year + '-' + month + '-' + day

    def parseNumbers(self, page):
        if page is None:
            print ("page is None")
            return None, None
        soup = BeautifulSoup(page, 'html.parser')
        resDiv = soup.findAll('div', {'class': 'boxbox'})
        if len(resDiv) != 1:
            print ("page does not contain <div class='boxbox'> element")
            return None, None
        preDiv = resDiv[0].findAll('pre')
        if len(preDiv) != 1:
            print ("One <pre> element should be found")
            return None, None
        #OIKEAT NUMEROT: 6,11,12,13,25,30,33
        p = re.compile('OIKEAT NUMEROT: \d{1,2},\d{1,2},\d{1,2},\d{1,2},\d{1,2},\d{1,2},\d{1,2}')
        matches = p.findall(preDiv[0].text)
        if len(matches) != 1:
            print ("could not find numbers in text", preDiv[0].text)
            return None
        numbers = matches[0][16:]
        n = [int(elem) for elem in numbers.split(',')]
        #LISÄNUMERO: 34
        p = re.compile('LIS.NUMERO: \d{1,2}')
        matches = p.findall(preDiv[0].text)
        if len(matches) != 1:
            Sprint ("could not fina extre number in text", preDiv[0].text)
            return None
        extranumber = matches[0][12:]
        e = [int(elem) for elem in extranumber.split(',')]
        return n, e
