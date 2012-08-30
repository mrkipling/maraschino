#!/usr/bin/env python
# $HeadURL: http://opensource.hld.ca/svn/trunk/ctw/weatherfeed.py $
# $Id: weatherfeed.py 315 2009-07-14 12:17:40Z dan $
# vim: ft=python ts=2 sw=2 et:

# Copyright Dan Cardamore <dan@hld.ca>
# Licensed under the GNU GPL version 2.0
# See GPL.gz in source distribution for more information

# Reads the weather from weather.com and stores it in dictionaries

from xml.dom.minidom import parse, parseString
import urllib2
import pprint

version = 0.2

class Weather:
  """ Get the weather from weather.com's XML feed.
  Dictionaries are created which can be accessed to get access
  to all the weather information.

  See currentConditions and forecast for the two dictionaries
  that will be of interest.

  To get the format of the dictionaries, print Weather.toString()
  after instantiation.
  """
  def __init__(self, location, metric=True):
    self.currentConditions = {}
    self.forecast = []
    temp = 0
    while temp < 10:
      self.forecast.append({})
      temp += 1

    self.location = location;
    if metric:
      self.units = "m"
    else:
      self.units = "s"

    self.dom = parseString(self._getData())
    self._getWeather()

  def __del__(self):
    self.dom.unlink()
  
  def _getData(self):
    """Connect to weather.com and get the weather as raw XML"""
    urlHandle = urllib2.urlopen("http://xoap.weather.com/weather/local/%s?cc=1&dayf=5&prod=xoap&link=xoap&unit=%s&par=1003666583&key=4128909340a9b2fc" %(self.location, self.units))
    return urlHandle.read()

  def _getWeather(self):
    for node in self.dom.childNodes[3].childNodes:
      if node.nodeName == 'cc':
        self._setCurrentConditions(node)

      if node.nodeName == 'dayf':
        self._setForecast(node)

      if node.nodeName == 'loc':
        self._setCurrentConditions(node)

    if self.forecast[0]["day"]["type"] == "N/A":
      self.forecast[0]["day"]["type"] = self.currentConditions["type"]
    if self.forecast[0]["day"]["wind"]["speed"] == "N/A" and self.forecast[0]["day"]["wind"]["direction"] == "N/A":
      self.forecast[0]["day"]["wind"]["speed"] = self.currentConditions["wind"]["speed"]
      self.forecast[0]["day"]["wind"]["direction"] = self.currentConditions["wind"]["direction"]

  def _setCurrentConditions(self, node):
    for elem in node.childNodes:
      if elem.nodeName == 'suns':
        self.currentConditions["sunset"] = elem.firstChild.data

      if elem.nodeName == 'sunr':
        self.currentConditions["sunrise"] = elem.firstChild.data

      if elem.nodeName == 'lsup':
        self.currentConditions["observed"] = elem.firstChild.data

      if elem.nodeName == 'obst':
        self.currentConditions["cityname"] = elem.firstChild.data

      if elem.nodeName == 'tmp':
        self.currentConditions["temperature"] = elem.firstChild.data

      if elem.nodeName == 't':
        self.currentConditions["type"] = elem.firstChild.data

      if elem.nodeName == 'flik':
        self.currentConditions["feelslike"] = elem.firstChild.data

      if elem.nodeName == 'vis':
        self.currentConditions["visibility"] = elem.firstChild.data

      if elem.nodeName == 'hmid':
        self.currentConditions["humidity"] = elem.firstChild.data

      if elem.nodeName == 'dewp':
        self.currentConditions["dewpoint"] = elem.firstChild.data

      if elem.nodeName == 'bar':
        self.currentConditions["bar"] = {}
        for subelem in elem.childNodes:
          if subelem.nodeName == 'r':
            self.currentConditions["bar"]["reading"] = subelem.firstChild.data

          if subelem.nodeName == 'd':
            self.currentConditions["bar"]["direction"] = subelem.firstChild.data

      if elem.nodeName == 'uv':
        self.currentConditions["uv"] = {}
        for subelem in elem.childNodes:
          if subelem.nodeName == 'i':
            self.currentConditions["uv"]["index"] = subelem.firstChild.data

          if subelem.nodeName == 't':
            self.currentConditions["uv"]["risk"] = subelem.firstChild.data

      if elem.nodeName == 'wind':
        self.currentConditions["wind"] = {}
        for subelem in elem.childNodes:
          if subelem.nodeName == 's':
            self.currentConditions["wind"]["speed"] = subelem.firstChild.data

          if subelem.nodeName == 'gust':
            self.currentConditions["wind"]["gusts"] = subelem.firstChild.data

          if subelem.nodeName == 'd':
            self.currentConditions["wind"]["degrees"] = subelem.firstChild.data

          if subelem.nodeName == 't':
            self.currentConditions["wind"]["direction"] = subelem.firstChild.data

  def _setForecast(self, node):
    day = 0
    for elem in node.childNodes:
      if elem.nodeName == 'lsup':
        pass

      if elem.nodeName == 'day':
        self._setForecastDay(elem, 
                              elem.attributes["d"].value,
                              elem.attributes["t"].value,
                              elem.attributes["dt"].value
                             )

  def _setForecastDay(self, node, index, day, date):
    index = int(index)
    self.forecast[index]["Day"] = day
    self.forecast[index]["Date"] = date
    for elem in node.childNodes:
      if elem.nodeName == 'hi':
        if elem.firstChild.data == "N/A":
          self.forecast[index]["high"] = "NA"
        else:
          self.forecast[index]["high"] = elem.firstChild.data

      if elem.nodeName == 'low':
        if elem.firstChild.data == "N/A":
          self.forecast[index]["low"] = "NA"
        else:
          self.forecast[index]["low"] = elem.firstChild.data

      if elem.nodeName == 'sunr':
        self.forecast[index]["sunrise"] = elem.firstChild.data

      if elem.nodeName == 'suns':
        self.forecast[index]["sunset"] = elem.firstChild.data

      if elem.nodeName == 'ppcp':
        self.forecast[index]["pop"] = elem.firstChild.data

      if elem.nodeName == 'hmid':
        self.forecast[index]["humidity"] = elem.firstChild.data

      if elem.nodeName == 'hmid':
        self.forecast[index]["humidity"] = elem.firstChild.data

      if elem.nodeName == 'part':
        if elem.attributes["p"].value == "d":
          self.forecast[index]["day"] = {}
          for subelem in elem.childNodes:
            if subelem.nodeName == 't':
              self.forecast[index]["day"]["type"] = subelem.firstChild.data

            if subelem.nodeName == 'ppcp':
              self.forecast[index]["day"]["pop"] = subelem.firstChild.data

            if subelem.nodeName == 'hmid':
              self.forecast[index]["day"]["humidity"] = subelem.firstChild.data

            if subelem.nodeName == 'wind':
              self.forecast[index]["day"]["wind"] = {}
              for windelem in subelem.childNodes:
                if windelem.nodeName == 's':
                  self.forecast[index]["day"]["wind"]["speed"] = windelem.firstChild.data

                if windelem.nodeName == 'gust':
                  self.forecast[index]["day"]["wind"]["gusts"] = windelem.firstChild.data

                if windelem.nodeName == 'd':
                  self.forecast[index]["day"]["wind"]["degrees"] = windelem.firstChild.data

                if windelem.nodeName == 't':
                  self.forecast[index]["day"]["wind"]["direction"] = windelem.firstChild.data

        if elem.attributes["p"].value == "n":
          self.forecast[index]["night"] = {}
          for subelem in elem.childNodes:
            if subelem.nodeName == 't':
              self.forecast[index]["night"]["type"] = subelem.firstChild.data

            if subelem.nodeName == 'ppcp':
              self.forecast[index]["night"]["pop"] = subelem.firstChild.data

            if subelem.nodeName == 'hmid':
              self.forecast[index]["night"]["humidity"] = subelem.firstChild.data

            if subelem.nodeName == 'wind':
              self.forecast[index]["night"]["wind"] = {}
              for windelem in subelem.childNodes:
                if windelem.nodeName == 's':
                  self.forecast[index]["night"]["wind"]["speed"] = windelem.firstChild.data

                if windelem.nodeName == 'gust':
                  self.forecast[index]["night"]["wind"]["gusts"] = windelem.firstChild.data

                if windelem.nodeName == 'd':
                  self.forecast[index]["night"]["wind"]["degrees"] = windelem.firstChild.data

                if windelem.nodeName == 't':
                  self.forecast[index]["night"]["wind"]["direction"] = windelem.firstChild.data






      if elem.nodeName == 'wind':
        self.forecast[index]["wind"] = {}
        for subelem in elem.childNodes:
          if subelem.nodeName == 's':
            self.forecast[index]["wind"]["speed"] = subelem.firstChild.data

          if subelem.nodeName == 'gust':
            self.forecast[index]["wind"]["gusts"] = subelem.firstChild.data

          if subelem.nodeName == 'd':
            self.forecast[index]["wind"]["degrees"] = subelem.firstChild.data

          if subelem.nodeName == 't':
            self.forecast[index]["wind"]["direction"] = subelem.firstChild.data



    

  def toString(self):
    print "Current Conditions: "
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(self.currentConditions)

    print "Forecasts:"
    day = 0
    for index in self.forecast:
      print "Day %d" %(day)
      pp.pprint(index)
      day += 1
  

if __name__ == "__main__":
  w = Weather("CAXX0343")
  print w.toString()
