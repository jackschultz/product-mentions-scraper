import requests

headers = {"User-Agent": "Product Mentions"}
class Gatherer(object):

  def __init__(self):
    pass

  def __str__(self):
    ""

  def gather_threads(self):
    pass

  def gather_comments(self):
    pass

  def get_url_with_retries(self, url, max_tries=3):
    for attempt in range(max_tries):
      response = requests.get(url, headers=headers)
      print "Requestion url ({}) try number {}, status code: {}".format(url, attempt, response.status_code)
      if response.status_code == 200:
        return response
    else:
        time.sleep(2)
    return response #return it anyway and get error
