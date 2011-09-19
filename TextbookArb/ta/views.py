# Create your views here.
from django.shortcuts import render_to_response
from ta.models import Amazon_Textbook_Section, Amazon
from django.core.context_processors import csrf
from django.http import HttpRequest, HttpResponse
import tasks


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
            tasks.doTheBooks.delay(Amazon.objects.order_by('?')[:1000])
    else:
        c = {}
        c.update(csrf(request))
       # latest_poll_list = Poll.objects.all().order_by('-pub_date')[:5]
        return render_to_response('defineProxies.html',c)