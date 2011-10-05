from celery.task import TaskSet, task
from amazon import *
from ta.models import Amazon_Textbook_Section, Amazon, Price, ATS_Middle

from itertools import islice



def chunks(it, n):
    for first in it:
        yield [first] + list(islice(it, n - 1))

@task(name='ta.tasks.process_chunk')
def process_chunk(pks,ignore_result=True):
 #   f = open('/tmp/stuff-' + str(pks[0]) + '.txt', 'w')
 #   for i in pks:
 #       f.write(str(i)) 
 #   f.close()
    objs = Amazon.objects.filter(pk__in=pks)
    print str(len(objs))
    for obj in objs:
        detailBook(obj)

@task(name='ta.tasks.process_lots_of_items')
def process_lots_of_items(ids_to_process):
    return TaskSet(process_chunk.subtask((chunk, ))
                       for chunk in chunks(iter(ids_to_process),
                                           25)).apply_async()

@task(name='ta.tasks.process_chunk_cats')
def process_chunk_cats(pks,ignore_result=True):
 #   f = open('/tmp/stuff-' + str(pks[0]) + '.txt', 'w')
 #   for i in pks:
 #       f.write(str(i)) 
 #   f.close()
    objs = ATS_Middle.objects.filter(pk__in=pks)
    for obj in objs:
        findBooks(obj.section.url,obj.page)
        
@task(name='ta.tasks.process_lots_of_items_cats')
def process_lots_of_items_cats(ids_to_process):
    return TaskSet(process_chunk_cats.subtask((chunk, ))
                       for chunk in chunks(iter(ids_to_process),
                                           5)).apply_async()
                                           

@task(name='ta.tasks.addCat',ignore_result=True)
def addCat(x):
    addCategory(x)


@task(name='ta.tasks.addProxy',ignore_result=True)
def addProxy(a,x):
    ap(a,x)
    
@task(name='ta.tasks.addTest')
def addTest(a,x):
    return a + x


@task(name='ta.tasks.findTheBooks',ignore_result=True)
def findTheBooks(url,i):
    findBooks(url,i)


@task(name='ta.tasks.detailTheBook',ignore_result=True)
def detailTheBook(am):
    detailBook(am)
    
@task(name='ta.tasks.findNewBooks',ignore_result=True)
def findNewBooks():
    objs = Amazon.objects.values_list('productcode', flat=True)
    tasks.process_lots_of_items(objs)
              
@task(name='ta.tasks.deleteExtraneousPrices',ignore_result=True)
def deleteExtraneousPrices():
    objs = Amazon.objects.all()
    for obj in objs:
        amz = Price.objects.filter(amazon=obj).order_by("-timestamp")
        count = len(amz)
        #print "Trying! " + str(count)
        if count > 1:
            for i in xrange(count-1,1,-1):
                #print i
                if (amz[i-1].buy == amz[i-2].buy) and (amz[i-1].sell == amz[i-2].sell):
                    amz[i-1].delete()
    
@task(name='ta.tasks.doTheBooks',ignore_result=True)
def doTheBooks(objs):
    for obj in objs:
        detailTheBook.delay(am)
        
@task(name='ta.tasks.updateBCs',ignore_result=True)
def updateBCs():
    updateBookCounts() 
    getProfitableBooks()