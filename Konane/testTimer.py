from threading import Timer
import thread, time, sys
from multiprocessing import Process

def doStuff(tts):
    """
    Busy waiting function to simulate actual program work.
    """
    print "busy wait for : " + str(tts) + " seconds"
    start_check = time.clock()
    prev_check = start_check
    while time.clock() - start_check < float(tts):
        prev_check = time.clock()
    print "Complete"
    return "Busy waiting finished"

def kill():
    """
    Raises an exception in the main execution thread

    You can't replace this with a generic 'raise Exception"
    statement, because exceptions raised in a child thread
    don't necessarily appear in the parent thread.
    """
    thread.interrupt_main()

def simple_method():
    print "Demonstration of a platform-independent timeout method"
    timeout = input("How many seconds do you want to allow the program to run? ")
    wait_time = input("How long do you want the program to _attempt_ to run? ")
    """
    This is what actually does the timeout 'work':

    -Timer(timeout, kill).start() creates a new timer that will call function
    "kill" after timeout seconds.

    -if doStuff(wait_time) completes _before_ the timer calls "kill", the
    program continues on, if not, the "try/except" block catches the
    exception raised by "kill" and the program stops executing "doStuff"
    """
    ret_val = "Timed out, no return value!"
    try:
        TimeoutTimer = Timer(timeout, kill)
        TimeoutTimer.start()
        ret_val = doStuff(wait_time)
    except:
        print "***Looks like we timed out***"
    TimeoutTimer.cancel()
    print ret_val

if __name__ == '__main__':
    """
    Caveat: this only works if your 'worker' function
    _does not_ use time.sleep() calls in it, as time.sleep()
    stops _all_ execution, including the timeout!
    """
    simple_method()
