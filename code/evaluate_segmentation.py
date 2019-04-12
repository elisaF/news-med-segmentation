from itertools import chain
import sys
from os import listdir
from os.path import basename, isfile, join

EDU_MARKER = "<edu_split>"


def get_files(_dir):
    return [join(_dir, f) for f in listdir(_dir) if isfile(join(_dir, f)) and f.endswith("edus")]


def get_counts(gold_dict):
    num_edus = 0
    num_tokens = 0

    for doc in gold_dict.keys():
        tokens = gold_dict[doc]
        num_tokens += len(tokens)
        num_edus += len([token for token in tokens if EDU_MARKER in token])
    return num_edus, num_tokens


def read_tokens(_dir):
    doc_to_tokens_med = {}
    doc_to_tokens_news = {}

    for file_name in get_files(_dir):
        doc_name = basename(file_name).split(".")[0]
        tokens = []
        with open(file_name) as f:
            for line in f:
                line = line.lstrip(" ")
                line = line.rstrip("\n ")
                tokens.extend([token for token in line.split(" ") if len(token) > 0 and token != "\n"])
                tokens[-1] = tokens[-1]+EDU_MARKER
            if doc_name.startswith("PMC"):
                doc_to_tokens_med[doc_name] = tokens
            else:
                doc_to_tokens_news[doc_name] = tokens
    return doc_to_tokens_med, doc_to_tokens_news


def check_lengths(gold_dict, pred_dict):
    for doc in gold_dict.keys():
        length = len(gold_dict[doc])
        assert(length == len(pred_dict[doc])), "Doc: "+doc+" gold length: "+str(length)+", pred length: "+str(len(pred_dict[doc]))


def evaluate_predictions(gold_dict, dplp_dict, feng_dict, domain_prefix):
    evaluate_edus(gold_dict, dplp_dict, "dplp_"+domain_prefix)
    evaluate_edus(gold_dict, feng_dict, "feng_" + domain_prefix)


def evaluate_edus(gold_dict, guess_dict, domain_prefix):
    correct = 0
    num_pred = 0
    num_gold = 0
    results = []
    for gold_doc, guess_doc in zip(gold_dict.keys(), guess_dict.keys()):
        results.append("\n\n"+guess_doc+"\n")
        gold_indices = [i for i, x in enumerate(gold_dict[gold_doc]) if EDU_MARKER in x]
        guess_indices = [i for i, x in enumerate(guess_dict[guess_doc]) if EDU_MARKER in x]
        for idx, token in enumerate(gold_dict[gold_doc]):
            if idx in gold_indices and idx in guess_indices:
                results.append(token+"GOOD_BREAK")
            elif idx in guess_indices and idx not in gold_indices:
                results.append(token+"BAD_BREAK")
            elif idx in gold_indices and idx not in guess_indices:
                results.append(token+"MISS_BREAK")
            else:
                results.append(token)
        doc_correct = len(set(gold_indices) & set(guess_indices))
        doc_pred = len(guess_indices)
        doc_gold = len(gold_indices)
        correct += doc_correct
        num_pred += doc_pred
        num_gold += doc_gold

        doc_prec = doc_correct / float(doc_pred)
        doc_rec = doc_correct / float(doc_gold)
        doc_f1 = 2 * doc_prec * doc_rec / (doc_prec + doc_rec)
        print("Per doc: ", guess_doc, " F1: " + "{0:.2f}".format(doc_f1 * 100) + \
          ", precision: " + repr(doc_correct) + "/" + repr(doc_pred) + " = " + "{0:.2f}".format(doc_prec * 100) + \
          ", recall: " + repr(doc_correct) + "/" + repr(doc_gold) + " = " + "{0:.2f}".format(doc_rec * 100))

        with open(domain_prefix + '_results.txt', 'w') as results_file:
            results_file.write(" ".join(results))
    if num_pred == 0:
        prec = 0
    else:
        prec = correct / float(num_pred)
    if num_gold == 0:
        rec = 0
    else:
        rec = correct / float(num_gold)
    if prec == 0 and rec == 0:
        f1 = 0
    else:
        f1 = 2 * prec * rec / (prec + rec)
    print(domain_prefix + " F1: " + "{0:.2f}".format(f1 * 100) + \
          ", precision: " + repr(correct) + "/" + repr(num_pred) + " = " + "{0:.2f}".format(prec * 100) + \
          ", recall: " + repr(correct) + "/" + repr(num_gold) + " = " + "{0:.2f}".format(rec * 100))


if __name__ == '__main__':
    gold_stanford_dir = sys.argv[1]
    gold_spacy_dir = sys.argv[2]
    dplp_dir = sys.argv[3]
    feng_dir = sys.argv[4]
    neural_dir = sys.argv[5]

    gold_stanford_dict_med, gold_stanford_dict_news = read_tokens(gold_stanford_dir)
    gold_spacy_dict_med, gold_spacy_dict_news = read_tokens(gold_spacy_dir)
    dplp_dict_med, dplp_dict_news = read_tokens(dplp_dir)
    feng_dict_med, feng_dict_news = read_tokens(feng_dir)
    neural_dict_med, neural_dict_news = read_tokens(neural_dir)

    # sanity check to make sure tokens match up
    check_lengths(gold_stanford_dict_med, dplp_dict_med)
    check_lengths(gold_stanford_dict_med, feng_dict_med)
    check_lengths(gold_stanford_dict_news, dplp_dict_news)
    check_lengths(gold_stanford_dict_news, feng_dict_news)
    check_lengths(gold_spacy_dict_med, neural_dict_med)
    check_lengths(gold_spacy_dict_news, neural_dict_news)

    evaluate_predictions(gold_stanford_dict_med, dplp_dict_med, feng_dict_med, "med")
    evaluate_predictions(gold_stanford_dict_news, dplp_dict_news, feng_dict_news, "news")
    evaluate_edus(gold_spacy_dict_med, neural_dict_med, "neural_med")
    evaluate_edus(gold_spacy_dict_news, neural_dict_news, "neural_news")

    num_edus_med, num_tokens_med = get_counts(gold_stanford_dict_med)
    num_edus_news, num_tokens_news = get_counts(gold_stanford_dict_news)
    print("Counts for medical: tokens / edus", num_tokens_med, num_edus_med)
    print("Counts for news: tokens / edus", num_tokens_news, num_edus_news)
