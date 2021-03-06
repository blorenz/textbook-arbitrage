from lxml import html as lhtml
import requests
from models import AmazonMongoTradeIn, Amazon_Textbook_Section_NR, Amazon_NR, Price_NR, Book_NR, ProfitableBooks_NR, MetaTable_NR
import re
import tasks
#import chilkat
# JINGWEMAILQ_tp6gXy5G9RoQ - mail

'''def mail():
    #  The mailman object is used for receiving (POP3)
    #  and sending (SMTP) email.
    mailman = chilkat.CkMailMan()

    #  Any string argument automatically begins the 30-day trial.
    success = mailman.UnlockComponent("JINGWEMAILQ_tp6gXy5G9RoQ")
    if (success != True):
        print "Component unlock failed"
        sys.exit()

    #  Set the GMail account POP3 properties.
    mailman.put_MailHost("pop.gmail.com")
    mailman.put_PopUsername("michaelbamazon")
    mailman.put_PopPassword("colonel1")
    mailman.put_PopSsl(True)
    mailman.put_MailPort(995)

    #  Read mail headers and one line of the body.
    #  To get the full emails, call CopyMail instead (no arguments)
    # bundle is a CkEmailBundle
    bundle = mailman.CopyMail()

    if (bundle == None ):
        print mailman.lastErrorText()
        sys.exit()

    s = 0
    print str(bundle.get_MessageCount())
    for i in range(0,bundle.get_MessageCount()):
        # email is a CkEmail
        email = bundle.GetEmail(i)
        #  Display the From email address and the subject.
        matches = re.findall("Amazon", email.ck_from())
        if len(matches):
            print email.ck_from()
            s += 1


def f7(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]

def difference(a, b):
    return list(set(b).difference(set(a)))
'''


def getROI(theBuy, theSell):
    theBuy = float(theBuy)
    theSell = float(theSell)
    actb = (theBuy - (theSell + 3.99)) / (theSell + 3.99)
    actb = round(actb * 100, 2)
    return actb


def isGoodProfit(obj):
    theBuy = float(obj.latest_price.buy)
    theSell = float(obj.latest_price.sell)
    actb = (theBuy - (theSell + 3.99)) / (theSell + 3.99)
    actb = round(actb * 100, 2)
    if actb >= 50.0:
        return True
    return False


def retrievePage(url, proxy=None):

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.66 Safari/535.11", }

    '''if (proxy):
        theProxy = Proxy.objects.order_by('?')[0]
        proxy = {theProxy.proxy_type:theProxy.ip_and_port}
        r = requests.get(url,proxies=proxy,headers=headers)
    else:'''
    r = requests.get(url, headers=headers)
    return r.content


def toAscii(content):
    return unicode(content).encode('ascii', 'ignore')


def createOrUpdateMetaField(keyvalue, value1):
    try:
        obj = MetaTable_NR.objects.get(metakey=keyvalue)
    except MetaTable_NR.DoesNotExist:
        obj = MetaTable_NR(metakey=keyvalue, metatype="INTEGER")
    obj.int_field = value1
    obj.save()


def updateBookCounts():
    createOrUpdateMetaField("totalIndexed", AmazonMongoTradeIn.objects.count())
    createOrUpdateMetaField("totalBooks", AmazonMongoTradeIn.objects.count())
    createOrUpdateMetaField("totalProfitable", ProfitableBooks_NR.objects.all().count())


'''def addProxy(type, proxy):
    p = Proxy(proxy_type=type, ip_and_port=proxy)
    p.save()'''

# thread = ta.models.AmazonMongo.objects.get().fields(slice__prices=-1)


def checkProfitable(a):
    print a
    price = a.prices[-1]
    if price.buy:
        if price.buy > price.sell:
            b = ProfitableBooks_NR()
            b.amazon = a.amazon
            b.price = price
            b.timestamp = price.timestamp
            b.save()


def getProfitableBooks():
    AmazonMongoTradeIn.objects.all().delete()
    objs = AmazonMongoTradeIn.objects.values_list('id', flat=True)
    tasks.process_lots_of_items_profitable.delay(objs)


def detailAllBooks():
    objs = AmazonMongoTradeIn.objects.values_list('id', flat=True)
    print 'Objs len is %d' % (len(objs),)
    print 'ok done with that'
    tasks.process_lots_of_items(objs)


'''
   New Detail book:

   if div#more-buying-choice-content-div
   if children divs == 3
     parse first-child with span.price
     parse third-child with div 2 span
'''
#//div[contains(concat(' ',normalize-space(@class),' '),' result')]


def countBooksInCategory(url):
    '''Counts how may books are in each category, to intelligently scrape the correct number of pages.'''
    content = retrievePage(url)
    html = lhtml.fromstring(content)
    #st = open('/virtualenvs/ta/ta/static/static/testing.html','w')
    #st.write(content)
    #st.close()

    s = html.xpath("//div[@id='resultCount']")
    resultsNoComma = 0

    if len(s):
        txt = s[0].text_content().strip()
        #print txt
        matches = re.search(r'of\s+([,\d]+) Results', txt)

        if matches != None:
            resultsNoComma = re.sub(",", "", matches.group(1))

    return resultsNoComma


# Edited on Apr27
def getBooksOnTradeinPage(url, page):
    '''Gets all the books on the tradein page'''
    print ('Getting books for ' + url + '&page=' + str(page))
    content = retrievePage(url + "&page=" + str(page))
    html = lhtml.fromstring(content)

