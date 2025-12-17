import nltk

def setup_nltk():
    resources = [
        "punkt",
        "punkt_tab",
        "stopwords",
        "wordnet",
        "omw-1.4"
    ]

    for r in resources:
        try:
            nltk.data.find(r)
        except LookupError:
            nltk.download(r)
