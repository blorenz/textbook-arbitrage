from celery.task import task
from amazon import addCategory
from amazon import addProxy as ap
from amazon import findBooks
from amazon import detailBook


@task(name='ta.tasks.add')
def add(x, y):
    return x + y

@task(name='ta.tasks.addCat')
def addCat(x):
    addCategory(x)
    return True

@task(name='ta.tasks.addProxy')
def addProxy(a,x):
    ap(a,x)
    return True

@task(name='ta.tasks.findTheBooks')
def findTheBooks(url,i):
    findBooks(url,i)
    return True

@task(name='ta.tasks.detailTheBook')
def detailTheBook(am):
    detailBook(am)
    return True

@task(name='ta.tasks.doTheBooks')
def doTheBooks(allAm):
    for am in allAm:
        detailTheBook.delay(am)
    return True
