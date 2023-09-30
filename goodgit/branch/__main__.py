from .branch import *

# Run and try your code here, use `swiftly run goodgit.branch` to run the code inside __main__
b = input("n for new, s for switch: ")
if b == "n":
    new_branch()
elif b == "s":
    switch_branch()