#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Sun 15 Apr 14:01:39 2012
#
# Copyright (C) 2011-2013 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Inverts the list of floating point numbers given on command line
"""

from .._library import reverse

def main():
  """Main routine, called by the script that gets the configuration of bob.blitz"""

  import sys
  if len(sys.argv) == 1:
    print ("Usage: %s <numbers>\n" % sys.argv[0])
    return

  numbers = [float(n) for n in sys.argv[1:]]
  print (numbers)
  rev = reverse(numbers)

  print ("%s reversed is %s" % (numbers, rev))
