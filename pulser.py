#!/usr/bin/env python3

from AFG31000 import pulser

import sys




if __name__=='__main__':
  pulser( **dict(arg.split('=') for arg in sys.argv[1:])) # kwargs
