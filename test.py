import sys, time, itertools as it

sys.stderr.write(
    '\nHi! Welcome to the do nothing loader! :D\n\n\tLoading . . . ')
for i in it.cycle('|/-\\'):
    sys.stderr.write(i)
    time.sleep(1)
    sys.stderr.write('\b')
