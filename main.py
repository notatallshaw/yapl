'''
Created on 2 Aug 2015

@author: Damian Shaw
'''

from requests import Request, Session
import time

__all__ = ["yapl", "batchRequest"]


class yapl(object):
    """YAPL - YouTube API Python Library"""
    def __init__(self, dev_key=None):
        """Initialise some class level variables"""
        self.dev_key = dev_key
        self.api_url = 'https://www.googleapis.com/youtube/v3'
        self.max_page_results = 50
        self.retry_on_known_error = True
        self.retry_count_on_error = 10
        self.sleep_on_error = 1
        self.increase_sleep_on_error = 6
        self.known_errors = [502, 503]

    def request(self, httptype, method, **params):
        """Returns a class object with useful methods execute() and
        inspect()"""
        return(_yaplRequest(
            self.dev_key, self.api_url, self.retry_on_known_error,
            self.retry_count_on_error, self.sleep_on_error,
            self.increase_sleep_on_error, self.known_errors,
            httptype=httptype, method=method, **params)
            )

    def requestIter(self, httptype, method, **params):
        """Returns a list of request objects, each one is a page of search
        results, limit to the number of pages, YouTube usually returns only a
        maximum of 10 pages"""
        request_class = self.request(httptype, method, **params)
        return(_yaplRequestIter(request_class=request_class))


class _yaplRequest(object):
    """Class for defining requests, allows you to prepare and execute them"""
    def __init__(self, dev_key, api_url, retry_on_known_error,
                 retry_count_on_error, sleep_on_error, increase_sleep_on_error,
                 known_errors, httptype, method, **params):
        """Take useful properties from instantiated yapl class"""
        self.dev_key = dev_key
        self.api_url = api_url
        self.retry_on_known_error = retry_on_known_error
        self.retry_count_on_error = retry_count_on_error
        self.sleep_on_error = sleep_on_error
        self.increase_sleep_on_error = increase_sleep_on_error
        self.known_errors = known_errors
        self.httptype = httptype
        self.method = method
        self.params = params

    def prepare(self):
        url = '/'.join([self.api_url, self.method])
        self.params["key"] = self.dev_key
        return Request(self.httptype, url,  params=self.params).prepare()

    def execute(self):
        s = Session()
        count = self.retry_count_on_error if self.retry_on_known_error else 1
        for i in range(count):
            request = self.prepare()
            response = s.send(request)
            if response.status_code not in self.known_errors:
                return response
            else:
                sleep = self.sleep_on_error + i * self.increase_sleep_on_error
                time.sleep(sleep)


class _yaplRequestIter(object):
    """An iterator class for returning a sequence of requests where the
    result is a JSON with a nextPageToken key, a new call is made with the
    nextPageToken in the request with the execute() method"""
    def __init__(self, request_class):
        """Take instantiated request class and a limit property"""
        self.request_class = request_class
        self.carry_on = True

    def __iter__(self):
        return self

    def __next__(self):
        if not self.carry_on:
            raise StopIteration
        else:
            return self

    def prepare(self):
        return self.request_class.prepare()

    def execute(self):
        response = self.request_class.execute()
        try:
            next_page_token = response.json()["nextPageToken"]
        except ValueError:
            # Failed to load as JSON
            # TO DO: Put a log warning here
            self.carry_on = False
        except KeyError:
            # No more next pages
            self.carry_on = False
        self.request_class.params["pageToken"] = next_page_token
        return response


class batchRequest(object):
    def __init__(self):
        pass

    def add(self):
        pass

    def execute(self):
        pass


def main():
    y = yapl(dev_key='AIzaSyCLuPamAJyq-zvbTW66tulD_wrElN8Nd30')
    requests = y.requestIter(
        httptype='GET', method='search', part='snippet', type='video',
        channelId='UCZYTClx2T1of7BRZ86-8fow', maxResults=50
        )

    for request in requests:
        response = request.execute()
        print(response.json()["nextPageToken"])

#    response = y.request(httptype='GET', method='videos', id='e0oELHA6EvM',
#                         part='snippet').execute()

#     part='snippet', maxResults=50, channelId=channel_id,
#     type='video', safeSearch='none', publishedAfter=check_after

if __name__ == '__main__':
    main()
