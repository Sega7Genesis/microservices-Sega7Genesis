import requests
from datetime import datetime
from rest_framework.response import Response
import time

SLEEP_TIME = 1


class my_circle_breaker(object):

    def __init__(self, max_retry, interval):
        self.max_retry = max_retry
        self.current_retry = 0
        self.is_fallback = False
        self.fallback_begin = datetime.now()
        self.interval = interval

    def do_request(self, url, http_method='get', headers={}, context={}):

        if self.is_fallback:

            if datetime.now() - self.fallback_begin < self.interval:
                return Response({'message': 'st'}, status=503)
            self.is_fallback = False

        if not self.is_fallback:
            while self.current_retry < self.max_retry:
                response = None
                if http_method == 'get':
                    response = requests.get(url, headers=headers)

                elif http_method == 'post':
                    response = requests.post(url, context, headers=headers)

                elif http_method == 'delete':
                    response = requests.delete(url, headers=headers)

                else:
                    return Response({'message': 'server cant do your request'}, status=501)

                if response.status_code == 500:
                    self.current_retry += 1
                else:
                    self.current_retry = 0
                    return Response(response.json(), status=response.status_code, headers=response.headers)
                time.sleep(SLEEP_TIME)
            self.fallback_begin = datetime.now()
            self.is_fallback = True
            return Response({'message': 'u'}, status=503)
