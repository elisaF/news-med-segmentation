#!/usr/bin/env bash
#
# Runs Stanford CoreNLP.
# Simple uses for xml and plain text output to files are:
#    ./corenlp.sh -file filename
#    ./corenlp.sh -file filename -outputFormat text 

# echo java -mx3g -cp \"$scriptdir/*\" edu.stanford.nlp.pipeline.StanfordCoreNLP $*

STANFORD_DIR=$1
INPUT=$2
SAVE=$3
for FNAME in $INPUT/*.out
do
    /usr/bin/java --add-modules java.xml.bind -Xms8g -Xmx32g -cp "$STANFORD_DIR/*" edu.stanford.nlp.pipeline.StanfordCoreNLP true -tokenize.options "strictTreebank3=true" -annotators tokenize,ssplit,pos,lemma,ner,parse -file $FNAME
    /bin/mv $(/usr/bin/basename $FNAME.xml) $SAVE/
done
