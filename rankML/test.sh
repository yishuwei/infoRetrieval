python rank.py queryDocTrainData.train queryDocTrainRel.train queryDocTrainData.dev $1 > ranked$1.dev
python ndcg.py ranked$1.dev queryDocTrainRel.dev
