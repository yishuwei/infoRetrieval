import marshal

word_dict_f = open('../PA1/output/index/word.dict', 'r')
posting_dict_f = open('../PA1/output/index/posting.dict', 'r')
query_terms_f = open('AllQueryTerms', 'r')

word_dict = {}
doc_freq_dict = {}
doc_freq_dict_full = {}

for line in word_dict_f:
  parts = line.split('\t')
  word_dict[parts[0]] = int(parts[1])
for line in posting_dict_f:
  parts = line.split('\t')
  term_id = int(parts[0])
  doc_freq = int(parts[2])
  doc_freq_dict_full[term_id] = doc_freq
for line in query_terms_f:
  term = line.strip()
  if term in word_dict:
    doc_freq_dict[term] = doc_freq_dict_full[word_dict[term]] + 1
  else:
    doc_freq_dict[term] = 1
word_dict_f.close()
posting_dict_f.close()
query_terms_f.close()

with open('DocFreqDict', 'wb') as ufile:
  marshal.dump(doc_freq_dict, ufile)