import os, sys, marshal
from math import log
from document import Document
import ndcg

def buildLabelMap(trainRelFile):
  label_map = {}
  for (query, results) in ndcg.getQueries(trainRelFile):
    query = query.split(' ', 1)[1].strip()
    label_map[query] = {}
    for res in results:
      temp = res.rsplit(' ', 1)
      url = temp[0].split(' ', 1)[1].strip()
      rel = float(temp[1].strip())
      label_map[query][url] = rel
  return label_map

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

    return queries, docs, query2docs

if __name__ == '__main__':
  if len(sys.argv) != 5:
    print >> sys.stderr, "Usage:", sys.argv[0], "train_data_file train_rel_file test_data_file task"
    os._exit(-1)
  
  taskId = int(sys.argv[4])
  train_queries, train_docs, train_query2docs = parseTrainFile(sys.argv[1])
  test_queries, test_docs, test_query2docs = parseTrainFile(sys.argv[3])
  
  if taskId == 1:
    import task1 as learner
    model = learner.train(train_docs, buildLabelMap(sys.argv[2]))
  elif taskId == 2:
    import task2 as learner
    scaler, model = learner.train(train_docs, train_query2docs, buildLabelMap(sys.argv[2]))
  elif taskId == 3:
    import task3 as learner
    scaler, model = learner.train(train_docs, train_query2docs, buildLabelMap(sys.argv[2]))
  elif taskId == 4:
    import task4 as learner
    model = learner.train(train_docs, buildLabelMap(sys.argv[2]))

  # some debug output
  print >> sys.stderr, "Weights:", str(model.coef_)
  
  for query in test_queries:
    docs = test_query2docs[query]
    scored_docs = []
    for doc in docs:
      if taskId == 1 or taskId == 4:
        score = learner.predict(model, doc)
      else:
        score = learner.predict(scaler, model, doc)
      scored_docs.append((score, doc))
    scored_docs.sort(reverse = True)
    
    print 'query: ' + query
    for score, doc in scored_docs:
      print '  url: ' + doc.url
