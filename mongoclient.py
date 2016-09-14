#!/usr/bin/env python
import sys
import subprocess
from subprocess import Popen, PIPE
import argparse
from pyld import jsonld
import json

import config

parser = argparse.ArgumentParser(description='Munge Documents with JSON-LD and Python')

parser.add_argument('--backup', action='store_true', help='back up the database')
parser.add_argument('--resetids', action='store_true', help='overwrite stats/all/index.txt with all current ids--should be fine but careful now!')
parser.add_argument('--getids', action='store_true', help="gets ids")

args = parser.parse_args()

if parser.parse_args().backup:
  print("Backing up...")
  p = subprocess.Popen([config.backup_cmd], shell=True, stdout=subprocess.PIPE)
  for line in iter(p.stdout.readline, b''):
    print line.strip('\n')
  p.stdout.close()
  p.wait()
  sys.exit()

if parser.parse_args().resetids:
  print("Overwriting ids with latest")
  p = subprocess.Popen([config.resetids_cmd], shell=True, stdout=subprocess.PIPE)
  for line in iter(p.stdout.readline, b''):
    print line.strip('\n')
  p.stdout.close()
  p.wait()
  sys.exit()

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
    print("error: something missing")

all = taskspending_applyfilter()
fromfile = taskspending_applyfilter(config.content)

if parser.parse_args().getids:
  with all as s:
    all_ids = [ str(x['_id']) for x in s ]
  for id in all_ids:
    print id
  sys.exit()

hascontext_query = [
  {"__context": {"$exists": 1}}
]

has_jsonld = taskspending_applyfilter(config.content, hascontext_query)

no_jsonld = all.count() - has_jsonld.count()

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

allaccounted = all.count() == fromfile.count()
if allaccounted or parser.parse_args().getids:
  print("total with jsonld context:", has_jsonld.count())
  print("total without jsonld context:", no_jsonld)
  print("output total:", output.count())
  for op in output:
    print(json.dumps(op, indent=8, sort_keys=True))
elif not allaccounted:
  print("all tasks not accounted for -- if you've been adding tasks maybe run --resetids")
