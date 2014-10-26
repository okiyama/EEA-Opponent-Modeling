import signal, time

"""
A technique for timing out a python function.

Simply import this file, then put an @timed_out(limit) line directly
above any function or class method you want to be able to limit.  The
limit is the maximum number of seconds the function or method can run.
If the limit is exceeded a TimedOutException will be raised.
"""

class TimedOutException(Exception):
    def __init__(self, value = "Timed Out"):
        self.value = value
    def __str__(self):
        return repr(self.value)

def timed_out(timeout):
    def decorate(f):
        def handler(signum, frame):
            raise TimedOutException()
        
        def new_f(*args, **kwargs):
            old = signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            try:
                result = f(*args, **kwargs)
            finally:
                signal.signal(signal.SIGALRM, old)
            signal.alarm(0)
            return result
        
        new_f.func_name = f.func_name
        return new_f
    return decorate

@timed_out(4)
def fn_2(secs):
    time.sleep(secs)
    return "Finished"

@timed_out(2)
def fn_3(secs):
    time.sleep(secs)
    return "Finished"

if __name__ == '__main__':

    try:
        print "fn_2 (sleep 2, timeout 4): ",
        print fn_2(2)
    except TimedOutException:
        print "took too long"

    try:
        print "fn_3 (sleep 4, timeout 2): ",
        print fn_3(4)
    except TimedOutException:
        print "took too long"

