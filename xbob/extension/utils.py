#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.dos.anjos@gmail.com>
# Fri 21 Mar 2014 10:37:40 CET

'''General utilities for building extensions'''

def uniq(seq):
  """Uniqu-fy preserving order"""

  seen = set()
  seen_add = seen.add
  return [x for x in seq if x not in seen and not seen_add(x)]
