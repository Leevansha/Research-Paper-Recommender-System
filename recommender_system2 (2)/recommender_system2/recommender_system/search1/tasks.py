from __future__ import absolute_import, unicode_literals
from nltk.corpus import stopwords
from .helpers import find_results,read_file
from celery import Celery
from .models import Keywords_Search, Urls,Keywords_Count
from gensim import corpora,models
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')


app = Celery('tasks', broker='redis://127.0.0.1:6379')

stop_words = set(stopwords.words('english'))
app.config_from_object(__name__)




@app.task
def find_results1():
    list = []
    while True:
        while len(list) == 0:
            query_set = Keywords_Search.objects.all()
            for query in query_set:
                list.append(query.keyword)
            list1 = []

        while len(list):
            for word in list:
                 k = Keywords_Search.objects.get(keyword = word)
                 if k.search == False:
                      find_results(word)
                      k.search = True
                      k.save()

            query_set = Keywords_Search.objects.all()
            list2 = []
            for query in query_set:
                list2.append(query.keyword)
            list1.append(list)
            list =list2[len(list1):len(list2)]


@app.task
def calculate_sim_score():
    while True:
        urls = Urls.objects.filter(search=False)
        for u in urls:
            if u.search == False:
                url = u.url
                texts = read_file(url)
                if(len(texts[0])==0):
                    continue
                dictionary = corpora.Dictionary(texts)
                keywords = Keywords_Search.objects.all()
                corpus = [dictionary.doc2bow(text) for text in texts]
                lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=2)
                for k in keywords:
                    doc = k.keyword
                    c = doc.lower().split()
                    vec_bow = dictionary.doc2bow(c)
                    vec_lsi = lsi[vec_bow]
                    if len(vec_lsi) > 0:
                        sim_score = vec_lsi[0][1]
                        if sim_score >= 0.02:
                            try:
                                da = Keywords_Count.objects.get(keyword=k, url=u)
                            except:
                                da = Keywords_Count(keyword=k, url=u, sim_score=sim_score)
                                da.save()
                u.search = True
                u.save()

find_results1.apply_async(queue="q1")
calculate_sim_score.apply_async(queue="q2")
