#!/bin/env python
import struct

def numToBytes(n):
  bytes = []
  while True:
    bytes.append(n % 128)
    if n < 128: break
    n /= 128
  bytes[0] += 128
  bytes.reverse()
  return bytes  

def VBEncode(numbers):
  bytestream = []
  for n in numbers:
    bytestream.extend(numToBytes(n))
  return struct.pack('B'*len(bytestream), *bytestream)

def VBDecode(s):
  numbers = []
  n = 0
  for ch in s:
    byte = ord(ch)
    if byte < 128:
      n = 128 * n + byte
    else:
      n = 128 * n + (byte - 128)
      numbers.append(n)
      n = 0
  return numbers

def convertPostings(postings):
  diff = [postings[0]]
  for i in range(1, len(postings)):
    diff.append(postings[i] - postings[i-1])
  return VBEncode(diff)

def getPostings(s):
  postings = VBDecode(s)
  for i in range(1, len(postings)):
    postings[i] = postings[i-1] + postings[i]
  return postings