#    file = open('/tmp/testing.html','w')
#    file.write(content)
#    file.close()

    listview = html.xpath("//div[@class='listView']")

    #s = html.xpath("//td[@class='dataColumn']")

    s = listview[0].xpath("//div[contains(concat(' ',normalize-space(@class),' '),' product ')]")
    for result in s:
        aa = result.cssselect("a")
        title = result.cssselect(".productTitle")
        re_product_code = re.compile(r'/dp/(.*?)/')
        pc = re.findall(re_product_code, aa[0].get('href'))

        am = AmazonMongoTradeIn()

        b = Book_NR()
        b.pckey = pc[0]
        b.title = title[0].text_content()

        a = Amazon_NR()
        a.book = b
        a.productcode = pc[0]
        am.amazon = a

        price = Price_NR()
        am.latest_price = price
        am.profitable = 0

        am.save()


def getDepartmentContainer(containers):
    for container in containers:
# Selects [New Releases, Departments, ...]
        h2s = container.cssselect("h2")
        for s in h2s:
        #s = container.cssselect("h2")
            print s.text_content()
        #s = container.cssselect("div.narrowItemHeading")
            matches = re.search(r'Department', s.text_content())
            if matches:
                return container
    return None


def getFormatContainer(containers):
    for container in containers:
        s = container.cssselect("div.narrowItemHeading")
        matches = re.search(r'Format', s[0].text_content())
        if matches:
            return container
    return None


# Works on Apr 27
def addFacetToScan(url):
    content = retrievePage(url)
    #import hashlib

    #fetchPage(url,'facet-' + hashlib.sha224(url).hexdigest());
    html = lhtml.fromstring(content)

    #containers = html.xpath(".//*[@class='refinementContainer']")
    #thecontainer = getDepartmentContainer(containers)

    thecontainer = html.xpath('//*[@class="expand"]/parent::node()/parent::node()/parent::node()')
    if thecontainer is None:
        return

    #Get all navigable directories
    s = thecontainer[0].xpath("./li/a/span[@class='refinementLink']")
    # No more to get -- this is a leaf node so add it to scan
    if not len(s):
        addCategoryToScan(url)

    for cat in s:
    # Get to the anchor tag
        el = cat.xpath("./parent::node()")
        if el:
            tasks.task_addFacetToScan.delay("http://www.amazon.com" + el[0].get('href'))
    print 'Made it thru!'


# Works on Apr 27
def addCategoryToScan(url):
    content = retrievePage(url)
    html = lhtml.fromstring(content)

    s = html.xpath("//h1[@id='breadCrumb']")
    breadcrumb = toAscii(s[0].text_content())

    #print breadcrumb
    containers = html.xpath(".//*[@class='refinementContainer']")
    thecontainer = getFormatContainer(containers)

    #currently always going here - Apr27
    if thecontainer is None:
        ats = Amazon_Textbook_Section_NR(title=breadcrumb, url=url)
        ats.save()
        return

    s = thecontainer.xpath(".//div[@class='refinement']")
    for cat in s:
        el = cat.cssselect("a")
        if el:
            ats = Amazon_Textbook_Section_NR(title=breadcrumb + " " + el[0].text_content(), url=el[0].get('href'))
            ats.save()


def scanCategories():
    objs = Amazon_Textbook_Section_NR.objects.all()
    for obj in iter(objs):
        tasks.task_scanCategoryAndAddBooks.delay(obj)


def scanCategoryAndAddBooks(cat):
    books = countBooksInCategory(cat.url)
    #print "Counted " + str(books)
    pages = int(books) / 12 + 1
    for i in range(1, pages + 1):
        tasks.scanTradeInPage.delay(cat.url, i)
        #tasks.scanTradeInPage(cat.url,i)


def parseUsedPage(am):
    if not am.latest_price:
        am.price = Price_NR()
    url = 'http://www.amazon.com/gp/offer-listing/%s/ref=dp_olp_used?ie=UTF8&condition=used' % (am.amazon.productcode)
    try:
        content = retrievePage(url)
    except:
        return
    html = lhtml.fromstring(content)
    matches = re.search(r'a \$?(\d*\.\d{2}) Amazon.com Gift Card', html.text_content())
    buyprice = None
    if matches != None:
        buyprice = matches.group(1)

    results = html.xpath("//tbody[@class='result']")

    for result in results:
        if re.search('Acceptable', result.cssselect('.condition')[0].text_content()):
            continue
        if re.search('nternational', result.cssselect('.comments')[0].text_content()):
            continue

        sellprice = re.match('\$?(\d*\.\d{2})', result.cssselect('.price')[0].text_content())
        if sellprice != None and buyprice != None:
            sellprice = sellprice.group(1)

            price = Price_NR(buy=buyprice, sell=sellprice)
        else:
            price = Price_NR()

        #am.prices.append(price)
        am.latest_price = price

        if price.buy and price.sell:
            roi = getROI(price.buy, price.sell)
            if roi:
                am.profitable = roi
            else:
                am.profitable = 0
        am.save()
        #print result.cssselect('.condition')[0].text_content()
        break


def fetchPage(url, add):
    content = retrievePage(url)
    f = open('/home/seocortex/dropbox/web/static/testing-' + add + '.html', 'w')
    f.write(content)
    f.close()
