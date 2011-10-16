from lxml import html as lhtml
from lxml import etree
from lxml.html.clean import clean_html
import requests
from models import Amazon_Textbook_Section as ats, ATS_Middle, ProfitableBooks, MetaTable, Proxy, Book, Amazon, Price, AmazonRankCategory, AmazonRank
from django.db import IntegrityError
import re
from django.db.models import F
import tasks
from django.db import connection, transaction


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


def getAllKnownA():   
    foo = Price.objects.raw('SELECT id,amazon_id FROM ( SELECT *, row_number() over (partition by amazon_id order by timestamp DESC) r from ta_price ) x where r = 1 AND buy <> null')
    f = []
    for s in foo:
        f.append(s.amazon_id)
    tasks.process_lots_of_items(f) 
    
def importContent(url,content):
    html = lhtml.fromstring(content)
    a = ats(url=unicode(url).encode('ascii', 'ignore'),title = unicode(html.xpath("//*[@class='breadCrumb']")[0].text_content()).encode('ascii', 'ignore'))
    try:
        a.save()
    except IntegrityError:
        print 'Tried to save a dupe'
  
def createOrUpdateMetaField(keyvalue, value1):
    try:
        obj = MetaTable.objects.get(metakey=keyvalue)
    except MetaTable.DoesNotExist:
        obj = MetaTable(metakey=keyvalue,metatype="INTEGER")
    obj.int_field = value1
    obj.save()  

def updateBookCounts():  
    createOrUpdateMetaField("totalIndexed",Price.objects.values('amazon_id').distinct().count())
    createOrUpdateMetaField("totalBooks",Amazon.objects.count())
    createOrUpdateMetaField("totalProfitable",ProfitableBooks.objects.all().count())

def deleteExtraneousPricesWorker(objs):
    for obj in objs:
	    amz = Price.objects.filter(amazon=obj).order_by("-timestamp")
	    count = len(amz)
	    if count > 1:
	        for i in xrange(count-1,1,-1): 
	            if (amz[i-1].buy == amz[i-2].buy) and (amz[i-1].sell == amz[i-2].sell):
	                amz[i-1].delete()
        #for row in amz:
          #print "[%s] %s: buy %s sell %s at %s good for %s" % (row.id, row.amazon.productcode, row.buy, row.sell, row.timestamp, row.last_timestamp)

def deleteExtraneousPrices():
	objs = Amazon.objects.all().values_list("productcode",flat=True)
	process_lots_of_items_extra.delay(objs)   
	     
def addCategory(url):
    content = retrievePage(url,proxy=False)
    importContent(url,content)
    
def addProxy(type,proxy):
    p = Proxy(proxy_type=type,ip_and_port=proxy)
    p.save()
    
def getProfitableBooks():
    cursor = connection.cursor()
    cursor.execute("SELECT * from ta_price a WHERE NOT EXISTS ( SELECT * FROM ta_price b WHERE b.amazon_id = a.amazon_id AND b.timestamp > a.timestamp ) AND a.buy > a.sell AND a.timestamp > '2011-10-13 09:23:54-04';")
    rows = cursor.fetchall()
    cursor.execute("TRUNCATE ta_profitablebooks")
    transaction.commit_unless_managed()
    with transaction.commit_on_success():
     for f in iter(rows):
      obj = ProfitableBooks(price=Price.objects.get(pk=f[0]),buy=f[2],sell=f[3])
      obj.save()
     
def getTheMiddle():
    for cat in ats.objects.all():
                 for i in range(1,101):
                     ATS_Middle.objects.create(page=i,section=cat)
                     
def detailAllBooks():    
    objs = Amazon.objects.values_list('productcode', flat=True)
    tasks.process_lots_of_items(objs)
    
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
        

def lookForBooks():   
    objs = ATS_Middle.objects.values_list('id', flat=True)      
    process_lots_of_items_cats(objs) 
                     

def parseUsedPage(am):
    url = 'http://www.amazon.com/gp/offer-listing/%s/ref=dp_olp_used?ie=UTF8&condition=used' % (am.productcode)
    content = retrievePage(url)
    html = lhtml.fromstring(content)
    matches = re.search(r'Get a \$?(\d*\.\d{2}) Amazon.com Gift Card when you sell back your copy of this book.',html.text_content())
    buyprice = None
    if matches != None: 
        buyprice = matches.group(1)
        
    results = html.xpath("//tbody[@class='result']")
    
    for result in results:
        if re.search('Acceptable',result.cssselect('.condition')[0].text_content()):
            continue
        sellprice = re.match('\$?(\d*\.\d{2})',result.cssselect('.price')[0].text_content())
        if sellprice != None and buyprice != None:
            sellprice = sellprice.group(1)
            print sellprice
            print buyprice
            price = Price(buy = buyprice, sell = sellprice, amazon = am)
            price.save()
        else:
            price = Price(amazon = am)
            price.save()      
        #print result.cssselect('.condition')[0].text_content()
        break
         
     
def fetchPage(url):
    content = retrievePage(url)
    f = open('/virtualenvs/ta/ta/static/static/testing.html','w')
    f.write(content)
    f.close()
    
def testthis():
    url = 'http://www.amazon.com/gp/search/ref=sr_ex_n_1?rh=n%3A283155%2Cn%3A%2144258011%2Cn%3A2205237011%2Cn%3A5&bbn=2205237011&ie=UTF8&qid=1317397002'
    url2= 'http://www.amazon.com/Programming-Objective-C-3rd-Developers-Library/dp/0321711394/ref=sr_1_32?ie=UTF8&s=textbooks-trade-in&qid=1317401882&sr=1-32'
    
    for i in range(100):
    	tic(url,i)
    
if (__name__ == '__main__'):
    testit2()
