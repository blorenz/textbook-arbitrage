from lxml import html as lhtml
import requests
from models import Amazon_Textbook_Section as ats, Proxy, Book, Amazon, Price
from django.db import IntegrityError
import re

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def difference(a, b):
    return list(set(b).difference(set(a))) 

def retrievePage(url,proxy=None):
    if (proxy):
        theProxy = Proxy.objects.order_by('?')[0];
        proxy = {theProxy.proxy_type:theProxy.ip_and_port}
    r = requests.get(url,proxies=proxy)
    return r.content


def importContent(url,content):
    html = lhtml.fromstring(content)
    a = ats(url=unicode(url).encode('ascii', 'ignore'),title = unicode(html.xpath("//*[@class='breadCrumb']")[0].text_content()).encode('ascii', 'ignore'))
    try:
        a.save()
    except IntegrityError:
        print 'Tried to save a dupe'
      
def addCategory(url):
    content = retrievePage(url,proxy=True)
    importContent(url,content)
    
def addProxy(type,proxy):
    p = Proxy(proxy_type=type,ip_and_port=proxy)
    p.save()
    
def findBooksWithPage(url):
    content = retrievePage(url)
    urlWithoutPage = re.sub(r'&page=\d{1,3}','',url)
    html = lhtml.fromstring(content)
    section = ats.objects.get(url=urlWithoutPage)
    for table in html.xpath("//table[@class='n2']"):
        aa = table.cssselect("td.dataColumn a")
        title = table.cssselect(".srTitle")
        b = Book(section = section, title = unicode(title[0].text).encode('ascii', 'ignore'))
        #,url=aa[0].get('href')
        #b.save()
        try:
            b.save()
        except IntegrityError:
            print 'Tried to save a dupe 1'
        re_product_code = re.compile(r'/dp/(.*?)/')
        pc = re.findall(re_product_code,aa[0].get('href'))
        s = Amazon(book = b,productcode=pc[0],rank=0)
        try:
            s.save()
        except IntegrityError:
            print 'Tried to save a dupe 2'
                
def findBooks(url,page):
    content = retrievePage(url + '&page=' + str(page))
    html = lhtml.fromstring(content)
    section = ats.objects.get(url=url)
    for table in html.xpath("//table[@class='n2']"):
        aa = table.cssselect("td.dataColumn a")
        title = table.cssselect(".srTitle")
        b = Book(section = section, title = unicode(title[0].text).encode('ascii', 'ignore'))
        #,url=aa[0].get('href')
        #b.save()
        try:
            b.save()
        except IntegrityError:
            print 'Tried to save a dupe 1'
        re_product_code = re.compile(r'/dp/(.*?)/')
        pc = re.findall(re_product_code,aa[0].get('href'))
        s = Amazon(book = b,productcode=pc[0],rank=0)
        try:
            s.save()
        except IntegrityError:
            print 'Tried to save a dupe 2'
        
def detailBook(am):  
    content = retrievePage('http://www.amazon.com/dp/' + am.productcode)
    html = lhtml.fromstring(content)
    s = html.xpath("//div[@class='qpHeadline']/..")
    if len(s):
        parseThis = s[0].text_content()
        money = re.compile(r'\$?(\d*\.\d{2})')#e.g., $.50, .50, $1.50, $.5, .5
        matches = re.findall(money, parseThis)
        if len(matches) >= 2:
            price = Price(buy = matches[0], sell = matches[1], amazon = am)
            price.save()
        

def testit():
    url = 'http://www.amazon.com/Organizational-Behavior-Robert-Kreitner/dp/007353045X/ref=pd_sim_b6'
    content = retrievePage(url)
    html = lhtml.fromstring(content)
    s = html.xpath("//div[@class='qpHeadline']/..")
    if len(s):
        parseThis = s[0].text_content()
        money = re.compile(r'\$?(\d*\.\d{2})')#e.g., $.50, .50, $1.50, $.5, .5
        print parseThis
        matches = re.findall(money, parseThis)
        print matches
        if len(matches) >= 2:
            print matches[0]
            print matches[1]

    
def testthis2(url,i):
    url = 'http://www.amazon.com/gp/search/ref=sr_nr_n_0?rh=n%3A283155%2Cn%3A%212349030011%2Cn%3A465600%2Cn%3A468220%2Cn%3A491564&bbn=468220&ie=UTF8&qid=1316294420&rnid=468220'
    findBooks(url,i)

def testthis():
    url = 'http://www.amazon.com/gp/search/ref=sr_nr_n_0?rh=n%3A283155%2Cn%3A!2349030011%2Cn%3A465600%2Cn%3A468220%2Cn%3A491564&bbn=468220&ie=UTF8&qid=1316313331&rnid=468220'
    content = retrievePage(url)
    print content
    f = open('/tmp/text.html', 'w')
    f.write(content)
    f.close()
    html = lhtml.fromstring(content)
    a = ats(url=unicode(url).encode('ascii', 'ignore'),title = unicode(html.xpath("//*[@class='breadCrumb']")[0].text_content()).encode('ascii', 'ignore'))
    try:
        a.save()
    except IntegrityError:
        print 'Tried to save a dupe'
    
if (__name__ == '__main__'):
    testit()