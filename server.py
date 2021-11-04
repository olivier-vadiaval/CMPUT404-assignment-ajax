#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Copyright 2021 Olivier Vadiavaloo
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, redirect, send_from_directory
import json, copy

app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data
        self.notify_all(entity, data)

    #  The methods notify_all, add_listener, get_listener, clear_listener, clear
    #  were obtained from the course examples in the cmput404-slides repository.
    #
    #  Copyright 2013 Abram Hindle
    #  Copyright 2019 Hazel Victoria Campbell
    #
    #  Source:
    #      https://github.com/uofa-cmput404/cmput404-slides/blob/master/examples/ObserverExampleAJAX/server.py
    #
    #  Accessed November 2, 2021
    #
    def notify_all(self, entity, data):
        for listener in self.listeners:
            self.listeners[listener][entity] = data

    def add_listener(self, listener_name):
        self.listeners[listener_name] = copy.deepcopy(self.space)

    def get_listener(self, listener_name):
        return self.listeners.get(listener_name)

    def clear_listener(self, listener_name):
        self.listeners[listener_name] = dict()

    def clear(self):
        self.space = dict()
        self.listeners = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()          

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    return redirect("/static/index.html")

@app.route("/static/index.html")
def serve_index():
    '''Requirements:  The webservice can serve /static/index.html'''
    return send_from_directory('static', 'index.html')

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    data = flask_post_json()
    try:
        myWorld.set(entity, data)
        return json.dumps(data), 200
    except:
        return '', 500

#  The methods get_listener and add_listener were obtained from
#  the course examples on the cmput404-slides repository.
#
#  Copyright 2013 Abram Hindle
#  Copyright 2019 Hazel Victoria Campbell
#
#  Source:
#      https://github.com/uofa-cmput404/cmput404-slides/blob/master/examples/ObserverExampleAJAX/server.py
#
#  Accessed November 2, 2021
#
@app.route("/listener/<entity>", methods=['PUT', 'POST'])
def add_listener(entity):
    myWorld.add_listener(entity)
    return json.dumps(dict())

@app.route("/listener/<entity>", methods=['GET'])
def get_listener(entity):
    v = myWorld.get_listener(entity)
    myWorld.clear_listener(entity)
    return json.dumps(v)

@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''
    return json.dumps(myWorld.world()), 200

@app.route("/entity/<entity>")    
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    return json.dumps(myWorld.get(entity)), 200

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    return json.dumps(myWorld.world()), 200

if __name__ == "__main__":
    app.run()
