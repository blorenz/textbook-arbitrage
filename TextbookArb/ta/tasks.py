from celery.task import TaskSet, task
from amazon import addCategory
from amazon import addProxy as ap
from amazon import findBooks
from amazon import detailBook
from amazon import findBooksWithPage
from ta.models import Amazon_Textbook_Section, Amazon, Price, ATS_Middle

from itertools import islice



def chunks(it, n):
    for first in it:
        yield [first] + list(islice(it, n - 1))

@task(name='ta.tasks.process_chunk')
def process_chunk(pks):
 #   f = open('/tmp/stuff-' + str(pks[0]) + '.txt', 'w')
 #   for i in pks:
 #       f.write(str(i)) 
 #   f.close()
    objs = Amazon.objects.filter(pk__in=pks)
    for obj in objs:
        detailBook(obj)

@task(name='ta.tasks.process_lots_of_items')
def process_lots_of_items(ids_to_process):
    return TaskSet(process_chunk.subtask((chunk, ))
                       for chunk in chunks(iter(ids_to_process),
                                           1000)).apply_async()

@task(name='ta.tasks.process_chunk_cats')
def process_chunk_cats(pks):
 #   f = open('/tmp/stuff-' + str(pks[0]) + '.txt', 'w')
 #   for i in pks:
 #       f.write(str(i)) 
 #   f.close()
    objs = ATS_Middle.objects.filter(pk__in=pks)
    for obj in objs:
        findBooksWithPage(obj.url)
        
@task(name='ta.tasks.process_lots_of_items_cats')
def process_lots_of_items_cats(ids_to_process):
    return TaskSet(process_chunk_cats.subtask((chunk, ))
                       for chunk in chunks(iter(ids_to_process),
                                           1000)).apply_async()
                                           

@task(name='ta.tasks.add')
def add(x, y):
    return x + y

@task(name='ta.tasks.addCat')
def addCat(x):
    addCategory(x)


@task(name='ta.tasks.addProxy')
def addProxy(a,x):
    ap(a,x)


@task(name='ta.tasks.findTheBooks')
def findTheBooks(url,i):
    findBooks(url,i)


@task(name='ta.tasks.detailTheBook',ignore_result=True)
def detailTheBook(am):
    detailBook(am)
    

@task(name='ta.tasks.doTheBooks',ignore_result=True)
def doTheBooks(objs):
    for obj in objs:
        detailTheBook.delay(am)
        

@task(name='ta.tasks.doBooks')
def doBooks(objs):
    slices = len(objs) / 1000
    for i in range(0,slices):
        doTheBooks.delay(objs[i*1000:i*1000+1001])