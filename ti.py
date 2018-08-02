import sqlite3
import re
import nltk
nltk.download("stopwords")
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

c = sqlite3.connect('pipermail.db')
cur = c.cursor()
sen_email_domain = []
domain_names = set()
subj_reg = set()
stop_words = set(stopwords.words('english'))
regularized_subj = {}
clusters = {}
temp_cluster = []
final_clusters = {}
#cur.execute("alter table csmail drop column id")
#cur.execute("update csmail set id=_rowid_")
#c.commit()
def get_domain_names():
    cur.execute("select distinct(sender_email) from csmail")

    sen_email = cur.fetchall()

    for i in sen_email:
        # print(i[0])
        sen_email_str = i[0]
        wrd_search = re.search(r'\b(at)\b', sen_email_str)
        dom_index = wrd_search.start()
        # print(dom_index)
        domain = sen_email_str[dom_index + 3:]
        domain_names.add(domain.strip())
        sen_email_domain.append((sen_email_str, domain.strip()))


    # print(sen_email_domain)
    # print(len(sen_email_domain))
    for i in sen_email_domain:
        cur.execute("update csmail set domain='" + str(i[1]) + "'where sender_email='" + str(i[0]) + "'")
    c.commit()


def regularize_subjects():
    cur.execute("select distinct(subject),domain from csmail")

    subj = cur.fetchall()

    for i in subj:
        subj_reg.add((re.sub(r'[0-9[\]]', '', i[0]),i[1]))

    for i in subj_reg:
        regularized_subj.setdefault(i[1],[])
        clusters.setdefault(i[1],[])
        final_clusters.setdefault(i[1], [])

    for i in subj_reg:
        word_tokens = word_tokenize(i[0])
        filtered_sentence = [w for w in word_tokens if not w in stop_words]
        filtered_sentence = []
        for w in word_tokens:
            if w not in stop_words:
                filtered_sentence.append(w)
        regularized_subj[i[1]].append(filtered_sentence)

def clustering():
    temp_subj = set()
    c = 1
    for i in domain_names:
        #print(c)
        cur.execute("select id,subject from csmail where domain ='"+i+"'")
        new_subj = cur.fetchall()
        dom_subj_count = len(new_subj)
        temp = []
        #print(dom_subj_count)
        for k in regularized_subj[i]:
            match_count = 0
            for j in new_subj:
                word_tokens = word_tokenize(j[1])
                filtered_sentence = [w for w in word_tokens if not w in stop_words]
                filtered_sentence = []
                for w in word_tokens:
                    if w not in stop_words:
                        filtered_sentence.append(w)
                temp_subj = set(filtered_sentence)
                temp_subj = set(filter(None, temp_subj))
                five_percent = (15 * dom_subj_count) / 100
                #print(set(k).difference(temp_subj),i)
                if len(set(k).difference(temp_subj))<2:
                    match_count +=1
                    temp.append(j[0])
            clusters[i].append(temp)
            temp = []
        c+=1

get_domain_names()
regularize_subjects()
clustering()
#print(domain_names)
#print(len(domain_names))
#print(regularized_subj)\
temp_list =[]

#for i in domain_names:
#    temp=0
#    flag =0
#    for j in clusters[i]:
#        if j[1] > temp:
#            temp = j[1]
#            temp_list.append(j[0])
#        else:
#            temp =0
#            final_clusters[i].append(temp_list)
#            flag =1
#            temp_list = []
#    if flag == 0:
#        final_clusters[i].append(temp_list)
#        temp_list = []


print(clusters['wufoo.com'])