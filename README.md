# News to Medical EDU Segmentation
This repository includes:
* a corpus of medical articles segmeted into EDUs, [following these guidelines](https://www.isi.edu/~marcu/discourse/tagging-ref-manual.pdf) (from RST-DT)
* code for preprocessing, postprocessing, evaluation

Please cite our NAACL DISRPT Workshop paper as:
> @inproceedings{Ferracane:2019,
  title={From News to Medical: Cross-domain Discourse Segmentation},
  author={Ferracane, Elisa and Page, Titan and Li, Junyi Jessy and Erk, Katrin},
  booktitle={Proceedings of the 7th Workshop on Rhetorical Structure Theory and Related Formalisms},
  publisher ="Association for Computational Linguistics",
  pages={in press},
  year={2019}
}

## Corpus:
Raw data is in [data/raw](data/raw)

Gold segmented data is in [data/gold](data/gold)

Notes:
* [data/rst-dt_tiny_file_list.txt](data/rst-dt_tiny_file_list.txt) contains list of files used from [RST-DT](https://catalog.ldc.upenn.edu/LDC2002T07) (we only provide samples due to licensing)
* version of gold data used in paper is in [data/gold_paper](data/gold_paper)


## Segmentation:
We use three publicly available RST segmenters to segment the raw data. 

#### 1. Neural EDU Segmenter
1. get code and requirements from here: https://github.com/PKU-TANGENT/NeuralEDUSeg
1. segment: `python run.py --segment --input_files <this_repo>/data/gold/*.out --result_dir <this_repo>/data/segmented/predicted_neural`
1. rename files: 
```
cd <this_repo>/data/segmented/predicted_neural  
for f in *.out; do 
 mv -- "$f" "${f}.edus" 
done
```

#### 2. Two-pass Feng Parser
1. download [code and requirements](https://github.com/elisaF/rst_discourse_parser) to <feng_parser_dir>
1. update to newer version of Stanford Core NLP:  
   1. download and unzip Stanford Core NLP to <stanford_corenlp_dir>: `curl -O https://nlp.stanford.edu/software/stanford-corenlp-full-2018-10-17.zip`
   1. download and unzip Stanford parser to <stanford_parser_dir>: `curl -O https://nlp.stanford.edu/software/stanford-parser-full-2018-10-17.zip`
   1. modify paths in <feng_parser_dir>/src/paths.py to point to <stanford_corenlp_dir> and <stanford_parser_dir> 
   1. replace ParserDemo.java in <stanford_parser_dir> with our version [here](code/ParserDemo.java)
   1. compile new java file: `javac -cp ".:*" ParserDemo.java`
1. run parser: `python parse.py -s -g -t <this_repo>/data/segmented/predicted_feng/ -D <this_repo>/data/file_list.txt`
1. postprocess predicted EDU files: `python parse_predicted.py feng ../data/segmented/predicted_feng/ ../data/segmented/postprocessed_feng/`

#### 3. DPLP Parser
1. download [code and requirements](https://github.com/jiyfeng/DPLP)
1. run DPLP parser:  
   1. use our version of [corenlp.sh](data/corenlp_raw.sh) to parse the input:
	 `./corenlp_raw.sh <stanford_corenlp_dir> ../data/raw/ ../data/segmented/preprocessed_dplp/`
   1. 	`python convert.py <this_repo>/data/segmented/preprocessed_dplp/`
   1. `python segmenter.py <this_repo>/data/segmented/preprocessed_dplp/ <this_repo>/data/segmented/predicted_dplp/`
1. postprocess predicted EDU files: `python parse_predicted.py dplp ../data/segmented/predicted_dplp/ ../data/segmented/postprocessed_dplp/`

## Evaluation
`python evaluate_segmentation.py ../data/gold/postprocessed/stanford/ ../data/gold/postprocessed/spacy/ ../data/segmented/postprocessed_dplp/ ../data/segmented/postprocessed_feng/ ../data/segmented/predicted_neural/`

## Update segmented gold data
If the segmented gold data is updated, follow these steps to reprocess:
1. `python parse_gold.py edu ../data/gold/ ../data/gold/postprocessed/spacy/ spacy`
1. `./corenlp_segmented.sh <stanford_corenlp_dir> ../data/gold/ ../data/gold/postprocessed/stanford/`
1. `python parse_gold.py edu ../data/gold/postprocessed/stanford ../data/gold/postprocessed/stanford/ stanford`
