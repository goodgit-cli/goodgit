import multiprocessing

def logalytics(data):
    from remote_log import remote_log
    remote_log("https://orca-app-qmx5i.ondigitalocean.app/api/analytics/", data)
    
def unblocking_logalytics(data):
    process = multiprocessing.Process(target=logalytics, args=(data,))
    process.start()
    # Now unblocking_logalytics will return immediately, while logalytics runs in its own process.

# Usage:
# unblocking_logalytics(some_data)
