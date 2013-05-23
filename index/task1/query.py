#!/bin/env python
from collections import deque
import os, glob, os.path
import sys
import re
import time
import struct

if len(sys.argv) != 2:
  print >> sys.stderr, 'usage: python query.py index_dir' 
  os._exit(-1)

def merge_posting (postings1, postings2):
  intersect = []
  itr1 = 0
  itr2 = 0
  while itr1 < len(postings1) and itr2 < len(postings2):
    did1 = postings1[itr1]
    did2 = postings2[itr2]
    if did1 < did2:
      itr1 += 1
    elif did2 < did1:
      itr2 += 1
    else:
      intersect.append(did1)
      itr1 += 1
      itr2 += 1
  return intersect

# file locate of all the index related files
index_dir = sys.argv[1]
index_f = open(index_dir+'/corpus.index', 'rb')
word_dict_f = open(index_dir+'/word.dict', 'r')
doc_dict_f = open(index_dir+'/doc.dict', 'r')
posting_dict_f = open(index_dir+'/posting.dict', 'r')

word_dict = {}
doc_id_dict = {}
file_pos_dict = {}
doc_freq_dict = {}

print >> sys.stderr, 'loading word dict'
for line in word_dict_f.readlines():
  parts = line.split('\t')
  word_dict[parts[0]] = int(parts[1])
print >> sys.stderr, 'loading doc dict'
for line in doc_dict_f.readlines():
  parts = line.split('\t')
  doc_id_dict[int(parts[1])] = parts[0]
print >> sys.stderr, 'loading index'
for line in posting_dict_f.readlines():
  parts = line.split('\t')
  term_id = int(parts[0])
  file_pos = int(parts[1])
  doc_freq = int(parts[2])
  file_pos_dict[term_id] = file_pos
  doc_freq_dict[term_id] = doc_freq

def read_posting(term_id):
  index_f.seek(file_pos_dict[term_id])
  freq = doc_freq_dict[term_id]
  return struct.unpack('i' * freq, index_f.read(4 * freq))

# read query from stdin
while True:
  input = sys.stdin.readline()
  start_time = time.time()
  input = input.strip()
  if len(input) == 0: # end of file reached
    break
  input_parts = input.split()
  # a set containing (doc_frequency, term_id) pairs
  qset = set()
  for word in input_parts:
    if word not in word_dict:
      print "no results found"
      break
    word_id = word_dict[word]
    qset.add((doc_freq_dict[word_id], word_id))
  else:
    qset = sorted(qset) # order the terms by doc_frequency
    answer_list = read_posting(qset[0][1])
    for i in range(1,len(qset)):
      answer_list =  merge_posting(answer_list, read_posting(qset[i][1]))
      if not answer_list:
        print "no results found"
        break
    else:
      print '\n'.join(sorted(map(doc_id_dict.get, answer_list)))
  print >> sys.stderr, "Retrieval time " + str(time.time() - start_time)
  # you need to translate words into word_ids
  # don't forget to handle the case where query contains unseen words
  # next retrieve the postings list of each query term, and merge the posting lists
  # to produce the final result

  # posting = read_posting(word_id)

  # don't forget to convert doc_id back to doc_name, and sort in lexicographical order
  # before printing out to stdout
