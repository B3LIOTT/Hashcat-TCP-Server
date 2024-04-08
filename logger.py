import sys


def basic_info(info):
    print("[+] INFO: ", info)


def severe_info(info):
    print("[X] INFO: ", info)


def error(err):
    sys.stderr.write(f"[!] ERREUR: {err}")
