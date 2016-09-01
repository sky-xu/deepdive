# sudo apt-get update
# sudo apt-get upgrade
# sudo apt-get install git

# Run the following command to install Postgres and DeepDive.
bash <(curl -fsSL deepdive.stanford.edu/install)  postgres deepdive

# Optionally, you can run tests to confirm that the installation was successful.
bash <(curl -fsSL deepdive.stanford.edu/install)  run_deepdive_tests

# To set the location of this database, we need to configure a URL in the db.url file, e.g.:
# echo "postgresql://$USER@$HOSTNAME:5432/deepdive_spouse_$USER" >db.url
echo "postgresql://localhost/deepdive_employ_$USER" >db.url

export PATH=~/local/bin:"$PATH"


# copy app.ddlog and deepdive.conf over


deepdive create table articles
deepdive load articles input/articles-1000.tsv.bz2
deepdive mark done articles
# to verify
deepdive query '?- articles(id, _).'

deepdive create table sentences
deepdive load sentences input/sentences-1000.tsv.bz2
deepdive mark done sentences
# to verify:
deepdive query '
    doc_id, index, tokens, ner_tags | 5
    ?- sentences(doc_id, index, text, tokens, lemmas, pos_tags, ner_tags, _, _, _).
'

deepdive do person_mention
# to verify:
deepdive query '
    name, doc, sentence, begin, end | 20
    ?- person_mention(p_id, name, doc, sentence, begin, end).
'

deepdive do spouse_candidate
# to verify:
deepdive query '
    name1, name2, doc, sentence | 20
    ?- spouse_candidate(p1, name1, p2, name2),
       person_mention(p1, _, doc, sentence, _, _).
'

deepdive do spouse_feature
# to verify:
deepdive query '| 20 ?- spouse_feature(_, _, feature).'

deepdive do spouses_dbpedia
# to verify:
deepdive query '| 20 ?- spouses_dbpedia(name1, name2).'

deepdive compile && deepdive do work_for
# to verify:
deepdive query 'rule, @order_by COUNT(1) ?- spouse_label(p1,p2, label, rule).'

deepdive do probabilities
# to verify:
deepdive sql "SELECT p1_id, p2_id, expectation FROM work_for_label_inference ORDER BY random() LIMIT 20"

deepdive do calibration-plots

mindbender search update
mindbender search gui

deepdive sql eval "
SELECT hsi.p1_id
     , hsi.p2_id
     , s.doc_id
     , s.sentence_index
     , hsi.label
     , hsi.expectation
     , s.tokens
     , pm1.mention_text AS p1_text
     , pm1.begin_index  AS p1_start
     , pm1.end_index    AS p1_end
     , pm2.mention_text AS p2_text
     , pm2.begin_index  AS p2_start
     , pm2.end_index    AS p2_end

  FROM work_for_label_inference hsi
     , person_mention             pm1
     , person_mention             pm2
     , sentences                  s

 WHERE hsi.p1_id          = pm1.mention_id
   AND pm1.doc_id         = s.doc_id
   AND pm1.sentence_index = s.sentence_index
   AND hsi.p2_id          = pm2.mention_id
   AND pm2.doc_id         = s.doc_id
   AND pm2.sentence_index = s.sentence_index
   AND       expectation >= 0.9

 ORDER BY random()
 LIMIT 100

" format=csv header=1 >labeling/work_for-precision/work_for.csv

mindbender tagger labeling/work_for-precision/mindtagger.conf
