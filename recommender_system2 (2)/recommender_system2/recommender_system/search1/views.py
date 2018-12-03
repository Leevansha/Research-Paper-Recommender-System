from __future__ import unicode_literals
from .models import Urls, Keywords_Count, Keywords_Search
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt



stop_words = set(stopwords.words('english'))


@csrf_exempt
# Create your views here.
def show_form(request):
    template = loader.get_template('get_query.html')
    return HttpResponse(template.render())




urls = Urls.objects.all()


def get_data(request):
    if request.method == 'POST':
        query = request.POST.get('q')
        query = query.lower()
        # REMOVE EXTRA SPACES
        query = query.strip()
        query = re.sub(' +', ' ', query)
        list = []
        list1 =[]
        ad = 0
        if(len(query) == 0):
            return render(request, 'get_query.html', )
        else:
            word_tokens = word_tokenize(query)
            filtered_query = []
            for w in word_tokens:
                if w not in stop_words:
                    filtered_query.append(w)
            query = ''
            for w in filtered_query:
                query = query + " " + w
            query = query.strip()
        #I am updating my column values for valid url
        try:
            key=Keywords_Search.objects.get(keyword=query)
            if key.search:
                print(query)

                if Keywords_Count.objects.all().filter(keyword=query).count()>=10:
                    list3=Keywords_Count.objects.all().filter(keyword=query).order_by('sim_score')
                    for key in list3:
                        list += [key.url.url]
                        list1 += [key.url.title]
                else:
                    ad = 1
            else:
                ad = 1
        except Exception as error:
            p = Keywords_Search(keyword=query,search=False)
            p.save()
            ad=1
        if ad == 1:
            print("hgjh")
            query=query.replace(' ','+')
            req = requests.get("http://api.springernature.com/metadata/json?q=keyword:" + query + "&p=100&api_key=a22eb2a96a01b2bbd164fc11ca2f07a3")
            req = req.json()
            length = len(req['records'])
            # extract all urls
            for i in range(0, length - 1):
                list += [req['records'][i]['url'][0]['value']]
                list1 += [req['records'][i]['title']]
        list = zip(list, list1)
         #Filter and save them in a list and show
        template = loader.get_template('show_result.html')
        return HttpResponse(template.render({'data':list}, request))
    else:
        template = loader.get_template('get_query.html')
        return HttpResponse(template.render())
