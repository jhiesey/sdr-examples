# Copyright 2014 Clayton Smith
#
# This file is part of sdr-examples
#
# sdr-examples is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# sdr-examples is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with sdr-examples; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

from array import array
import math

COLOR_FREQ = 3579545.0 - 15750.0
SAMPLES_PER_LINE = 772
SAMP_RATE = SAMPLES_PER_LINE * 60 * .999 * 525 / 2
RADIANS_PER_SAMPLE = 2 * math.pi * COLOR_FREQ / SAMP_RATE

SYNCH_LEVEL = -40.0
BLANKING_LEVEL = 0.0
BLACK_LEVEL = 7.5
WHITE_LEVEL = 100.0

EQUALIZING_PULSE = [SYNCH_LEVEL] * 28 + [BLANKING_LEVEL] * 358
SYNCHRONIZING_PULSE = [SYNCH_LEVEL] * 329 + [BLANKING_LEVEL] * 57
INTERVALS = EQUALIZING_PULSE * 6 + SYNCHRONIZING_PULSE * 6 + EQUALIZING_PULSE * 6
EXTRA_HALF_LINE = [BLANKING_LEVEL] * 386

FRONT_PORCH = [BLANKING_LEVEL] * 18
SYNCH_PULSE = [SYNCH_LEVEL] * 57

def addBackPorch():
  global ntsc_signal
  ntsc_signal += [BLANKING_LEVEL] * 13
  l = len(ntsc_signal)
  for x in range(l, l+31):
    ntsc_signal += [BLANKING_LEVEL + 20 * math.sin(math.pi + RADIANS_PER_SAMPLE * x)]
  ntsc_signal += [BLANKING_LEVEL] * 13

def addNonVisibleLine():
  global ntsc_signal
  ntsc_signal += SYNCH_PULSE
  addBackPorch()
  ntsc_signal += [BLANKING_LEVEL] * 658

def addFirstHalfFrame():
  global ntsc_signal
  ntsc_signal += SYNCH_PULSE
  addBackPorch()
  ntsc_signal += [BLACK_LEVEL] * 272

def addSecondHalfFrame():
  global ntsc_signal
  ntsc_signal += SYNCH_PULSE
  addBackPorch()
  ntsc_signal += [BLANKING_LEVEL] * 272 + [BLACK_LEVEL] * 368 + FRONT_PORCH

def addPixel(x):
  global ntsc_signal, BLACK_LEVEL, WHITE_LEVEL
  gate_on = (x * 12 / 640) % 1 < 0.3
  Ec = 0
  if gate_on:
    Ec = 20

  phase = math.pi + RADIANS_PER_SAMPLE * len(ntsc_signal)
  Em = Ec * math.sin(math.pi + RADIANS_PER_SAMPLE * len(ntsc_signal))

  ntsc_signal += [BLACK_LEVEL + (WHITE_LEVEL - BLACK_LEVEL) * Em]

ntsc_signal = []

# Generate even field
ntsc_signal += INTERVALS
for x in range(13):
  addNonVisibleLine()
for line in range(0,480,2):
  ntsc_signal += SYNCH_PULSE
  addBackPorch()
  for x in range(640):
    addPixel(x)
  ntsc_signal += FRONT_PORCH
addFirstHalfFrame()

# Generate odd field
ntsc_signal += INTERVALS + EXTRA_HALF_LINE
for x in range(12):
  addNonVisibleLine()
addSecondHalfFrame()
for line in range(1,481,2):
  ntsc_signal += SYNCH_PULSE
  addBackPorch()
  for x in range(640):
    addPixel(x)
  ntsc_signal += FRONT_PORCH

ntsc_signal = [0.75 - (0.25/40) * x for x in ntsc_signal]

f = open('ve3irr-testing.dat', 'wb')
ntsc_array = array('f', ntsc_signal)
ntsc_array.tofile(f)
f.close()
