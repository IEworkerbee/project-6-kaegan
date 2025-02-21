"""
Resource: Brevets
"""
from flask import Response, request, jsonify
from flask_restful import Resource
import json

# You need to implement this in database/models.py
from database.models import Brevet, Checkpoint

# MongoEngine queries:
# Brevet.objects() : similar to find_all. Returns a MongoEngine query
# Brevet(...).save() : creates new brevet
# Brevet.objects.get(id=...) : similar to find_one

# Two options when returning responses:
#
# return Response(json_object, mimetype="application/json", status=200)
# return python_dict, 200
#
# Why would you need both?
# Flask-RESTful's default behavior:
# Return python dictionary and status code,
# it will serialize the dictionary as a JSON.
#
# MongoEngine's objects() has a .to_json() but not a .to_dict(),
# So when you're returning a brevet / brevets, you need to convert
# it from a MongoEngine query object to a JSON and send back the JSON
# directly instead of letting Flask-RESTful attempt to convert it to a
# JSON for you.

class BrevetsName(Resource):
    
    def get(self):
        brevets = Brevet.objects().to_json()
        return Response(brevets, mimetype="application/json", status=200)
    
    def post(self):
        input_json = request.json
        brevet = Brevet(**input_json).save()
        ret_val = {"id": str(brevet.id)}
        return ret_val, 200