
# coding: utf-8

# In[ ]:

from collections import Counter

import pandas as pd
import numpy as np

import scipy.sparse as sp

import matplotlib.pyplot as plt
import seaborn as sns

from tsne import bh_sne

from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize


# In[ ]:

df_reactions = pd.read_csv('reaction-logs.txt', sep='\t')
df_reactions = df_reactions[df_reactions.channel != 'bots']
df_reactions.ts = pd.to_datetime(df_reactions.ts)

aug16 = pd.to_datetime('2016-08-16')
df_reactions = df_reactions[~((df_reactions.channel == '_general') & (df_reactions.ts >= aug16))]


# In[ ]:

def as_set_normalize(reactions):
    uniq = set(reactions.split())
    result = set()
    for r in uniq:
        if 'skin-tone' in r:
            r, _ = r.split('::')
        result.add(r)
    return result

reactions_grouped = df_reactions.groupby('message_id').agg({'reaction': ' '.join})
reactions_set = reactions_grouped.reaction.apply(as_set_normalize)


# In[ ]:

reaction_cnt = Counter()
reactions_set.apply(reaction_cnt.update)
reaction_cnt = {k: v for (k, v) in reaction_cnt.items() if v >= 5}
freq = set(reaction_cnt.keys())
len(freq)


# In[ ]:

def remove_infreq(reactions):
    return {r for r in reactions if r in freq}


# In[ ]:

reactions_set = reactions_set.apply(remove_infreq)


# In[ ]:

no_reactions = reactions_set.apply(len)
reactions_set = reactions_set[(no_reactions > 1) & (no_reactions < 20)]


# In[ ]:

vocab = sorted(freq)
vocab_idx = {v: i for (i, v) in enumerate(vocab)}


# In[ ]:

N = len(vocab)
cooc = sp.dok_matrix((N, N))


# In[ ]:

for rset in reactions_set:
    for r in rset:
        others = rset.copy()
        others.remove(r)
        
        for o in others:
            cooc[vocab_idx[r], vocab_idx[o]] += 1


# In[ ]:

smoothing = 2.5


# In[ ]:

reaction_total_cnt = sum(reaction_cnt.values())
reaction_total_cnt_log = np.log(reaction_total_cnt + N * smoothing)


# In[ ]:

cnt_log = {vocab_idx[k]: np.log(v + smoothing) for (k, v) in reaction_cnt.items()}


# In[ ]:

ppmis = cooc.copy()

for (i, j), val in ppmis.items():
    log_cooc = np.log(ppmis[i, j] + smoothing)
    pmi = log_cooc + reaction_total_cnt_log - cnt_log[i] - cnt_log[j]
    if pmi > 0:
        ppmis[i, j] = pmi
    else:
        ppmis[i, j] = 0.0


# In[ ]:

ppmis = ppmis.tocsc()


# In[ ]:

dim = 40
svd = TruncatedSVD(n_components=dim, random_state=1)


# In[ ]:

reactions_embeddings = svd.fit_transform(ppmis)


# In[ ]:

def most_similar_reactions(rname):
    print 'most similar to %s' % rname
    vec = reactions_embeddings[vocab_idx[rname]]
    sim = reactions_embeddings.dot(vec)

    for i in (-sim).argsort()[1:11]:
        print '- %s (%.3f)' % (vocab[i], sim[i])


# In[ ]:

most_similar_reactions('facepalm')


# In[ ]:

most_similar_reactions('kaggle')


# In[ ]:

most_similar_reactions('r')


# In[ ]:

emb_2d = bh_sne(normalize(reactions_embeddings))


# In[ ]:

plt.figure(figsize=(50, 50))

plt.scatter(emb_2d[:, 0], emb_2d[:, 1], marker='.', alpha=0.1)

ax = plt.gca()

for i, txt in enumerate(vocab):
    ax.annotate(txt, (emb_2d[i, 0], emb_2d[i, 1]), fontsize=20)

plt.margins(0)
plt.tight_layout()
plt.savefig('emoji-embed.png')


# In[ ]:



