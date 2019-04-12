from bs4 import BeautifulSoup
from collections import defaultdict
from os.path import join
import os
import re
from sys import argv


EDU_DPLP_SUFFIX = ".merge"
EDU_FENG_SUFFIX = ".edus"


def main(source_edu, input_dir, output_dir):
    if source_edu == 'dplp':
            parse_edu_dplp(input_dir, output_dir)
    elif source_edu == 'feng':
        parse_edu_feng(input_dir, output_dir)
    else:
        raise ValueError("Invalid source edu", source_edu, " must be dplp or feng.")


def parse_edu_dplp(input_dir, output_dir):
    for file_name in os.listdir(input_dir):
        edu_to_tokens = defaultdict(list)
        if file_name.endswith(EDU_DPLP_SUFFIX):
            with open(join(input_dir, file_name)) as f_in:
                lines = f_in.readlines()
            for line in lines:
                if len(line) > 1:
                    tabs = line.split("\t")
                    token = tabs[2]
                    edu_num = tabs[-1]
                    edu_to_tokens[edu_num].append(token)
            # fix up tokenization issue when handling raw vs. segmented input
            for edu_num, tokens in edu_to_tokens.items():
                last_token = tokens[-1].rstrip("\n")
                if last_token.lower() == "corp.":
                    tokens[-1] = last_token.split(".")[0] + " ."
                    edu_to_tokens[edu_num] = tokens
            edus = "\n".join([" ".join(tokens).rstrip("\n") for tokens in edu_to_tokens.values()])
            # write EDUs to output file
            output_file_name = ".".join(file_name.split(".")[:-1])+".edus"  # strip off suffix
            with open(join(output_dir, output_file_name), "w") as f_out:
                f_out.write(edus)


def parse_edu_feng(input_dir, output_dir):
    for file_name in os.listdir(input_dir):
        edus = []
        if file_name.endswith(EDU_FENG_SUFFIX):
            with open(join(input_dir, file_name)) as f_in:
                lines = f_in.readlines()
                for line in lines:
                    line = line.replace("EDU_BREAK ", "\n")
                    edus.append(line)
                edus = "\n".join(edu.rstrip("\n") for edu in edus)
                # write EDUs to output file
                with open(join(output_dir, file_name), "w") as f_out:
                    f_out.write(edus)


if __name__ == '__main__':
    if len(argv) == 4:
        source_edu = argv[1]
        input_dir = argv[2]
        output_dir = argv[3]
        main(source_edu, input_dir, output_dir)
    else:
        print('python dplp|feng input_path output_path')
