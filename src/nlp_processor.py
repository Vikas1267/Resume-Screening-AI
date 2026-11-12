"""NLP preprocessing utilities: tokenization, stopword removal, and lemmatization."""

from __future__ import annotations

import re
from functools import lru_cache
from typing import List

import nltk
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_NLTK_PACKAGES = (
    ("tokenizers/punkt", "punkt"),
    ("tokenizers/punkt_tab", "punkt_tab"),
    ("corpora/stopwords", "stopwords"),
    ("corpora/wordnet", "wordnet"),
    ("corpora/omw-1.4", "omw-1.4"),
    ("taggers/averaged_perceptron_tagger_eng", "averaged_perceptron_tagger_eng"),
)


def ensure_nltk_data() -> None:
    """Download required NLTK corpora/models if not already present locally."""
    for resource_path, package_name in _NLTK_PACKAGES:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(package_name, quiet=True)


@lru_cache(maxsize=1)
def _get_stopwords() -> set[str]:
    ensure_nltk_data()
    return set(stopwords.words("english"))


@lru_cache(maxsize=1)
def _get_lemmatizer() -> WordNetLemmatizer:
    ensure_nltk_data()
    return WordNetLemmatizer()


def _to_wordnet_pos(treebank_tag: str) -> str:
    if treebank_tag.startswith("J"):
        return wordnet.ADJ
    if treebank_tag.startswith("V"):
        return wordnet.VERB
    if treebank_tag.startswith("R"):
        return wordnet.ADV
    return wordnet.NOUN


def clean_raw_text(text: str) -> str:
    """Normalize whitespace and remove non-informative control characters."""
    text = text.replace("\x00", " ").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def preprocess_text(text: str) -> str:
    """
    Apply NLP preprocessing pipeline to text:
    1. Lowercase & normalize technical symbols
    2. Tokenization (NLTK word_tokenize)
    3. Stopword & punctuation filtering
    4. POS-tagged Lemmatization (WordNetLemmatizer)

    Returns a space-joined string of normalized lemmas ready for TF-IDF vectorization.
    """
    if not text or not text.strip():
        return ""

    ensure_nltk_data()
    stop_words = _get_stopwords()
    lemmatizer = _get_lemmatizer()

    normalized = text.lower()
    # Preserve common tech tokens like c++, c#, .net, node.js
    normalized = normalized.replace("c++", " cpp ").replace("c#", " csharp ").replace(".net", " dotnet ")

    tokens = word_tokenize(normalized)
    alpha_tokens = [tok for tok in tokens if re.match(r"^[a-z0-9][a-z0-9\.\-\_]*$", tok) and len(tok) > 1]

    try:
        tagged = nltk.pos_tag(alpha_tokens)
    except LookupError:
        tagged = [(tok, "NN") for tok in alpha_tokens]

    lemmas: List[str] = []
    for token, pos_tag in tagged:
        if token in stop_words:
            continue
        lemma = lemmatizer.lemmatize(token, _to_wordnet_pos(pos_tag))
        if lemma not in stop_words and len(lemma) > 1:
            lemmas.append(lemma)

    return " ".join(lemmas)

