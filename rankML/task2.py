from math import log10, exp
from sklearn import svm, preprocessing
import itertools

def sublinear_number_scaling(n):
  if n == 0:
    return 0.0
  else:
    return (1.0 + log10(n))

def sublinear_vector_scaling(v):
  return map(sublinear_number_scaling, v)

def dot_product(v1, v2):
  if len(v1) !=len(v2):
    raise ValueError, "vectors are of different length"
  return sum(x * y for x, y in zip(v1, v2))

def vec_difference(v1, v2):
  if len(v1) !=len(v2):
    raise ValueError, "vectors are of different length"
  return [x - y for x, y in zip(v1, v2)]

def normalize(v, norm):
  return [float(x) / norm for x in v]

def extractFeatures(doc):
  qv = [tf * idf for tf,idf in zip(doc.query_vec, doc.idf_vec)]
  tf_url = sublinear_vector_scaling(doc.url_vec)
  tf_title = sublinear_vector_scaling(doc.title_vec)
  tf_header = sublinear_vector_scaling(doc.header_vec)
  tf_body = sublinear_vector_scaling(doc.body_vec)
  tf_anchor = sublinear_vector_scaling(doc.anchor_vec)
  normL1 = doc.body_length + 5000
  return normalize([dot_product(qv, tf_url), dot_product(qv, tf_title), dot_product(qv, tf_header), dot_product(qv, tf_body), dot_product(qv, tf_anchor)], normL1)

def train(docs, query2docs, label_map):
  scaler = preprocessing.Scaler().fit([extractFeatures(doc) for doc in docs]) # scaler.transform will standardize the data
  
  X_train = []
  y_train = []
  for query in query2docs:
    qdocs = query2docs[query]
    features = scaler.transform([extractFeatures(doc) for doc in qdocs])
    for i, j in itertools.permutations(range(len(qdocs)), 2):
      doc_i = qdocs[i]
      doc_j = qdocs[j]
      label = cmp(label_map[doc_i.query][doc_i.url], label_map[doc_j.query][doc_j.url])
      if label != 0:
        X_train.append(vec_difference(features[i], features[j]))
        y_train.append(label)
  model = svm.SVC(kernel='linear', C=3.0).fit(X_train, y_train)
  return scaler, model

def predict(scaler, model, doc):
  weights = model.coef_[0]
  return dot_product(weights, scaler.transform(extractFeatures(doc)))
