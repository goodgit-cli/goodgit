from .timetravel import *
from .apply import *

# Run and try your code here, use `swiftly run goodgit.timetravel` to run the code inside __main__
t = input("t for timetravel, a for apply")
if t == "t":
    timetravel()
elif t == "a":
    apply_timetravel()