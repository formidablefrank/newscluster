# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import time
from datetime import date, datetime
import re
from urlparse import urlparse

# Create your models here.
class Article(models.Model):
    headline = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    src = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    datepub = models.DateField()

    metadata = {}
    links = []
    titles = []
    words = []

    fakes = ['classifiedtrends', 'definitelyfilipino', 'du30newsinfo',
        'extremereaders', 'filipinewsph', 'getrealphilippines', 'theguard1an',
        'kalyepinoy', 'leaknewsph', 'dutertedefender', 'mindanation',
        'netizensph', 'newsmediaph', 'newstitans', 'okd2', 'pinoyfreedomwall',
        'pinoytrending', 'altervista', 'pinoyviralissues', 'pinoyworld',
        'publictrending', 'socialnewsph', 'tahonews', 'thevolatilian',
        'thinkingpinoy', 'trendingbalita', 'trendingnewsportal', 'trendtitan']

    links = []

    def __init__(self, metadata, links, words, src, domain, datepub, headline):
        self.metadata = metadata
        self.links = links
        self.words = words
        self.src = src
        self.domain = domain
        self.datepub = datepub
        self.headline = headline

    def __str__(self):
        return self.headline

    def analyze(self):
        results = []
        #ask if : ? ! exist in headlines
        if ':' in self.headline or '?' in self.headline or '!' in self.headline:
            results.append('HEADLINE - use of symbols')
        #ask if there is a capitalized word in headline
        for h in self.headline:
            if h.isupper():
                results.append('HEADLINE - uppercase word')
        #check if the domain belongs to a fake
        for f in self.fakes:
            if f in self.domain:
                results.append('DOMAIN - flagged as a fake news site')
        #check if any of the reference links is also a fake
        for f in self.fakes:
            for l in self.links:
                if f in l:
                    results.append('LINK - referenced link belong to a fake news site')
        if 'I' in self.words or 'i' in self.words:
            results.append('WORD CHOICE - use of "i" pronoun')
        results.append('INDIVIDUAL ANALYSIS COMPLETE')
        return results
