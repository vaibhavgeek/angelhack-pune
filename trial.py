import json
data_try = {u'language': u'en', u'entities': [{u'type': u'PERSON', u'metadata': {}, u'mentions': [{u'type': u'COMMON', u'text': {u'beginOffset': 42, u'content': u'person'}}], u'name': u'person', u'salience': 0.6916537}, {u'type': u'OTHER', u'metadata': {}, u'mentions': [{u'type': u'COMMON', u'text': {u'beginOffset': 0, u'content': u'Complaint'}}], u'name': u'Complaint', u'salience': 0.18964562}, {u'type': u'OTHER', u'metadata': {}, u'mentions': [{u'type': u'COMMON', u'text': {u'beginOffset': 22, u'content': u'problem'}}], u'name': u'problem', u'salience': 0.07849536}, {u'type': u'OTHER', u'metadata': {}, u'mentions': [{u'type': u'COMMON', u'text': {u'beginOffset': 141, u'content': u'violence'}}], u'name': u'violence', u'salience': 0.019375721}, {u'type': u'OTHER', u'metadata': {}, u'mentions': [{u'type': u'COMMON', u'text': {u'beginOffset': 163, u'content': u'end'}}], u'name': u'end', u'salience': 0.012739177}, {u'type': u'OTHER', u'metadata': {}, u'mentions': [{u'type': u'COMMON', u'text': {u'beginOffset': 122, u'content': u'basis'}}], u'name': u'basis', u'salience': 0.008090399}]}
many = ""
for utility in data_try["entities"]:
    if utility["type"] == "OTHER":
        useful = utility["name"] + " : " + str(utility["salience"]) + " , "
        many = many + useful
print many[:-2] 
