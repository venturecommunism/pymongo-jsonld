from pymongo import MongoClient
client = MongoClient('localhost', 27017)
db = client.meteor
taskspending = db.taskspending

with open('/path/to/file') as f:
  content = [ x.strip('\n') for x in f.readlines() ]

'''

The rest below is for the JSON-LD examples.

'''

doc = {
    "http://schema.org/name": "Manu Sporny",
    "http://schema.org/url": {"@id": "http://manu.sporny.org/"},
    "http://schema.org/image": {"@id": "http://manu.sporny.org/images/manu.png"}
}

context = {
    "name": "http://schema.org/name",
    "homepage": {"@id": "http://schema.org/url", "@type": "@id"},
    "image": {"@id": "http://schema.org/image", "@type": "@id"}
}

lib = {
  "@context": {
    "dc": "http://purl.org/dc/elements/1.1/",
    "ex": "http://example.org/vocab#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "ex:contains": {
      "@type": "@id"
    }
  },
  "@graph": [
    {
      "@id": "http://example.org/library",
      "@type": "ex:Library",
      "ex:contains": "http://example.org/library/the-republic"
    },
    {
      "@id": "http://example.org/library/the-republic",
      "@type": "ex:Book",
      "dc:creator": "Plato",
      "dc:title": "The Republic",
      "ex:contains": "http://example.org/library/the-republic#introduction"
    },
    {
      "@id": "http://example.org/library/the-republic#introduction",
      "@type": "ex:Chapter",
      "dc:description": "An introductory chapter on The Republic.",
      "dc:title": "The Introduction"
    }
  ]
}

frame = {
  "@context": {
    "dc": "http://purl.org/dc/elements/1.1/",
    "ex": "http://example.org/vocab#"
  },
  "@type": "ex:Library",
  "ex:contains": {
    "@type": "ex:Book",
    "ex:contains": {
      "@type": "ex:Chapter"
    }
  }
}
