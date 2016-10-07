
# coding: utf-8

# In[75]:

import sys
import re
import random
from operator import itemgetter
import urllib

def extract_features(INPUT_FILE_1, INPUT_FILE_2, OUTPUT_FILE):
    digits = re.compile('[\d]+$')
    feature_4c = re.compile('[^\d]+\d+[^\d]+$')
    count = 0
    count1 = 0
    features = {}
    for file in (INPUT_FILE_1, INPUT_FILE_2):
        f = open(file, 'r')
        lines = f.read().splitlines()
        for line in random.sample(lines, 1000):
            #print line
            try:
                line = urllib.unquote(line).decode('utf-8')
            except UnicodeDecodeError:
                try:
                    line = urllib.unquote(line).decode('cp1251')
                except UnicodeDecodeError:
                    pass
            #print line
            line = line[line.find('.'):]
            num1 = line.count('/') - int(line[len(line) - 1] == '/')
            features['segments:' + str(num1)] = features.setdefault('segments:' + str(num1), 0) + 1
            line = line[line.find('/') + 1:]
            query = ''
            if line.find('?') != -1:
                query = line[line.find('?') + 1:]
                line = line[:line.find('?')]
            # 3, 4
            if query != '':
                query = query[1:]
                while query.find('&') != -1:
                    param = query[:query.find('&')]
                    if param.find('=') != -1:
                        s = 'param_name:' + param[:param.find('=')]
                        features[s] = features.setdefault(s, 0) + 1
                        s = 'param:' + param
                        features[s] = features.setdefault(s, 0) + 1
                    else:
                        s = 'param_name:' + param
                        features[s] = features.setdefault(s, 0) + 1
                    query = query[query.find('&') + 1:]
                query = query[:-1]
                if query.find('=') != -1:
                    s = 'param_name:' + query[:query.find('=')]
                    features[s] = features.setdefault(s, 0) + 1
                    s = 'param:' + query
                    features[s] = features.setdefault(s, 0) + 1
                else:
                    s = 'param_name:' + query
                    features[s] = features.setdefault(s, 0) + 1
            idx = 0
            while line.find('/') != -1:
                segment = line[:line.find('/')]

                #if idx == 1:
                #    print 'idx=1: ' + segment

                # 4a
                s = 'segment_name_' + str(idx) + ':' + segment
                features[s] = features.setdefault(s, 0) + 1

                # 4b
                res = digits.match(segment)
                #if idx == 2:
                    #count += 1
                if res:
                    s = 'segment_[0-9]_' + str(idx) + ':1'
                    #if idx == 2:
                        #count1 += 1
                    #print segment
                    features[s] = features.setdefault(s, 0) + 1
                #else:
                    #print 'no: ' + segment

                # 4c
                res = feature_4c.search(segment)
                if res:
                    s = 'segment_substr[0-9]_' + str(idx) + ':1'
                    features[s] = features.setdefault(s, 0) + 1

                # 4f
                s = 'segment_len_' + str(idx) + ':' + str(len(segment))
                features[s] = features.setdefault(s, 0) + 1

                line = line[line.find('/') + 1:]
                idx += 1
            #print line
            if line != '\n':
                #print line
                # 4a
                # s = 'segment_name_' + str(idx) + ':' + segment
                # features[s] = features.setdefault(s, 0) + 1

                # 4b
                res = digits.match(segment)
                if res:
                    s = 'segment_[0-9]_' + str(idx) + ':1'
                    features[s] = features.setdefault(s, 0) + 1

                # 4c
                res = feature_4c.match(line)
                if res:
                    #print line
                    s = 'segment_substr[0-9]_' + str(idx) + ':1'
                    features[s] = features.setdefault(s, 0) + 1

                # # 4f
                # s = 'segment_len_' + str(idx) + ':' + str(len(segment))
                # features[s] = features.setdefault(s, 0) + 1

                if line.find('.') != -1:
                    # 4d
                    extension = line[line.rfind('.') + 1:]
                    s = 'segment_ext_' + str(idx) + ':' + extension
                    features[s] = features.setdefault(s, 0) + 1

                    # 4e
                    res = feature_4c.match(line[:line.rfind('.')])
                    if res:
                        s = 'segment_ext_substr[0-9]_' + str(idx) + ':' + extension
                        features[s] = features.setdefault(s, 0) + 1
                idx += 1
            #1
            #idx -= 1
            #features['segments:' + str(idx)] = features.setdefault('segments:' + str(idx), 0) + 1

        f.close()
    #print count
    #print count1
    # Отберём фичи
    dict_delete = []
    for feature in features:
        if features[feature] < 100:
            dict_delete.append(feature)
    for feature in dict_delete:
        features.pop(feature)

    res = sorted(features.items(), key = itemgetter(1), reverse=True)
    f = open(OUTPUT_FILE, 'w')
    for idx in range(len(res)):
        f.write(res[idx][0] + '\t' + str(res[idx][1]) + '\n')
    f.close()

extract_features('data/urls.wikipedia.examined', 'data/urls.wikipedia.general', 'result/wikipedia.res')