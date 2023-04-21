import os
from contextlib import contextmanager


@contextmanager
def chdir(path: str):
   old = os.getcwd()
   os.chdir(path)
   try:
       yield
   finally:
       os.chdir(old)
