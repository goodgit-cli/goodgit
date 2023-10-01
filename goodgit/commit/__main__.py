from .add import *
from .commit import *
from .push import *
from .uncommit import *

# Run and try your code here, use `swiftly run goodgit.commit` to run the code inside __main__
c = input("c for commit, u for uncommit: ")
if c == "c":
    add()
    commit()
    push_to_remote()

elif c == "u":
    uncommit()