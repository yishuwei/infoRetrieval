#!/bin/env python
from collections import deque
import os, glob, os.path
import sys
import re
import vb

if len(sys.argv) != 3:
  print >> sys.stderr, 'usage: python index.py data_dir output_dir' 
  os._exit(-1)

total_file_count = 0
root = sys.argv[1]
out_dir = sys.argv[2]
if not os.path.exists(out_dir):
  os.makedirs(out_dir)

# this is the actual posting lists dictionary
posting_dict = {}
# this is a dict holding document name -> doc_id
doc_id_dict = {}
# this is a dict holding word -> word_id
word_dict = {}
# this is a queue holding block names, later used for merging blocks
block_q = deque()
# this is a queue of posting lists dictionaries
dict_q = deque()

# function to count number of files in collection
def count_file():
  global total_file_count
  total_file_count += 1

# function for printing a line in a postings list to a given file
def print_posting(file, posting_line, tid, block_dict):
  if not posting_line:
    return
  block_dict[tid] = (file.tell(), len(posting_line))
  file.write(vb.convertPostings(posting_line))
  
# function for merging two lines of postings list to create a new line of merged results
def merge_posting(line1, line2):
  itr1 = 0
  itr2 = 0
  merge = []
  while itr1 < len(line1) and itr2 < len(line2):
    did1 = line1[itr1]
    did2 = line2[itr2]
    if did1 < did2:
      merge.append(did1)
      itr1 += 1
    else:
      merge.append(did2)
      itr2 += 1
  while itr1 < len(line1):
    merge.append(line1[itr1])
    itr1 += 1
  while itr2 < len(line2):
    merge.append(line2[itr2])
    itr2 += 1
  return merge


doc_id = 0
word_id = 0

for dir in sorted(os.listdir(root)):
  print >> sys.stderr, 'processing dir: ' + dir
  dir_name = os.path.join(root, dir)
  block_pl_name = out_dir+'/'+dir 
  # append block names to a queue, later used in merging
  block_q.append(dir)
  block_pl = open(block_pl_name, 'wb')
  term_doc_list = []
  for f in sorted(os.listdir(dir_name)):
    count_file()
    file_id = os.path.join(dir, f)
    doc_id += 1
    doc_id_dict[file_id] = doc_id
    fullpath = os.path.join(dir_name, f)
    file = open(fullpath, 'r')
    for line in file.readlines():
      tokens = line.strip().split()
      for token in tokens:
        if token not in word_dict:
          word_dict[token] = word_id
          word_id += 1
        term_doc_list.append( (word_dict[token], doc_id) )
    file.close()
  print >> sys.stderr, 'sorting term doc list for dir:' + dir
  # sort term doc list
  term_doc_list.sort()
  print >> sys.stderr, 'print posting list to disc for dir:' + dir
  # write the posting lists to block_pl for this current block
  newdict = {}
  line = []
  current_term_id = term_doc_list[0][0]
  current_doc_id = 0
  for (tid, did) in term_doc_list:
    if tid != current_term_id:
      print_posting(block_pl, line, current_term_id, newdict)
      current_term_id = tid
      current_doc_id = 0
      line = []
    if did != current_doc_id:
      line.append(did)
      current_doc_id = did
  print_posting(block_pl, line, current_term_id, newdict)
  block_pl.close()
  dict_q.append(newdict)

print >> sys.stderr, '######\nposting list construction finished!\n##########'

