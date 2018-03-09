#!/usr/bin/python
# coding: utf-8


YOUTUBE_CATEGORY = {
    "music":10,
    "films":1,
    "vehicles":2,
    "sport":17,
    "travels":19,
    "gaming":20,
    "people":22,
    "comedy":23,
    "entertainment":24,
    "news":25,
    "how to":26,
    "education":27,
    "activism":29,
    "science & technology":28,
    "science":28,
    "technology":28,
    "animals":15
}

PEERTUBE_CATEGORY = {
    "music":1,
    "films":2,
    "vehicles":3,
    "sport":5,
    "travels":6,
    "gaming":7,
    "people":8,
    "comedy":9,
    "entertainment":10,
    "news":11,
    "how to":12,
    "education":13,
    "activism":14,
    "science & technology":15,
    "science":15,
    "technology":15,
    "animals":16
}

def getCategory(category, type):
    if type == "youtube":
        return YOUTUBE_CATEGORY[category.lower()]
    else:
        return PEERTUBE_CATEGORY[category.lower()]