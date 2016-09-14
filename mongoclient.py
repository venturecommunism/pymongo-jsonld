#!/usr/bin/env python
from pyld import jsonld
import json

import config

all = config.taskspending.find({})
fromfile = config.taskspending.find({"_id": {"$in": config.content}})

wjsonld = config.taskspending.find({"$and": [{"_id": {"$in": config.content}}, {"$or": [
  {"__context": {"$exists": 1}},
]}]})

not_jsonld = all.count() - wjsonld.count()

subtasks = config.taskspending.find({"$and": [{"_id": {"$in": config.content}}, {"$or": [ 
  {"type": "project"},
  {"tags": "largeroutcome"},
  {"type": "context"},
  {"tags": "largercontext"},
]}]})

with subtasks as s:
  subtask_ids = [ str(x['_id']) for x in s ]

subsubtasks = config.taskspending.find({"$and": [{"_id": {"$nin": subtask_ids}}, {"$or": [
  {"description": "test"},
]}]})

with subsubtasks as s:
  subsubtask_ids = [ str(x['_id']) for x in s ]

output = config.taskspending.find({"_id": {"$in": subsubtask_ids}})

#TODO: turn this into a function
newcursor = config.taskspending.find({"$and": [{"_id": {"$in": config.content}}, {"$or": 
  config.dict
}]})

print "newcursor count:", newcursor.count()
print "subtasks count:", subtasks.count()

compacted = jsonld.compact(config.doc, config.context)

#print "compacted"
#print(json.dumps(compacted, indent=8))

jsonld.compact('http://dbpedia.org/resource/John_Lennon', 'http://json-ld.org/contexts/person.jsonld')

expanded = jsonld.expand(compacted)

#print "expanded"
#print(json.dumps(expanded, indent=8))

jsonld.expand('http://json-ld.org/contexts/person.jsonld')

flattened = jsonld.flatten(config.doc)

#print "flattened"
#print(json.dumps(flattened, indent=8))

framed = jsonld.frame(config.lib, config.frame)

#print "framed", json.dumps(framed, indent=8)

normalized = jsonld.normalize(config.doc, {'algorithm': 'URDNA2015', 'format': 'application/nquads'})

#https://github.com/json-ld/json-ld.org/issues/53
#http://stackoverflow.com/questions/36636160/getting-rid-of-blank-node-in-subject-of-triple-generated-using-pyld
#print "normalized"
#print normalized

allaccounted = all.count() == fromfile.count() == 2043
if allaccounted:
  print "wjsonld total:", wjsonld.count()
  print "not jsonld total:", not_jsonld
  print "output total:", output.count()
  for op in output:
    print json.dumps(op, indent=8, sort_keys=True)
elif not allaccounted:
  print "all tasks not accounted for"
