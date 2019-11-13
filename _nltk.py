import nltk
import sys 


# provide .txt in argument
fn = sys.argv[1]
# opening file and caching data
f = open(fn)
txt = f.read()
f.close()

# remove punctuation
cleansed = txt.lower()

# split text
tokens = nltk.word_tokenize(cleansed)
# singular to plurial
lemma = nltk.stem.WordNetLemmatizer()
lem = [lemma.lemmatize(word) for word in tokens]
# words to word's stem i.e.; programer => program
stemma = nltk.stem.PorterStemmer()
stem = [stemma.stem(token) for token in lem]
# tagging words with their grammactical use
tagged = nltk.pos_tag(stem, tagset='universal')

# tag frequency distribution
tag_fd = dict(nltk.FreqDist(tag for (word, tag) in tagged))
# as sorted list of tuples
tag_fd = sorted(tag_fd.items(), key=lambda x: x[1], reverse=True)

# TODO : concanate function words together

# most used nouns and verbs
word_fd = dict(nltk.FreqDist(word if tag == "NOUN" else None for (word, tag) in tagged))
# as sorted list of tuples
word_fd = sorted(word_fd.items(), key=lambda x: x[1], reverse=True)
print(word_fd)
# print words over threshold occurences
# claculating threshold
threshold  = 0
for item in word_fd:
    # filter out invalid items from calculation
    if item[1]>threshold and item[0] not in [None, "NUM", ".", "X"]:
        threshold=item[1]

max_item = 5
res = list()
while len(res) < max_item:
    for tup in word_fd:
        if len(res) == max_item:
            break
        word, c = tup
        if c >= threshold and word not in [None, "hidayah", "octopu", "bob", "is", "are", "look", "get", "be"] and word not in res:
            res.append(word)
    threshold -= 1
print(res)

# calculate %
total = int()
for key, value in tag_fd:
    total += int(value)

temp = 0.0
for key, value in tag_fd:
    if key in ["NOUN", "VERB", "ADJ"]:
        print(key, (value / total) * 100)
    elif key in ["NUM", ".", "X"]:
       continue
    else:
        temp += value
temp = (temp/total) * 100
print("Other :", temp)
