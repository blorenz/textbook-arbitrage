# Create your views here.
from django.shortcuts import render_to_response
from ta.models import Amazon_Textbook_Section, Book, Amazon, Price, ATS_Middle
from django.core.context_processors import csrf
from django.http import HttpRequest, HttpResponse
from celery.task.sets import TaskSet
from django.db.models import F
import tasks
from amazon import f7, difference
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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
    return HttpResponse("done")
    
    
    
    
def getKnown(request):   
    foo = Price.objects.raw('SELECT id,amazon_id FROM ( SELECT *, row_number() over (partition by amazon_id order by timestamp DESC) r from ta_price ) x where r = 1 AND buy > sell')
    f = []
    for s in foo:
        f.append(s.amazon_id)
    tasks.process_lots_of_items(f)    
    return HttpResponse('Doing so for %d for %s' % (len(f), str(f)))
    
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
    #totalIndexedL = Price.objects.raw('SELECT "ta_price"."id", COUNT(DISTINCT "ta_price"."amazon_id") AS thecount FROM "ta_price"')
    #totalIndexed = totalIndexedL[0].thecount
    totalIndexed = Price.objects.only('amazon_id').distinct().count()
    #totalIndexedL = Price.objects.raw('select id, count(distinct amazon_id) AS thecount from ta_price')
    #totalIndexed = totalIndexedL[0].thecount
    
    totalBooks = Amazon.objects.count()
    totalProfitable = Price.objects.filter(buy__gte=F('sell')).values('amazon_id').distinct().count()
   # foo = Price.objects.all().extra(where=['amazon_id IS NOT NULL']).distinct().filter(buy__gte=F('sell')+9)
   # foo = Price.objects.raw('SELECT DISTINCT amazon_id, buy, sell FROM ta_price WHERE `ta_price`.`buy` >=  `ta_price`.`sell` + 9')
    #foo = Price.objects.order_by('-timestamp').distinct().only('amazon', 'buy', 'sell', 'timestamp').filter(buy__gte=F('sell'))
    foo = Price.objects.raw('SELECT * FROM ( SELECT *, row_number() over (partition by amazon_id order by timestamp DESC) r from ta_price ) x where r = 1 AND buy > sell + 9')

    for obj in foo:
	    ctb = 0
	    actb = 0
	    if (float(obj.sell) != 0):
		ctb = (float(obj.buy)-float(obj.sell)) / float(obj.sell)
		actb = (float(obj.buy)-float(obj.sell)) / (float(obj.sell) + 3.99)
            amz = Amazon.objects.only('productcode', 'book').filter(pk=obj.amazon.productcode).get()
            bk = Book.objects.only('title').filter(pk=amz.book.pckey).get()
	    dictItems[amz.productcode] = (referer % (amz.productcode, amz.productcode),
                             bk.title,
                            float(obj.buy),
                            float(obj.sell),
                            float(obj.buy) - float(obj.sell),
			    ctb, actb, obj.timestamp, amz.productcode )
    
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
     t = Amazon.objects.values_list('productcode', flat=True).distinct()
     p = Price.objects.values_list('amazon_id', flat=True).distinct()
     s = difference(p,t)
     tasks.process_lots_of_items(s)
     return HttpResponse("Created " + str(len(s)) + " tasks")# + str(t) + "<br><br><br>" + str(p)+ "<br><br><br>" + str(s))
      
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
