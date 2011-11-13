from celery.task import TaskSet, task
from amazon import *
from ta.models import AmazonMongo

from itertools import islice



def chunks(it, n):
    for first in it:
        yield [first] + list(islice(it, n - 1))

@task(name='ta.tasks.process_chunk')
def process_chunk(pks,ignore_result=True):
    #objs = Amazon_NR.objects.filter(pk__in=pks)
    for p in pks:
        print p
        objs = AmazonMongo.objects.filter(pk=p)
        #print str(len(objs))
        for obj in objs:
            #detailBook(obj)
            parseUsedPage(obj)

@task(name='ta.tasks.process_lots_of_items')
def process_lots_of_items(ids_to_process):
    return TaskSet(process_chunk.subtask((chunk, ))
                       for chunk in chunks(iter(ids_to_process),
                                           25)).apply_async()



@task(name='ta.tasks.process_chunk_profitable')
def process_chunk_profitable(pks,ignore_result=True):
    #objs = Amazon_NR.objects.filter(pk__in=pks)
    for p in pks:
        objs = AmazonMongo.objects.filter(pk=p)
        #print str(len(objs))
        for obj in objs:
            #detailBook(obj)
            checkProfitable(obj)

@task(name='ta.tasks.process_lots_of_items_profitable')
def process_lots_of_items_profitable(ids_to_process):
    return TaskSet(process_chunk_profitable.subtask((chunk, ))
                       for chunk in chunks(iter(ids_to_process),
                                           25)).apply_async()
                                           
                                           
@task(name='ta.tasks.process_chunk_nulltimes')
def process_chunk_nulltimes(pks,ignore_result=True):
    #objs = Amazon_NR.objects.filter(pk__in=pks)
    for p in pks:
        objs = AmazonMongo.objects.filter(pk=p)
        #print str(len(objs))
        for obj in objs:
            #detailBook(obj)
            nullTimes(obj)

@task(name='ta.tasks.process_lots_of_items_nulltimes')
def process_lots_of_items_nulltimes(ids_to_process):
    return TaskSet(process_chunk_nulltimes.subtask((chunk, ))
                       for chunk in chunks(iter(ids_to_process),
                                           25)).apply_async()
                                           
@task(name='ta.tasks.process_chunk_convert')
def process_chunk_convert(pks,ignore_result=True):
 #   f = open('/tmp/stuff-' + str(pks[0]) + '.txt', 'w')
 #   for i in pks:
 #       f.write(str(i)) 
 #   f.close()
    objs = Amazon.objects.filter(pk__in=pks)
    #print str(len(objs))
    for obj in objs:
        #detailBook(obj)
        print obj
        convertBook(obj)

@task(name='ta.tasks.process_lots_of_items_convert')
def process_lots_of_items_convert(ids_to_process):
    return TaskSet(process_chunk_convert.subtask((chunk, ))
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
                                           

@task(name='ta.tasks.process_chunk_extra')
def process_chunk_extra(pks,ignore_result=True):
    objs = Amazon.objects.filter(pk__in=pks)
    deleteExtraneousPricesWorker(objs)

@task(name='ta.tasks.process_lots_of_items_extra')
def process_lots_of_items_extra(ids_to_process):
    return TaskSet(process_chunk_extra.subtask((chunk, ))
                       for chunk in chunks(iter(ids_to_process),
                                           25)).apply_async()
                                           
@task(name='ta.tasks.addCat',ignore_result=True)
def addCat(x):
    addCategoryToScan(x)


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
    parseUsedPage(am)
    
@task(name='ta.tasks.findNewBooks',ignore_result=True)
def findNewBooks():
    detailAllBooks()

@task(name='ta.tasks.updateProfitable',ignore_result=True)
def updateProfitable():
    ProfitableBooks.objects.values_list("price__amazon")
     
@task(name='ta.tasks.lookForNewBooks',ignore_result=True) 
def lookForNewBooks():           
    lookForBooks()
    
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
  
@task(name='ta.tasks.doKnown',ignore_result=True)   
def doKnown():   
    foo = Price.objects.raw('SELECT id,amazon_id from ta_price a WHERE NOT EXISTS ( SELECT * FROM ta_price b WHERE b.amazon_id = a.amazon_id AND b.timestamp > a.timestamp ) AND a.buy > a.sell')
    #SELECT id,amazon_id FROM ( SELECT *, row_number() over (partition by amazon_id order by timestamp DESC) r from ta_price ) x where r = 1 AND buy > sell')
    f = []
    for s in foo:
        f.append(s.amazon_id)
    tasks.process_lots_of_items(f) 
    
@task(name='ta.tasks.doKnownAllTrades',ignore_result=True)   
def doKnownAllTrades():   
    foo = Price.objects.raw('SELECT id,amazon_id from ta_price a WHERE NOT EXISTS ( SELECT * FROM ta_price b WHERE b.amazon_id = a.amazon_id AND b.timestamp > a.timestamp ) AND a.buy > 0')
    f = []
    for s in foo:
        f.append(s.amazon_id)
    tasks.process_lots_of_items(f)    
    
@task(name='ta.tasks.updateBCs',ignore_result=True)
def updateBCs():
    updateBookCounts() 
    getProfitableBooks()
