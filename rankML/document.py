from collections import Counter
from math import log10
import re

class Document():
  def __init__(self, query):
    self.query = query
    self.url = ''
    self.title = ''
    self.headers = []
    self.body_hits = {}
    self.anchors = []
    self.anchor_counts = []

    self.url_length = 0
    self.title_length = 0
    self.header_length = 0
    self.anchor_length = 0
    self.body_length = 0
    self.pagerank = 0
    
    self.avlen_url = 0
    self.avlen_title = 0
    self.avlen_header = 0
    self.avlen_body = 0
    self.avlen_anchor = 0
    
    self.query_terms = Counter(query.split())
    self.url_terms = Counter()
    self.title_terms = Counter()
    self.header_terms = Counter()
    self.anchor_terms = Counter()
  
  def set_title(self, title):
    title = title.lower()
    self.title = title
    title_tokens = title.split()
    self.title_length = len(title_tokens)
    self.title_terms = Counter(title_tokens)
  
  def set_url(self, url):
    self.url = url
    url_tokens = re.findall(r'[a-z0-9]+', url.lower())
    self.url_length = len(url_tokens)
    self.url_terms = Counter(url_tokens)
  
  def set_body_length(self, length):
    self.body_length = length
  
  def set_pagerank(self, rank):
    self.pagerank = rank
  
  def set_averages(self, avlen_url, avlen_title, avlen_header, avlen_body, avlen_anchor):
    self.avlen_url = avlen_url
    self.avlen_title = avlen_title
    self.avlen_header = avlen_header
    self.avlen_body = avlen_body
    self.avlen_anchor = avlen_anchor
  
  def add_header(self, header):
    header = header.lower()
    self.headers.append(header)
    header_tokens = header.split()
    self.header_length += len(header_tokens)
    self.header_terms.update(header_tokens)
  
  def add_body_hits(self, term, positions):
    term = term.lower()
    self.body_hits[term] = positions
  
  def add_anchor(self, anchor_text, count):
    anchor_text = anchor_text.lower()
    self.anchors.append(anchor_text)
    self.anchor_counts.append(count)
    for term in anchor_text.split():
      self.anchor_length += count
      self.anchor_terms[term] += count
  
  def make_vectors(self, doc_freq_dict):
    self.query_vec = []
    self.url_vec = []
    self.title_vec = []
    self.header_vec = []
    self.body_vec = []
    self.anchor_vec = []
    self.idf_vec = []
    
    for term in self.query_terms:
      self.query_vec.append(self.query_terms[term])
      self.url_vec.append(self.url_terms[term])
      self.title_vec.append(self.title_terms[term])
      self.header_vec.append(self.header_terms[term])
      self.body_vec.append(len(self.body_hits.get(term,[])))
      self.anchor_vec.append(self.anchor_terms[term])
      self.idf_vec.append(log10(98999/doc_freq_dict[term]))
