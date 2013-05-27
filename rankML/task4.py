from math import log10, exp
from sklearn import linear_model, preprocessing

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

def train(docs, label_map):
  features = [extractFeatures(doc) for doc in docs]
  labels = [label_map[doc.query][doc.url] for doc in docs]
  return linear_model.Ridge(alpha=4.5).fit(features, labels)

def predict(model, doc):
  return model.predict(extractFeatures(doc))
