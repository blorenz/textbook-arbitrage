# Create your views here.
from django.shortcuts import render_to_response
from ta.models import Amazon_Textbook_Section, ProfitableBooks, Book, Amazon, Price, ATS_Middle, MetaTable
from django.core.context_processors import csrf
from django.http import HttpRequest, HttpResponse
from celery.task.sets import TaskSet
from django.db.models import F
import tasks
from amazon import f7, difference
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json

def loginThing(request):
    if request.method == 'POST':
     username = request.POST['l']
     password = request.POST['p']
     user = authenticate(username=username, password=password)
     if (user is not None):
         if user.is_active:
           login(request,user)
           return HttpResponse("Logged in!!")
         else:
            return HttpResponse("Disabled account!")
     else:
            
            return HttpResponse("No Account! ")
    else:
        c = {}
        c.update(csrf(request))
        return render_to_response('login.html',c)
	
    
    
def lazy(request):
    objs = Amazon.objects.values_list('productcode', flat=True).filter(productcode=request.GET['product'])
    tasks.process_lots_of_items(objs)
    return HttpResponse(request.GET['product'] + " : " + str(objs))
    
    
def getHistoricalPrices(request):
    amz_code = request.GET['amazoncode']
    foo = Price.objects.raw("SELECT id,buy,sell,timestamp from ta_price a WHERE a.amazon_id = '" + amz_code + "' ORDER BY a.timestamp ASC")
    output = []
    lastprice = -1
    
    if request.GET['type'] == 'buy':
        for s in foo:
            if not s.buy:
                s.buy = 0.0
            
            if s.buy != lastprice:   
                output.append((s.timestamp.isoformat(' '), float(s.buy)))
            lastprice = s.buy
    else:
        for s in foo:
            if not s.sell:
                s.sell = 0.0
            if s.sell != lastprice:
                output.append((s.timestamp.isoformat(' '), float(s.sell)))
            lastprice = s.sell
    
    
    return HttpResponse(json.dumps(output))
    
def getKnown(request):
    tasks.doKnown.delay()
    return HttpResponse('Did it!')
    
def getAllKnown(request):   
    foo = Price.objects.raw('SELECT id,amazon_id FROM ( SELECT *, row_number() over (partition by amazon_id order by timestamp DESC) r from ta_price ) x where r = 1 AND buy <> null')
    f = []
    for s in foo:
        f.append(s.amazon_id)
    tasks.process_lots_of_items(f)    
    return HttpResponse('Doing so for %d' % (len(f), ))

@login_required(login_url='/login/')
def getDeals(request):
    dictItems = {}
    
    if request.user.username == 'brandon':
      referer = 'http://www.amazon.com/gp/product/%s/ref=as_li_ss_tl?ie=UTF8&tag=deafordea-20&linkCode=as2&camp=217145&creative=399373&creativeASIN=%s'
    else:
      referer = 'http://www.amazon.com/gp/product/%s/ref=as_li_ss_tl?ie=UTF8&tag=ngre-20&linkCode=as2&camp=217145&creative=399373&creativeASIN=%s'

    totalIndexed = MetaTable.objects.get(metakey="totalIndexed").int_field
    totalBooks = MetaTable.objects.get(metakey="totalBooks").int_field
    totalProfitable = MetaTable.objects.get(metakey="totalProfitable").int_field

    foo = ProfitableBooks.objects.all().values_list("price",flat=True)

    objs = Price.objects.filter(pk__in=foo).values_list("buy","sell","amazon__productcode","amazon__book__title","timestamp")
    
    for obj in iter(objs):
        ctb = 0
        actb = 0
        theBuy = float(obj[0])
        theSell = float(obj[1])
        
        if (theSell != 0):
            ctb = (theBuy-theSell) / theSell
            actb = (theBuy-(theSell+3.99)) / (theSell+3.99) 
            ctb = round(ctb * 100,2)
            actb = round(actb * 100,2)
            

            productCode = obj[2]
            dictItems[productCode] = (referer % (productCode, productCode),
                                 obj[3],
                                theBuy,
                                theSell,
                                theBuy - theSell,
            	    ctb, actb, obj[4], productCode )
    
    return render_to_response('deals.html', {'dictItems': dictItems, 
                                             'totalIndexed': totalIndexed,
                                             'totalProfitable': totalProfitable,
                                             'totalBooks': totalBooks,
                                             'username': request.user.username,
                                             })

def logout_user(request):
	logout(request)
	return HttpResponse("Logged out!")
	
def launch(request):   
    objs = ATS_Middle.objects.values_list('id', flat=True)      
    tasks.process_lots_of_items_cats(objs) 
    return HttpResponse("Created " + str(len(objs)) + " tasks (but didn't execute)")

def defineCategories(request):
    if request.method == 'POST':
        if (request.POST.get('categories')):
            urls = request.POST.get('categories').strip().split()
            for url in urls:
                tasks.addCat.delay(url)
                tasks.addCat.delay(url + "&sort=pricerank")
                tasks.addCat.delay(url + "&sort=inversepricerank")
                tasks.addCat.delay(url + "&sort=daterank")
                tasks.addCat.delay(url + "&sort=reviewrank_authority")
            return HttpResponse(str(len(urls)))
        else:
            for cat in Amazon_Textbook_Section.objects.all():
                 for i in range(1,101):
                     ATS_Middle.objects.create(page=i,section=cat)
                     #tasks.findTheBooks.delay(cat.url,i)
            return HttpResponse('Done!')
    else:
        c = {}
        c.update(csrf(request))
       # latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
        return render_to_response('defineCategories.html',c)


def getOthers(request):
     #t = Amazon.objects.values_list('productcode', flat=True).distinct()
     #p = Price.objects.values_list('amazon_id', flat=True).distinct()
     #s = difference(p,t)
     #tasks.process_lots_of_items(s)
     tasks.deleteExtraneousPrices.delay()
     return HttpResponse("ok!")
     #return HttpResponse("Created " + str(len(s)) + " tasks")# + str(t) + "<br><br><br>" + str(p)+ "<br><br><br>" + str(s))
      
def defineProxies(request):
    if request.method == 'POST':
        if (request.POST.get('proxies')):
            urls = request.POST.get('proxies').strip().split()
            for url in urls:
                tasks.addProxy.delay('http',url)
            return HttpResponse(str(len(urls)))
        else:
            objs = Amazon.objects.values_list('productcode', flat=True)
            
            tasks.process_lots_of_items(objs)

            
            return HttpResponse("Created " + str(len(objs)) + " tasks (but didn't execute)")
            #tasks.doBooks.delay(objs)
    else:
        c = {}
        c.update(csrf(request))
       # latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
        return render_to_response('defineProxies.html',c)
