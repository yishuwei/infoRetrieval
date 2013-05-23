import os, sys, marshal
from math import log
from document import Document
import scorer

def parseTrainFile(trainFile):
    train_f = open(trainFile, 'r')
    queries = []
    docs = []
    query2docs = {}

    for line in train_f:
      key = line.split(':', 1)[0].strip()
      value = line.split(':', 1)[1].strip()
      if (key == 'query'):
        query = value
        queries.append(query)
        query2docs[query] = []
      elif (key == 'url'):
        doc = Document(query)
        docs.append(doc)
        query2docs[query].append(doc)
        doc.set_url(value)
      elif (key == 'title'):
        doc.set_title(value)
      elif (key == 'header'):
        doc.add_header(value)
      elif (key == 'body_hits'):
        temp = value.split(' ', 1)
        doc.add_body_hits(temp[0].strip(), map(int, temp[1].strip().split()))
      elif (key == 'body_length'):
        doc.set_body_length(int(value))
      elif (key == 'pagerank'):
        doc.set_pagerank(int(value))
      elif (key == 'anchor_text'):
        anchor_text = value
      elif (key == 'stanford_anchor_count'):
        doc.add_anchor(anchor_text, int(value))
    train_f.close()    
    
    doc_count = len(docs)
    avlen_url = sum(doc.url_length for doc in docs) / doc_count
    avlen_title = sum(doc.title_length for doc in docs) / doc_count
    avlen_header = sum(doc.header_length for doc in docs) / doc_count
    avlen_body = sum(doc.body_length for doc in docs) / doc_count
    avlen_anchor = sum(doc.anchor_length for doc in docs) / doc_count
        
    with open('DocFreqDict', 'rb') as doc_freq_f:
      doc_freq_dict = marshal.load(doc_freq_f)
    for doc in docs:
      doc.set_averages(avlen_url, avlen_title, avlen_header, avlen_body, avlen_anchor)
      doc.make_vectors(doc_freq_dict)

    return queries, query2docs

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print >> sys.stderr, 'usage: python rank.py <taskId> <inputDataFile>' 
    os._exit(-1)
  taskId = int(sys.argv[1])
  get_score = scorer.cosine_score
  if taskId == 2:
    get_score = scorer.BM25F_score
  if taskId == 3:
    get_score = scorer.smallest_window_score
  
  queries, query2docs = parseTrainFile(sys.argv[2])
  for query in queries:
    docs = query2docs[query]
    scored_docs = []
    for doc in docs:
      score = get_score(doc)
      scored_docs.append((score, doc))
    scored_docs.sort(reverse = True)
    
    print 'query: ' + query
    for score, doc in scored_docs:
      print '  url: ' + doc.url