# Create your views here.
from django.shortcuts import render_to_response
from ta.models import Amazon_Textbook_Section, Book, Amazon, Price
from django.core.context_processors import csrf
from django.http import HttpRequest, HttpResponse
from celery.task.sets import TaskSet
from django.db.models import F
import tasks
from amazon import f7


def getDeals(request):
    dealList = []
    totalIndexed = Price.objects.count()
    totalProfitable = Price.objects.filter(buy__gte=F('sell')).count()
   # foo = Price.objects.all().extra(where=['amazon_id IS NOT NULL']).distinct().filter(buy__gte=F('sell')+9)
   # foo = Price.objects.raw('SELECT DISTINCT amazon_id, buy, sell FROM ta_price WHERE `ta_price`.`buy` >=  `ta_price`.`sell` + 9')
    foo = Price.objects.all().distinct().only('amazon', 'buy', 'sell').filter(buy__gte=F('sell')+9)
    for obj in foo:
	    ctb = 0
	    actb = 0
	    if (float(obj.sell) != 0):
		ctb = (float(obj.buy)-float(obj.sell)) / float(obj.sell)
		actb = (float(obj.buy)-float(obj.sell)) / (float(obj.sell) + 3.99)
            amz = Amazon.objects.only('url', 'book').filter(pk=obj.amazon.id).get()
            bk = Book.objects.only('title').filter(pk=amz.book.id).get()
	    dealList.append((amz.url,
                             bk.title,
                            float(obj.buy),
                            float(obj.sell),
                            float(obj.buy) - float(obj.sell),
			    ctb, actb ))
    
    return render_to_response('deals.html', {'dealList': dealList, 
                                             'totalIndexed': totalIndexed,
                                             'totalProfitable': totalProfitable,
                                             })
    
def defineCategories(request):
    if request.method == 'POST':
        if (request.POST.get('categories')):
            urls = request.POST.get('categories').strip().split()
            for url in urls:
                tasks.addCat.delay(url)
            return HttpResponse(str(len(urls)))
        else:
            for cat in Amazon_Textbook_Section.objects.all():
                 for i in range(1,101):
                     tasks.findTheBooks.delay(cat.url,i)
            return HttpResponse('Done!')
    else:
        c = {}
        c.update(csrf(request))
       # latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
        return render_to_response('defineCategories.html',c)
    
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
