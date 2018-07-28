#!/usr/bin/env python3

import logging
import queue
import re
import time

from collections import deque
from multiprocessing.pool import ThreadPool

from dns.resolver import Resolver, NXDOMAIN, NoAnswer, Timeout, NoNameservers

logger = logging.getLogger(__name__)


def find_email(line):
    """
    Returns the most plausable email in a given line
    """
    emails = re.findall(r"[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}", line, re.IGNORECASE)
    if not emails:
        return None

    return sorted(emails, key=lambda x:len(x))[-1]


class MXResolver:
    def __init__(self, nameservers, queue_max_size=5000, max_resolving=100):
        self.resolver = Resolver(configure=False)
        self.resolver.nameservers = nameservers

        self.queue_max_size = queue_max_size

        self.queue = deque()
        self.mxes = {None: None}

        self._resolving = set()
        self._resolved = queue.Queue()
        self._pool = ThreadPool(processes=max_resolving)


    def handle_line(self, line):
        """
        Input a new line to parse, return lines that can be removed
        from the queue.
        """
        email_addr = find_email(line)
        if email_addr:
            domain = email_addr.split('@')[-1].lower()
            if domain not in self._resolving and domain not in self.mxes:
                self.resolve_domain(domain)
            self.queue.append((domain, line))
        else:
            self.queue.append((None, line))

    def empty_queue(self, empty=False):
        while True:
            try:
                result = self._resolved.get_nowait()
            except queue.Empty:
                pass
            else:
                domain, mxes = result
                self.mxes[domain] = mxes
                self._resolving.discard(domain)

            while self.queue and self.queue[0][0] in self.mxes:
                domain, line = self.queue.popleft()
                yield self.mxes[domain], line

            if empty:
                queue_max_size = 0
            else:
                queue_max_size = self.queue_max_size

            if len(self.queue) <= queue_max_size:
                break

            time.sleep(0.1)

    def resolve_domain(self, domain):
        logger.debug('Resolving domain %s' % (domain, ))
        self._resolving.add(domain)
        self._pool.apply_async(self.resolve_mx, (domain, ))

    def resolve_mx(self, domain):
        logger.debug('Trying to resolve %s' % (domain, ))
        mxes = []
        try:
            mxes = [x.exchange.to_text().strip('.').lower() for x in self.resolver.query(domain, 'MX')]
        except NXDOMAIN:
            logger.debug('No isp for %s' % (domain, ))
        except NoAnswer:
            logger.debug('No answer for %s' % (domain, ))
        except Timeout:
            logger.debug('Timeout for %s' % (domain, ))
        except NoNameservers:
            logger.debug('No nameservers found %s' % (domain, ))

        logger.debug('Resolved domain %s to %r' % (domain, mxes))
        self._resolved.put((domain, mxes))


class PatternMatcher:
    def __init__(self, patterns):
        self.patterns = []
        for pattern in patterns:
            self.patterns += self.expand_pattern(pattern)

    def expand_pattern(self, pattern):
        pattern = re.escape(pattern)
        if pattern.endswith('?'):
            pattern = '%s.[a-z]{2,}' % pattern[:-2]

        pattern += '$'

        if pattern.startswith(r'\.'):
            pattern = '(.+|^)%s' % pattern[2:]
        else:
            pattern = '^' + pattern

        return [re.compile(pattern)]

    def __call__(self, mxes):
        for mx in mxes:
            for pattern in self.patterns:
                if pattern.match(mx):
                    return True

        return False
