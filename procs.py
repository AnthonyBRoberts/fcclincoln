from hirefire.procs.celery import CeleryProc

class CelerydProc(CeleryProc):
    name = 'celeryd'
    queues = ['celery']

class CelerybeatProc(CeleryProc):
    name = 'celerybeat'
    queues = ['celery']
