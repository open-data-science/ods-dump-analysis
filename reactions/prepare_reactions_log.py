import json
from zipfile import ZipFile
from tqdm import tqdm
import pandas as pd

from collections import defaultdict

ods_dump_file = '../data/opendatascience Slack export Nov 27 2016.zip'

with ZipFile(ods_dump_file, 'r') as zfile:

    with zfile.open('users.json') as users_file:
        users_text = users_file.read()
        if type(users_text) is not str:
            users_text = users_text.decode('utf8')
        users = json.loads(users_text)
        user_ids = {u['id']: u['name'] for u in users}

    msg_id = 0
    reaction_logs = []
    message_texts = {}

    for name in tqdm(zfile.namelist()):
        if name.count('/') != 1 or not name.endswith('.json'):
            continue

        channel, date = name.split('/')

        with zfile.open(name) as msgs_file:
            msgs_text = msgs_file.read()
            if type(msgs_text) is not str:
                msgs_text = msgs_text.decode('utf8')
            messages = json.loads(msgs_text)

            for m in messages:
                if 'user' not in m:
                    continue

                user_id = m['user']
                if user_id not in user_ids:
                    continue
                user = user_ids[user_id]

                ts = float(m['ts'])
                if 'reactions' not in m:
                    continue
                
                msg_id = msg_id + 1
                message_texts[msg_id] = m.get('text', "NO_TEXT")
                
                for r in m['reactions']:
                    rname = r['name']

                    reaction_order = 0
                    
                    for u in r['users']:
                        if u not in user_ids:
                            continue
                        u = user_ids[u]
                        
                        reaction_order += 1
                        reaction_logs.append((msg_id, channel, user, rname, u, reaction_order, ts))



cnt = 0

def cnt_factory():
    global cnt
    cnt = cnt + 1
    return cnt

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