print >> sys.stderr, '\nMerging postings...'
while True:
  if len(block_q) <= 1:
    break
  b1 = block_q.popleft()
  b2 = block_q.popleft()
  dict1 = dict_q.popleft()
  dict2 = dict_q.popleft()
  print >> sys.stderr, 'merging %s and %s' % (b1, b2)
  b1_f = open(out_dir+'/'+b1, 'rb')
  b2_f = open(out_dir+'/'+b2, 'rb')
  comb = b1+'+'+b2
  comb_f = open(out_dir + '/'+comb, 'wb')
  # (provide implementation merging the two blocks of posting lists)
  b1_tids = sorted(dict1.keys())
  b2_tids = sorted(dict2.keys())
  ptr1 = 0
  ptr2 = 0
  newdict = {}
  while ptr1 < len(b1_tids) and ptr2 < len(b2_tids):
    tid1 = b1_tids[ptr1]
    tid2 = b2_tids[ptr2]
    line1 = []
    line2 = []
    start_pos1 = dict1[tid1][0]
    start_pos2 = dict2[tid2][0]
    b1_f.seek(start_pos1)
    b2_f.seek(start_pos2)
    
    if (ptr1 + 1) == len(b1_tids):
      line1 = vb.getPostings(b1_f.read())
    else:
      line1 = vb.getPostings(b1_f.read(dict1[b1_tids[ptr1 + 1]][0] - start_pos1))
    
    if (ptr2 + 1) == len(b2_tids):
      line2 = vb.getPostings(b2_f.read())
    else:
      line2 = vb.getPostings(b2_f.read(dict2[b2_tids[ptr2 + 1]][0] - start_pos2))
    
    if tid1 < tid2:
      print_posting(comb_f, line1, tid1, newdict)
      ptr1 += 1
    elif tid2 < tid1:
      print_posting(comb_f, line2, tid2, newdict)
      ptr2 += 1
    else:
      print_posting(comb_f, merge_posting(line1, line2), tid1, newdict)
      ptr1 += 1
      ptr2 += 1
  while ptr1 < len(b1_tids):
    tid1 = b1_tids[ptr1]
    line1 = []
    start_pos1 = dict1[tid1][0]
    b1_f.seek(start_pos1)
    if (ptr1 + 1) == len(b1_tids):
      line1 = vb.getPostings(b1_f.read())
    else:
      line1 = vb.getPostings(b1_f.read(dict1[b1_tids[ptr1 + 1]][0] - start_pos1))
    print_posting(comb_f, line1, tid1, newdict)
    ptr1 += 1
  while ptr2 < len(b2_tids):
    tid2 = b2_tids[ptr2]
    line2 = []
    start_pos2 = dict2[tid2][0]
    b2_f.seek(start_pos2)
    if (ptr2 + 1) == len(b2_tids):
      line2 = vb.getPostings(b2_f.read())
    else:
      line2 = vb.getPostings(b2_f.read(dict2[b2_tids[ptr2 + 1]][0] - start_pos2))
    print_posting(comb_f, line2, tid2, newdict)
    ptr2 += 1

  b1_f.close()
  b2_f.close()
  comb_f.close()
  os.remove(out_dir+'/'+b1)
  os.remove(out_dir+'/'+b2)
  block_q.append(comb)
  dict_q.append(newdict)
    
print >> sys.stderr, '\nPosting Lists Merging DONE!'

# rename the final merged block to corpus.index
final_name = block_q.popleft()
os.rename(out_dir+'/'+final_name, out_dir+'/corpus.index')

posting_dict = dict_q.popleft()

# print all the dictionary files
doc_dict_f = open(out_dir + '/doc.dict', 'w')
word_dict_f = open(out_dir + '/word.dict', 'w')
posting_dict_f = open(out_dir + '/posting.dict', 'w')
print >> doc_dict_f, '\n'.join( ['%s\t%d' % (k,v) for (k,v) in sorted(doc_id_dict.iteritems(), key=lambda(k,v):v)])
print >> word_dict_f, '\n'.join( ['%s\t%d' % (k,v) for (k,v) in sorted(word_dict.iteritems(), key=lambda(k,v):v)])
print >> posting_dict_f, '\n'.join(['%s\t%s' % (k,'\t'.join([str(elm) for elm in v])) for (k,v) in sorted(posting_dict.iteritems(), key=lambda(k,v):v)])
doc_dict_f.close()
word_dict_f.close()
posting_dict_f.close()

print total_file_count
