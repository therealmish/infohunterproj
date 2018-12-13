import webapp2, urllib, urllib2, json
import jinja2
import os
from datetime import datetime, timedelta
import logging

# import ssl
# ssl._create_default_https_context = ssl._create_unverified_context

apiKey = "1d163dccb04f4dd49faf23679508a6d9"
baseurl = "https://newsapi.org/v2/"


# This function handles all errors produced when making the API request.
def errorFreeData(url):
    try:
        return urllib.urlopen(url)
    except urllib2.HTTPError as e:
        logging("Server couldn't fulfill the request")
        logging("Error code: ", e.code)
    except urllib2.URLError as e:
        logging("Failed to reach the server")
        logging("Reason: ", e.reason)
    return None


# This function is used to assign query parameters that will later be
# used when making the API request.
def getByKey(method="everything", q="nothing", source="nothing"):
    params = {}
    if q is not "nothing":
        params["q"] = q
    if source is not "nothing":
        params["sources"] = source
    params["apiKey"] = apiKey
    url = baseurl + method + "?" + urllib.urlencode(params)
    return json.load(errorFreeData(url))


# Class to store information about each headline that will later be displayed.
# Contains title, author, description, news source, date published, and image URL
# of each result.
class Headline():
    def __init__(self, dict):
        self.title = dict['title'].encode('ascii', 'ignore')
        self.author = dict['author']
        self.description = dict['description'].encode('ascii', 'ignore')
        self.source = dict["source"]["name"]
        self.date = datetime.strptime(dict["publishedAt"], '%Y-%m-%dT%H:%M:%S%fZ')
        self.photo_url = dict['urlToImage']


# Created an environment for the front end to be rendered.
JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


# Handles the landing(home) page of the application.
class MainHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        template = JINJA_ENVIRONMENT.get_template('newsform.html')
        self.response.write(template.render(template_values))


# Filters the data and sends it to the HTML file.
# Handles the results page of the application.
class HeadlineHandler(webapp2.RequestHandler):
    def post(self):
        vals = {}
        vals['page_title'] = "This is What WE Have For YOU based on your search"
        keyword = self.request.get("keyword")
        source = self.request.get("source")
        data = getByKey(q=keyword, source=source)["articles"]
        objects = [Headline(article) for article in data]
        time = int(self.request.get("date"))
        filtered = [object for object in objects if object.date > (datetime.now() - timedelta(days=time))]
        sorter = self.request.get("sort")
        if sorter == "newdate":
            sortedData = sorted(filtered, key=lambda x: x.date, reverse=True)
        elif sorter == "olddate":
            sortedData = sorted(filtered, key=lambda x: x.date, reverse=False)
        elif sorter == "author":
            sortedData = sorted(filtered, key=lambda x: x.author, reverse=False)
        for obj in sortedData:
            obj.date = obj.date.strftime("%A %d. %B %Y")
        vals["results"] = sortedData
        template = JINJA_ENVIRONMENT.get_template('results.html')
        self.response.write(template.render(vals))


# Created a web application application
app = webapp2.WSGIApplication([
    ('/results', HeadlineHandler),
    ('/.*', MainHandler)
], debug=True)


