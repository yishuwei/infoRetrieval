#!/bin/env python
import struct

def bitsToBytes(bits):
  if len(bits) % 8 != 0:
    bits.extend([1] * (8 - len(bits) % 8))
  bytes = []
  for i in range(0,len(bits),8):
    bytes.append(bits[i]*128+bits[i+1]*64+bits[i+2]*32+bits[i+3]*16+bits[i+4]*8+bits[i+5]*4+bits[i+6]*2+bits[i+7])
  return bytes

def numToBits(n):
  offset = []
  length = []
  while n > 1:
    offset.append(n % 2)
    length.append(1)
    n /= 2
  length.append(0)
  offset.reverse()  
  return length + offset

def gammaEncode(numbers):
  bitstream = []
  for n in numbers:
    bitstream.extend(numToBits(n))
  bytes = bitsToBytes(bitstream)  
  return struct.pack('B'*len(bytes), *bytes)

def gammaDecode(s):
  bits = ''.join(bin(ord(ch))[2:].zfill(8) for ch in s)
  numbers = []
  i = 0
  length = 0
  reading_length = True
  while i < len(bits):
    if reading_length:
      if bits[i] == '1':
        length += 1
      else:
        reading_length = False
      i += 1
    else:
      offset = '1' + bits[i:i+length]
      numbers.append(int(offset,2))
      i += length
      length = 0
      reading_length = True
  if not reading_length and length == 0:
    numbers.append(1)
  return numbers

def convertPostings(postings):
  diff = [postings[0]]
  for i in range(1, len(postings)):
    diff.append(postings[i] - postings[i-1])
  return gammaEncode(diff)

def getPostings(s):
  postings = gammaDecode(s)
  for i in range(1, len(postings)):
    postings[i] = postings[i-1] + postings[i]
  return postings