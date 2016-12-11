import pandas as pd
from sklearn.preprocessing import minmax_scale
import json
import os
import matplotlib.pyplot as plt
plt.style.use('ggplot')

BASE_DIR = '/home/arseny/Downloads/ods/'
PICS_DIR = '/home/arseny/Downloads/ods_pics/'
TOP_N = 10
ITERS = 5
MAX_WEIGHT = 3

good_reactions = '100', 'heavy_plus_sign', '+1', 'muscle'
bad_reactions = 'heavy_minus_sign', 'facepalm', 'ban'


def get_weighted_top(channel, reaction_set):
    users_list = '{}users.json'.format(BASE_DIR)
    with open(users_list) as users:
        users = json.load(users)
        users = {user.get('id'): user.get('name') for user in users}

    weights = {}

    for _ in range(ITERS):
        reactions = []
        for f in os.listdir(channel):
            with open(channel + f) as day:
                day = json.load(day)
                for msg in day:
                    reacted = msg.get('reactions')
                    username = users.get(msg.get('user'))
                    row = {r: 0 for r in reaction_set}
                    row['user'] = username

                    if reacted is not None:
                        for r in reacted:
                            if r.get('name') in reaction_set:
                                row[r.get('name')] = r.get('count') * weights.get(username, 1)
                    reactions.append(row)

        if len(reactions) > 100:
            df = pd.DataFrame(reactions)
            df['total'] = df.sum(axis=1)
            df = df.groupby(['user']).agg(sum)
            df = df[df.total > 0]

            if df.shape[0] < TOP_N:
                return

            weights = pd.Series(minmax_scale(df.total, feature_range=(1, MAX_WEIGHT)), index=df.total.index)
            weights = weights.to_dict()
        else:
            return

    df.total = minmax_scale(df.total, (.01, 1))
    return df.sort_values('total', ascending=False).head(TOP_N).total


def main():
    channels = ['{}{}/'.format(BASE_DIR, p) for p in os.listdir(BASE_DIR)]
    channels = filter(os.path.isdir, channels)

    for chan in channels:
        result = get_weighted_top(chan, good_reactions)
        if result is not None:
            chan_name = chan.split('/')[-2]
            print('\nchannel {}'.format(chan_name))
            if PICS_DIR:
                result.plot('barh', title='#{}'.format(chan_name))\
                    .get_figure().savefig('{}{}.png'.format(PICS_DIR, chan_name))
            print(result)


if __name__ == '__main__':
    main()
