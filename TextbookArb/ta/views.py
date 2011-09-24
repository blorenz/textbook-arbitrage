# Create your views here.
from django.shortcuts import render_to_response
from ta.models import Amazon_Textbook_Section, Book, Amazon, Price, ATS_Middle
from django.core.context_processors import csrf
from django.http import HttpRequest, HttpResponse
from celery.task.sets import TaskSet
from django.db.models import F
import tasks
from amazon import f7, difference


def getDeals(request):
    dictItems = {}
    totalIndexedL = Price.objects.raw("SELECT id, count(DISTINCT amazon_id) AS thecount FROM ta_price")
    totalIndexed = totalIndexedL[0].thecount
    totalBooks = Amazon.objects.count()
    totalProfitable = Price.objects.filter(buy__gte=F('sell')).values('amazon_id').distinct().count()
   # foo = Price.objects.all().extra(where=['amazon_id IS NOT NULL']).distinct().filter(buy__gte=F('sell')+9)
   # foo = Price.objects.raw('SELECT DISTINCT amazon_id, buy, sell FROM ta_price WHERE `ta_price`.`buy` >=  `ta_price`.`sell` + 9')
    foo = Price.objects.order_by('-timestamp').distinct().only('amazon', 'buy', 'sell', 'timestamp').filter(buy__gte=F('sell')+9)
    for obj in foo:
	    ctb = 0
	    actb = 0
	    if (float(obj.sell) != 0):
		ctb = (float(obj.buy)-float(obj.sell)) / float(obj.sell)
		actb = (float(obj.buy)-float(obj.sell)) / (float(obj.sell) + 3.99)
            amz = Amazon.objects.only('url', 'book').filter(pk=obj.amazon.id).get()
            bk = Book.objects.only('title').filter(pk=amz.book.id).get()
	    dictItems[amz.url] = (amz.url,
                             bk.title,
                            float(obj.buy),
                            float(obj.sell),
                            float(obj.buy) - float(obj.sell),
			    ctb, actb, obj.timestamp )
    
    return render_to_response('deals.html', {'dictItems': dictItems, 
                                             'totalIndexed': totalIndexed,
                                             'totalProfitable': totalProfitable,
                                             'totalBooks': totalBooks,
                                             })

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
                     ATS_Middle.objects.create(url=cat.url + "&page="+  str(i))
                     #tasks.findTheBooks.delay(cat.url,i)
            return HttpResponse('Done!')
    else:
        c = {}
        c.update(csrf(request))
       # latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
        return render_to_response('defineCategories.html',c)


def getOthers(request):
     t = Amazon.objects.values_list('id', flat=True).distinct()
     p = Price.objects.values_list('amazon_id', flat=True).distinct()
     s = difference(p,t)
     tasks.process_lots_of_items(s)
     return HttpResponse("Created " + str(len(s)) + " tasks" + str(t) + "<br><br><br>" + str(p)+ "<br><br><br>" + str(s))
      
def defineProxies(request):
    if request.method == 'POST':
        if (request.POST.get('proxies')):
            urls = request.POST.get('proxies').strip().split()
            for url in urls:
                tasks.addProxy.delay('http',url)
            return HttpResponse(str(len(urls)))
        else:
            objs = Amazon.objects.values_list('id', flat=True)
            
            tasks.process_lots_of_items(objs)

            
            return HttpResponse("Created " + str(len(objs)) + " tasks (but didn't execute)")
            #tasks.doBooks.delay(objs)
    else:
        c = {}
        c.update(csrf(request))
       # latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
        return render_to_response('defineProxies.html',c)
