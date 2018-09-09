from threading import Thread
import random,time

class MyThread(Thread):
    def __init__(self, func, name, args=()):
        super(MyThread, self).__init__()
        self.func = func
        self.args = args
        self.name = name
 
    def run(self):
        self.result = self.func(*self.args)
 
    def get_result(self):
        Thread.join(self) # 等待线程执行完毕
        try:
            return self.result
        except Exception:
            return None

