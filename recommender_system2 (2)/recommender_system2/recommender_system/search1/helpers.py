from __future__ import unicode_literals
from .models import Urls,Keywords_Search
from django.conf import settings
import requests
from django.views.decorators.csrf import csrf_exempt
from bs4 import BeautifulSoup
import traceback
from nltk.corpus import stopwords

stop_words = set(stopwords.words('english'))

def read_file(link):
    documents = []
    try:
      page = requests.get(link)
      if page.status_code == 200:
        page = BeautifulSoup(page.text, "lxml")
        [x.extract() for x in page.findAll(['script', 'style'])]
        try:
           ti = page.title.string
        except:
           ti = link
        durls = Urls(url=link, title=ti, search=False)
        durls.save()
        documents.append(str(page))
        documents[0] = documents[0].lower()
        texts = [[word for word in document.lower().split() if word not in stop_words] for document in documents]
        return texts
      else:
        st = [""]
        texts = [[word for word in doc] for doc in st]
        return texts
    except:
        st = [""]
        texts = [[word for word in doc] for doc in st]
        return texts


@csrf_exempt
def crawl(visited_link, links, keywords, depth):
    if depth == 3:
        return
    new_links=[]
    dict1={}
    for link in links:
        if link not in visited_link:
            visited_link.append(link)

            dict3 = link.split(".")
            if "pdf" in dict3:
                continue
            try:
                page = requests.get(link)
                if page.status_code == 200:
                    page = BeautifulSoup(page.text, "lxml")
                    if depth == 3:
                        continue
                    if depth == 1:
                        for key in page.find_all("a", {'target': '_blank', 'rel': 'noopener'}):
                            link = key.get('href')
                            if link not in new_links and links:
                                try:
                                    durls = Urls.objects.get(url=link)
                                except Exception as error:
                                    durls = Urls(url=link, title=ti, search=False)
                                    durls.save()
                                new_links += [link]
                    else:
                        for key in page.find_all("a"):
                            link = key.get('href')
                            if link not in new_links and links:
                                try:
                                    durls = Urls.objects.get(url=link)
                                except Exception as error:
                                    durls = Urls(url=link, title="", search=False)
                                    durls.save()
                                new_links += [link]
            except Exception as error:
                Urls.objects.filter(url=link).delete()
                pass
    crawl(visited_link,new_links,keywords,depth+1)

@csrf_exempt
def find_results(query):
    print("h1")
    query1 = query.replace(" ", '+')
    req = requests.get('http://api.springernature.com/metadata/json?q=keyword:' + query1 + "&api_key=" + settings.SPRINGER_KEY)
    req = req.json()
    length = len(req['records'])

    result = []
    for i in range(0, length - 1):
        url = req['records'][i]['url'][0]['value']
        result += [url]
        try:
            durls = Urls.objects.get(url=url)
        except Exception as error:
            durls = Urls(url=url,title="",search=False)
            durls.save()

    # extract all pages_object and keywords

    keywords = []
    links = [] + result
    visited_links = []

    for i in range(0, length - 1):
        try:
            page = requests.get(result[i])
            if page.status_code == 200:
                soup = BeautifulSoup(page.text, 'html.parser')
                for key in soup.find_all("span", {'class': 'Keyword'}):
                    start = 0
                    end = len(key.get_text()) - 1
                    keyword = key.get_text()[start:end].lower()
                    if keyword not in keywords:
                        keywords += [keyword]
        except:
            Urls.objects.filter(url = result[i]).delete()
    for keyword in keywords:
        try:
            key = Keywords_Search.objects.get(keyword=keyword)
        except Exception as error:
            key = Keywords_Search(keyword=keyword,search=False)
            key.save()
    crawl(visited_links, links, keywords, 1)
