#!/usr/bin/env python
from pyld import jsonld
import json

import config

def taskspending_applyfilter(ids=None, query=None, excluding_ids=None):
  if excluding_ids:
    return config.taskspending.find({"$and": [{"_id": {"$nin": excluding_ids}}, {"$or":
      query
    }]})
  if query and ids:
    return config.taskspending.find({"$and": [{"_id": {"$in": ids}}, {"$or":
      query
    }]})
  elif ids:
    return config.taskspending.find({"_id": {"$in": ids}})
  elif not ids:
    return config.taskspending.find({})
  else:
    print "error: something missing"

all = taskspending_applyfilter()
fromfile = taskspending_applyfilter(config.content)

hascontext_query = [
  {"__context": {"$exists": 1}}
]

hascontext = taskspending_applyfilter(config.content, hascontext_query)

not_jsonld = all.count() - hascontext.count()

projects_and_contexts_query = [
  {"type": "project"},
  {"tags": "largeroutcome"},
  {"type": "context"},
  {"tags": "largercontext"},
]

projects_and_contexts = taskspending_applyfilter(config.content, projects_and_contexts_query)

with projects_and_contexts as s:
  project_and_context_ids = [ str(x['_id']) for x in s ]

not_project_or_context_test_query = [
  {"description": "test"},
]

not_project_or_context_tests = taskspending_applyfilter(config.content, not_project_or_context_test_query, project_and_context_ids)

with not_project_or_context_tests as s:
  not_project_or_context_test_ids = [ str(x['_id']) for x in s ]

#output = config.taskspending.find({"_id": {"$in": subsubtask_ids}})

output = taskspending_applyfilter(not_project_or_context_test_ids)

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
  print "total with jsonld context:", hascontext.count()
  print "total without jsonld context:", not_jsonld
  print "output total:", output.count()
  for op in output:
    print json.dumps(op, indent=8, sort_keys=True)
elif not allaccounted:
  print "all tasks not accounted for"
