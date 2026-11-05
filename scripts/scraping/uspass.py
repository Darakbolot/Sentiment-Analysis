import os

def userpass():
    return os.environ["IG_USERNAME"], os.environ["IG_PASSWORD"], os.environ.get("IG_VERIFICATION", "")
