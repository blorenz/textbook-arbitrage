from lxml import html as lhtml
from lxml import etree
from lxml.html.clean import clean_html
import requests
from models import Amazon_Textbook_Section as ats, Proxy, Book, Amazon, Price, AmazonRankCategory, AmazonRank
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
        theProxy = Proxy.objects.order_by('?')[0]
        proxy = {theProxy.proxy_type:theProxy.ip_and_port}
        r = requests.get(url,proxies=proxy)
    else:
        r = requests.get(url)
    return r.content


def importContent(url,content):
    html = lhtml.fromstring(content)
    a = ats(url=unicode(url).encode('ascii', 'ignore'),title = unicode(html.xpath("//*[@class='breadCrumb']")[0].text_content()).encode('ascii', 'ignore'))
    try:
        a.save()
    except IntegrityError:
        print 'Tried to save a dupe'
      
def addCategory(url):
    content = retrievePage(url,proxy=False)
    importContent(url,content)
    
def addProxy(type,proxy):
    p = Proxy(proxy_type=type,ip_and_port=proxy)
    p.save()
                
def findBooks(url,page):
    content = retrievePage(url + '&page=' + str(page))
    html = lhtml.fromstring(content)
    section = ats.objects.get(url=url)
    for table in html.xpath("//table[@class='n2']"):
        aa = table.cssselect("td.dataColumn a")
        title = table.cssselect(".srTitle")
        re_product_code = re.compile(r'/dp/(.*?)/')
        pc = re.findall(re_product_code,aa[0].get('href'))
        
        b = Book.objects.filter(pckey=pc)
        
        if len(b) == 0:
            b = Book(pckey=pc,section = section, title = unicode(title[0].text).encode('ascii', 'ignore'))
            try:
                b.save()
            except IntegrityError:
                print 'Tried to save a dupe 1'
        else:
            b = b[0]
          
        s = Amazon(book = b,productcode=pc[0])
        try:
            s.save()
        except IntegrityError:
            print 'Tried to save a dupe 2'
        
def detailBook(am):
    '''Grabs the details of a book page including Buy, Sell, Rank, ISBN'''
    content = retrievePage('http://www.amazon.com/dp/' + am.productcode)
    html = lhtml.fromstring(content)
    s = html.xpath("//div[@class='qpHeadline']/..")
    ###sqlQuery = "SELECT * FROM ( SELECT *, row_number() over (partition by amazon_id order by timestamp DESC) r from ta_price ) x where r = 1 AND amazon_id = '" + am.productcode + "' LIMIT 1";
    ###foo = Price.objects.raw(sqlQuery)
    if len(s):
        parseThis = s[0].text_content()
        money = re.compile(r'\$?(\d*\.\d{2})')#e.g., $.50, .50, $1.50, $.5, .5
        matches = re.findall(money, parseThis)
        if len(matches) >= 2:
            price = Price(buy = matches[0], sell = matches[1], amazon = am)
            price.save()
            #print "Ranked"
            #print("Price buy %s and sell %s for %s" % (matches[0],matches[1],am.book.title))
    else:
        price = Price(amazon = am)
        print "not Ranked"
        price.save()
    	
    s = html.xpath("//td[@class='bucket']/div[@class='content']/ul/li")
    rankCategory = "None"
    rankNoComma = "0"
    
    for t in s:
        i = t.xpath("script")
        for j in i:
            t.remove(j)
        #for u,t in enumerate(s):
        txt = t.text_content().strip()
        
        matches = re.match(r'ISBN-10: ([\d\w]+)',txt)
        if matches != None:
            am.book.isbn10 = matches.group(1)
       
        matches = re.match(r'ISBN-13: ([-\d\w]+)',txt)
        if matches != None:
            am.book.isbn = matches.group(1)
        
        matches = re.match(r'Amazon Best Sellers Rank:\s+#([,\d]+) in ([\w\s]+) \(',txt)
        if matches != None:
            rankNoComma = re.sub(",","",matches.group(1))
            rankCategory = matches.group(2)
                
    print ("ISBN %s and IBSN-10 %s and rank is %s in %s" % (am.book.isbn, am.book.isbn10, rankNoComma, rankCategory))
    am.book.save() 
    arc = AmazonRankCategory.objects.filter(category = rankCategory)
    if len(arc) == 0:
        arc = AmazonRankCategory(category=rankCategory)
        arc.save()
    else:
        arc = arc[0]
    #print arc
    ar = AmazonRank(amazon = am, rank = int(rankNoComma), category = arc)
    ar.save()
        
