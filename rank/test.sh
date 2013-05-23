python rank.py $1 queryDocTrainData > ranked
python ndcg.py ranked queryDocTrainRel
rm -f ranked
