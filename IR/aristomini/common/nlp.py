"""
nlp utils
"""
from functools import lru_cache
import re
from typing import List, NamedTuple, Iterable
from .thulac import thulac
import json
import os

# os.environ["HANLP_HOME"] = "/scratch/jindi/packages/hanlp"
# han_tokenizer = hanlp.load('CTB6_CONVSEG') # for chinese sentence segmentation
cwd = os.path.split(os.path.realpath(__file__))[0]
STOPWORDS = set(json.load(open(cwd + '/stopwords_zh.json'))["words"])

def get_sentences(filename: str) -> List[str]:
    """get sentences"""
    with open(filename) as f:
        return [line.strip() for line in f]


NGram = NamedTuple("NGram", [("gram", str), ("position", int)])
Token = NamedTuple("Token",
                   [("word", str),
                    ("position", int),
                    ("is_stopword", bool)])

thu_tokenizer = thulac(seg_only=True)
def word_tokenize(sent):
    return thu_tokenizer.cut(sent, text=True).split()


def tokenize(sentence: str) -> List[Token]:
    """
    lowercase a sentence, split it into tokens, label the stopwords, and throw out words that
    don't contain alphabetic/chinese/numeric characters
    """
    pre_tokens = [Token(w, i, w in STOPWORDS)
                  for i, w in enumerate(word_tokenize(sentence))]

    return [token for token in pre_tokens if re.search(u'[\u4e00-\u9fff]+', token.word) or
                                             re.search("[a-zA-Z0-9]+", token.word)]


def ngrams(n: int, tokens: List[Token], skip: bool=False) -> List[NGram]:
    """generate all the ngrams of size n. do not allow ngrams that contain stopwords, except that a
        3-gram may contain a stopword as its middle word"""

    def stopwords_filter(subtokens: List[Token]) -> bool:
        """a filter"""
        if n == 3:
            return not subtokens[0].is_stopword and not subtokens[2].is_stopword
        else:
            return all(not token.is_stopword for token in subtokens)

    def make_gram(subtokens: List[Token]) -> NGram:
        """make a gram using the position of the leftmost work and skipping the middle maybe"""
        words = [token.word if not skip or i == 0 or i == len(subtokens) - 1 else "_"
                 for i, token in enumerate(subtokens)]
        return NGram(" ".join(words), subtokens[0].position)

    # if n is 1, we want len(tokens), etc..
    slices = [tokens[i:(i+n)] for i in range(len(tokens) - n + 1)]

    return [make_gram(slic) for slic in slices if stopwords_filter(slic)]


def distinct_grams(grams: List[NGram]) -> List[str]:
    """return the distinct grams from a bunch of ngrams"""
    return list({gram.gram for gram in grams})


def all_grams_from_tokens(tokens: List[Token]) -> List[NGram]:
    """make all the 1, 2, 3, and skip-3 grams from some tokens"""
    return (ngrams(1, tokens) +
            ngrams(2, tokens) +
            ngrams(3, tokens) +
            ngrams(3, tokens, skip=True))


def all_grams(sentence: str) -> List[NGram]:
    """tokenize the sentence and make all the grams"""
    return all_grams_from_tokens(tokenize(sentence))