'''
   New Detail book:
   
   if div#more-buying-choice-content-div
   if children divs == 3
     parse first-child with span.price
     parse third-child with div 2 span
'''
#//div[contains(concat(' ',normalize-space(@class),' '),' result')]
def countBooksInCategory(url):
    '''Counts how may books are in each category, to intelligently scrape the 
	correct number of pages.'''
    content = retrievePage(url)
    html = lhtml.fromstring(content)
    st = open('/virtualenvs/ta/ta/static/static/testing.html','w')
    st.write(content)
    st.close()
    
    s = html.xpath("//td[@class='resultCount']")
    resultsNoComma = 0
  
    if len(s):
        txt = s[0].text_content().strip()
        print txt 
        matches = re.search(r'of\s+([,\d]+) Results',txt)
        
        if matches != None:
            resultsNoComma = re.sub(",","",matches.group(1))
            
    return resultsNoComma
    
def getBooksOnTradeinPage(url,page):
    '''Gets all the books on the tradein page'''
    content = retrievePage(url + "page=" + str(page))
    html = lhtml.fromstring(content)
    #st = open('/virtualenvs/ta/ta/static/static/testing.html','w')
    #st.write(content)
    #st.close()
    
    s = html.xpath("//div[contains(concat(' ',normalize-space(@class),' '),' result ')]")
  
    for result in s:
        aa = table.cssselect("td.dataColumn a")
        title = table.cssselect(".srTitle")
        re_product_code = re.compile(r'/dp/(.*?)/')
        pc = re.findall(re_product_code,aa[0].get('href'))
        
        b = Book.objects.filter(pckey=pc)
        
        if len(b) == 0:
            b = Book(pckey=pc,section = section, title = unicode(title[0].text).encode('ascii', 'ignore'))
            try:
                b.save()
            except IntegrityError:
                print 'Tried to save a dupe 1'
        else:
            b = b[0]
          
        s = Amazon(book = b,productcode=pc[0])
        try:
            s.save()
        except IntegrityError:
            print 'Tried to save a dupe 2'
        
def tic(url,page):  
    '''Gets all the books on the tradein page'''
    print 'Going to page: ' + str(page)
    content = retrievePage(url + "&page=" + str(page))
    html = lhtml.fromstring(content)
    st = open('/virtualenvs/ta/ta/static/static/testing.html','w')
    st.write(content)
    st.close()
    
    s = html.xpath("//table[@class='n2']")
  
    for table in s:
        aa = table.cssselect("td.dataColumn a")
        title = table.cssselect(".srTitle")
        re_product_code = re.compile(r'/dp/(.*?)/')
        pc = re.findall(re_product_code,aa[0].get('href'))
        
        print pc[0] + "  : " +  title[0].text
        
        
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
    s = html.xpath("//td[@class='bucket']/div[@class='content']/ul/li")
    for t in s:
        i = t.xpath("script")
        for j in i:
            t.remove(j)
        for u,t in enumerate(s):
            txt = t.text_content().strip()
            matches = re.match(r'ISBN-10: ([\d\w]+)',txt)
            if matches != None:
                print matches.group(1)
            matches = re.match(r'ISBN-13: ([-\d\w]+)',txt)
            if matches != None:
                    print matches.group(1)
            matches = re.match(r'Amazon Best Sellers Rank:\s+#([,\d]+) in [\w\s]+ \(',txt)
            if matches != None:
                    print matches.group(1)

def testit2():
    url = 'http://www.amazon.com/Organizational-Behavior-Robert-Kreitner/dp/007353045X/ref=pd_sim_b6'
    content = retrievePage(url)
    html = lhtml.fromstring(content)
    f = open('/tmp/text.html', 'w')
    f.write(content)
    f.close()
    s = html.xpath("//td[@class='bucket']/div[@class='content']/ul/li")
    for t in s:
	i = t.xpath("script")
	for j in i:
		t.remove(j)
    for u,t in enumerate(s):
	txt = t.text_content().strip()
	matches = re.match(r'ISBN-10: ([\d\w]+)',txt)
	if matches != None:
		print matches.group(1)
	matches = re.match(r'ISBN-13: ([-\d\w]+)',txt)
        if matches != None:
                print matches.group(1)
	matches = re.match(r'Amazon Best Sellers Rank:\s+#([,\d]+) in [\w\s]+ \(',txt)
        if matches != None:
                print matches.group(1)
        
        
#    if len(s):
#        parseThis = s[0].text_content()
#        money = re.compile(r'\$?(\d*\.\d{2})')#e.g., $.50, .50, $1.50, $.5, .5
#        print parseThis
#        matches = re.findall(money, parseThis)
#        print matches
#        if len(matches) >= 2:
#            print matches[0]
#            print matches[1]
           

def testthis():
    url = 'http://www.amazon.com/gp/search/ref=sr_ex_n_1?rh=n%3A283155%2Cn%3A%2144258011%2Cn%3A2205237011%2Cn%3A5&bbn=2205237011&ie=UTF8&qid=1317397002'
    url2= 'http://www.amazon.com/Programming-Objective-C-3rd-Developers-Library/dp/0321711394/ref=sr_1_32?ie=UTF8&s=textbooks-trade-in&qid=1317401882&sr=1-32'
    
    for i in range(100):
    	tic(url,i)
    
if (__name__ == '__main__'):
    testit2()
