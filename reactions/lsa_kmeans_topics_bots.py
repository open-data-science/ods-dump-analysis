from __future__ import print_function
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

# preparing the data

df_reactions = pd.read_csv('reaction-logs.txt', sep='\t')
df_reactions = df_reactions[df_reactions.channel == 'bots']
df_reactions.ts = pd.to_datetime(df_reactions.ts)

aug16 = pd.to_datetime('2016-08-16')
df_reactions = df_reactions[~((df_reactions.channel == '_general') & (df_reactions.ts >= aug16))]


def as_set(reactions):
    return ' '.join(set(reactions.split()))


reactions_grouped = df_reactions.groupby('message_id').agg({'reaction': ' '.join})
distinct_reactions = reactions_grouped.reaction.apply(as_set)
no_reactions = distinct_reactions.str.count(' ') + 1

distinct_reactions = distinct_reactions[(no_reactions > 1) & (no_reactions < 20)]

# vectorizing the "docs"

cv = TfidfVectorizer(min_df=5, norm='l2', token_pattern='\\S+')
X = cv.fit_transform(distinct_reactions)

# clustering

N = 20
K = 20

svd = TruncatedSVD(n_components=N, random_state=1)
X_svd = svd.fit_transform(X)
X_svd = normalize(X_svd)

km = KMeans(n_clusters=K, random_state=1)
km.fit(X_svd)

centroids = svd.inverse_transform(km.cluster_centers_)
order = centroids.argsort()[:, ::-1]

# showing the topics

terms = cv.get_feature_names()

for i in range(K):
    if (centroids[i] > 0.1).sum() < 2:
        continue

    print("Cluster %d:" % i)

    for ind in order[i]:
        weight = centroids[i, ind]
        if weight < 0.1:
            break
        print('%s (%0.3f), ' % (terms[ind], weight), end='')

    print()
    print()
