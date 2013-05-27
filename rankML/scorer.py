# Implementations of the three scoring functions.

"""
Tune the parameters here.
"""
# parameters for cosine score
c1 = 1; c2 = 4; c3 = 4; c4 = 2; c5 = 400; length_smooth = 15000

# parameters for BM25F score
B1 = 0.99; B2 = 0.3; B3 = 0.1; B4 = 0.3; B5 = 0.01
W1 = 18; W2 = 59; W3 = 17; W4 = 1; W5 = 15
lambda1 = 1; K1 = 7

# parameters for smallest window score
c1s = 1; c2s = 4; c3s = 4; c4s = 2; c5s = 400; length_smooth_s = 15000; B = 2.7

from math import log10, exp
from collections import Counter
import re

def sublinear_number_scaling(n):
  if n == 0:
    return 0.0
  else:
    return (1.0 + log10(n))

def sublinear_vector_scaling(v):
  return map(sublinear_number_scaling, v)

def sigmoid(n):
  return 1/(1 + exp(-n))

def dot_product(v1, v2):
  if len(v1) !=len(v2):
    raise ValueError, "vectors are of different length"
  return sum(x * y for x, y in zip(v1, v2))

def cosine_score(doc):
  qv = [tf * idf for tf,idf in zip(sublinear_vector_scaling(doc.query_vec), doc.idf_vec)]
  tf_url = sublinear_vector_scaling(doc.url_vec)
  tf_title = sublinear_vector_scaling(doc.title_vec)
  tf_header = sublinear_vector_scaling(doc.header_vec)
  tf_body = sublinear_vector_scaling(doc.body_vec)
  tf_anchor = sublinear_vector_scaling(doc.anchor_vec)
  dv = [(c1*tf1 + c2*tf2 + c3*tf3 + c4*tf4 + c5*tf5) / (doc.body_length + length_smooth)
         for tf1,tf2,tf3,tf4,tf5 in zip(tf_url, tf_title, tf_header, tf_body, tf_anchor)]
  return dot_product(qv, dv)

def BM25F_score(doc):
  norm_url = 1 + B1 * (doc.url_length/doc.avlen_url - 1)
  norm_title = 1 + B2 * (doc.title_length/doc.avlen_title - 1)
  norm_header = 1 + B3 * (doc.header_length/doc.avlen_header - 1)
  norm_body = 1 + B4 * (doc.body_length/doc.avlen_body - 1)
  norm_anchor = 1 + B5 * (doc.anchor_length/doc.avlen_anchor - 1)
  ftf_url = [t/norm_url for t in doc.url_vec]
  ftf_title = [t/norm_title for t in doc.title_vec]
  ftf_header = [t/norm_header for t in doc.header_vec]
  ftf_body = [t/norm_body for t in doc.body_vec]
  ftf_anchor = [t/norm_anchor for t in doc.anchor_vec]
  weight_vec = [(W1*ftf1 + W2*ftf2 + W3*ftf3 + W4*ftf4 + W5*ftf5)
                 for ftf1,ftf2,ftf3,ftf4,ftf5 in zip(ftf_url, ftf_title, ftf_header, ftf_body, ftf_anchor)]
  dv = [w/(K1 + w)for w in weight_vec]
  return dot_product(dv, doc.idf_vec) #+ lambda1 * log10(doc.pagerank + 1)
  #return dot_product(dv, doc.idf_vec) + lambda1 * sigmoid(doc.pagerank)

def smallest_window_score(doc):
  w = float('inf')
  qterms = doc.query.split()
  
  w = min(w, sequence_min_window_size(doc.title.split(), qterms),
             sequence_min_window_size(re.findall(r'[a-z0-9]+', doc.url.lower()), qterms),
             hits_min_window_size(doc.body_hits, qterms))
  for header in doc.headers:
    w = min(w, sequence_min_window_size(header.split(), qterms))
  for anchor_text in doc.anchors:
    w = min(w, sequence_min_window_size(anchor_text.split(), qterms))
  
  qv = [tf * idf for tf,idf in zip(sublinear_vector_scaling(doc.query_vec), doc.idf_vec)]
  tf_url = sublinear_vector_scaling(doc.url_vec)
  tf_title = sublinear_vector_scaling(doc.title_vec)
  tf_header = sublinear_vector_scaling(doc.header_vec)
  tf_body = sublinear_vector_scaling(doc.body_vec)
  tf_anchor = sublinear_vector_scaling(doc.anchor_vec)
  dv = [(c1s*tf1 + c2s*tf2 + c3s*tf3 + c4s*tf4 + c5s*tf5) / (doc.body_length + length_smooth_s)
         for tf1,tf2,tf3,tf4,tf5 in zip(tf_url, tf_title, tf_header, tf_body, tf_anchor)]
  return (len(qterms)/float(w) * (B - 1) + 1) * dot_product(qv, dv)

def sequence_min_window_size(sequence, terms):
  terms = set(terms)
  n = len(sequence)
  
  start = 0
  terms_in_window = Counter()
  num_unseen_terms = len(terms)
  for end in range(n):
    term = sequence[end]
    if term in terms:
      if terms_in_window[term] == 0:
        num_unseen_terms -= 1
      terms_in_window[term] += 1
    if num_unseen_terms == 0:
      break
  else:
    return float('inf')
  
  start_term = sequence[start]
  while terms_in_window[start_term] > 1 or start_term not in terms:
    if terms_in_window[start_term] > 1:
      terms_in_window[start_term] -= 1
    start += 1
    start_term = sequence[start]
  
  win_size = end - start + 1
  if end < n - 1:
    for march in range(end + 1, n):
      term = sequence[march]
      if term in terms:
        terms_in_window[term] += 1
      while terms_in_window[start_term] > 1 or start_term not in terms:
        if terms_in_window[start_term] > 1:
          terms_in_window[start_term] -= 1
        start += 1
        start_term = sequence[start]
      if march - start + 1 < win_size:
        win_size = march - start + 1
  return win_size

def hits_min_window_size(hit_map, terms):
  terms = set(terms)
  for term in terms:
    if term not in hit_map:
      return float('inf')
  
  all_positions = []
  tid = 1
  for term in terms:
    all_positions.extend((pos, tid) for pos in hit_map[term])
    tid += 1
  all_positions.sort()
  n = len(all_positions)
  
  start_ptr = 0
  terms_in_window = Counter()
  num_unseen_terms = len(terms)
  for end_ptr in range(n):
    tid = all_positions[end_ptr][1]
    if terms_in_window[tid] == 0:
      num_unseen_terms -= 1
    terms_in_window[tid] += 1
    if num_unseen_terms == 0:
      break
  else:
    return float('inf')
  
  start_tid = all_positions[start_ptr][1]
  while terms_in_window[start_tid] > 1:
    terms_in_window[start_tid] -= 1
    start_ptr += 1
    start_tid = all_positions[start_ptr][1]
  
  win_size = all_positions[end_ptr][0] - all_positions[start_ptr][0] + 1
  if end_ptr < n - 1:
    for march in range(end_ptr + 1, n):
      tid = all_positions[march][1]
      terms_in_window[tid] += 1
      while terms_in_window[start_tid] > 1:
        terms_in_window[start_tid] -= 1
        start_ptr += 1
        start_tid = all_positions[start_ptr][1]
      if all_positions[march][0] - all_positions[start_ptr][0] + 1 < win_size:
        win_size = all_positions[march][0] - all_positions[start_ptr][0] + 1
  return win_size
