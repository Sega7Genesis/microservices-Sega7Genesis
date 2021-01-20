import requests
from datetime import datetime, timedelta
from rest_framework.response import Response
import time

SLEEP_TIME = 1


class my_circle_breaker(object):

    def __init__(self, max_retry, interval):
        self.max_retry = max_retry
        self.current_retry = 0
        self.is_fallback = False
        self.fallback_begin = datetime.now()
        self.interval = timedelta(seconds=interval)

    def do_request(self, url, http_method='get', headers={}, context={}):

        if self.is_fallback:

            if datetime.now() - self.fallback_begin < self.interval:
                return Response({'message': 'st'}, status=503)
            self.is_fallback = False

        if not self.is_fallback:
            while self.current_retry < self.max_retry:
                response = None
                is_available = True
                if http_method == 'get':
                    try:
                        response = requests.get(url, headers=headers)
                    except requests.exceptions.ConnectionError:
                        is_available = False

                elif http_method == 'post':
                    try:
                        response = requests.post(url, context, headers=headers)
                    except requests.exceptions.ConnectionError:
                        is_available = False

                elif http_method == 'delete':
                    try:
                        response = requests.delete(url, headers=headers)
                    except requests.exceptions.ConnectionError:
                        is_available = False

                else:
                    return Response({'message': 'server cant do your request'}, status=501)

                if not is_available:
                    self.current_retry += 1
                elif response.status_code == 204:
                    self.current_retry = 0
                    return Response(status=response.status_code, headers=response.headers)
                else:
                    self.current_retry = 0
                    return Response(response.json(), status=response.status_code, headers=response.headers)
                time.sleep(SLEEP_TIME)
            self.fallback_begin = datetime.now()
            self.is_fallback = True
            return Response({'message': 'u'}, status=503)
