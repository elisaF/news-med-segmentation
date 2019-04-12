from bs4 import BeautifulSoup
from collections import defaultdict
from os.path import join
import os
import re
import spacy
from sys import argv


RS3_SUFFIX = ".rs3"


def main(parse_option, input_dir, output_dir, source_edu):
    if parse_option == 'rs3':
        parse_rs3(input_dir, output_dir)
    elif parse_option == 'edu':
        if source_edu == 'spacy':
            parse_edu_spacy(input_dir, output_dir)
        elif source_edu == 'stanford':
            parse_edu_stanford(input_dir, output_dir)
        else:
            raise ValueError("Invalid source edu", source_edu, " must be spacy or stanford.")
    else:
        raise ValueError("Invalid parse option ", parse_option, " must be rs3 or edu.")


def parse_rs3(input_dir, output_dir):
    for file_name in os.listdir(input_dir):
        if file_name.endswith(RS3_SUFFIX):
            with open(join(input_dir, file_name)) as f_in:
                soup = BeautifulSoup(f_in)
                segments = soup("segment")
                edus = "\n".join([segment.text for segment in segments])

            # write EDUs to output file
            output_file_name = ".".join(file_name.split(".")[:-1])  # strip off suffix
            with open(join(output_dir, output_file_name), "w") as f_out:
                f_out.write(edus)


def parse_edu_stanford(input_dir, output_dir):
    for file_name in os.listdir(input_dir):
        edus = []
        if file_name.endswith("xml"):
            with open(join(input_dir, file_name)) as f_in:
                soup = BeautifulSoup(f_in)
                sents = soup("sentence")
                for sent in sents:
                    edu = " ".join([word.get_text() for word in sent.find_all('word')])
                    edus.append(edu)
            edus = "\n".join([edu.rstrip("\n") for edu in edus])
            # write EDUs to output file
            output_file_name = ".".join(file_name.split(".")[:-1])  # strip off suffix
            with open(join(output_dir, output_file_name), "w") as f_out:
                f_out.write(edus)


def parse_edu_spacy(input_dir, output_dir):
    spacy_nlp = spacy.load('en', disable=['parser', 'ner', 'textcat'])
    for file_name in os.listdir(input_dir):
        edus = []
        if file_name.endswith("edus"):
            with open(join(input_dir, file_name)) as f_in:
                lines = f_in.readlines()
                for line in lines:
                    line = line.lstrip(" ")
                    line = line.rstrip("\n")
                    parsed_line = spacy_nlp(line)
                    edus.append(" ".join([token.text for token in parsed_line]))
                edus = "\n".join(edus)
                # write EDUs to output file
                with open(join(output_dir, file_name), "w") as f_out:
                    f_out.write(edus)


if __name__ == '__main__':
    source_edu = None
    if len(argv) == 4 or len(argv) == 5:
        parse_option = argv[1]
        input_dir = argv[2]
        output_dir = argv[3]

        if len(argv) == 5:
            source_edu = argv[4]
        main(parse_option, input_dir, output_dir, source_edu)

    else:
        print('python rs3|edu input_path output_path <source_edu=stanford|spacy>')
