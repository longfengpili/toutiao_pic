from threading import Thread
import random,time
import logging

logging.basicConfig(level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(filename)s - %(threadName)s - %(lineno)d行 - %(message)s")

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

