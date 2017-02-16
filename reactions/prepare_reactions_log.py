from collections import defaultdict

import pandas as pd

from utils import message_generator

ods_dump_file = '../data/opendatascience Slack export Feb 16 2017.zip'

cnt = 0


def cnt_factory():
    global cnt
    cnt += 1
    return cnt


if __name__ == '__main__':
    reaction_logs = []
    message_texts = {}
    for msg_id, channel, user, text, ts, reactions in message_generator(ods_dump_file):
        if len(reactions) == 0:
            continue
        message_texts[msg_id] = text
        for rname, users in reactions.items():
            for i, u in enumerate(users):
                reaction_logs.append((msg_id, channel, user, rname, u, i, ts))

    cnts_dict = defaultdict(cnt_factory)

    df_reaction_logs = pd.DataFrame(reaction_logs)
    df_reaction_logs.columns = ['message_id', 'channel', 'message_user', 'reaction',
                                'reaction_user', 'reaction_order', 'ts']
    df_reaction_logs.ts = pd.to_datetime(df_reaction_logs.ts.round(), unit='s')
    df_reaction_logs.sort_values(by=['ts', 'reaction', 'reaction_order'], inplace=1)
    df_reaction_logs.reset_index(drop=1, inplace=1)
    df_reaction_logs.message_id = df_reaction_logs.message_id.apply(lambda x: cnts_dict[x])

    df_reaction_logs.to_csv('reaction-logs.txt', sep='\t', index=False)

    message_texts = {cnts_dict[k]: v for (k, v) in message_texts.items()}

    items = message_texts.items()
    if type(items) is not list:
        items = list(items)
    df_messages = pd.DataFrame(items, columns=['message_id', 'text'])
    df_messages.to_csv('reaction-messages.txt', encoding='utf-8', sep='\t', index=False)
