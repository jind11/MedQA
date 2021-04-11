## for chinese
curl -H 'Content-Type: application/json' -XPUT 'http://localhost:9200/knowledge' -d '
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
      "dynamic": "false",
      "properties": {
        "body": {
	      "analyzer": "smartcn",
          "type": "text"
        }
      }
  }
}'

curl -H 'Content-Type: application/json' -XGET "localhost:9200/knowledge/_analyze?pretty" -d'
{
"field": "body",
"text":  "我爱这世界！"
}
'

curl -XPUT 'http://localhost:9200/knowledge' -d '
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "sentence": {
      "dynamic": "false",
      "properties": {
        "body": {
	      "analyzer": "smartcn",
          "type": "string"
        }
      }
    }
  }
}'

curl -XPUT 'http://localhost:9200/knowledge' -d '
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "sentence": {
      "dynamic": "false",
      "properties": {
        "body": {
	      "analyzer": "smartcn",
          "type": "string",
          "similarity":"BM25"
        }
      }
    }
  }
}'

curl -XGET "localhost:9200/knowledge/_analyze?pretty" -d'
{
"field": "body",
"text":  "我爱这世界！"
}
'

curl -XGET "localhost:9200/knowledge" -d'
{
"type": "sentence",
"field": "body",
"id":  "AXFXCg2z8WfZWASYHjvr"
}
'

export PYTHONPATH=$PYTHONPATH:`pwd`

curl -XDELETE 'http://localhost:9200/knowledge'

cat /Users/jindi/Dropbox\ \(MIT\)/MedQA/data/official/textbooks/zh_sentence/all_books.txt | scripts/insert_text_to_elasticsearch_zh.py

cat /Users/jindi/Dropbox\ \(MIT\)/MedQA/data/official/textbooks/zh_paragraph/all_books.txt | scripts/insert_text_to_elasticsearch_zh.py

cat /data/medg/misc/jindi/nlp/datasets/MedQA/textbooks/zh_paragraph/all_books.txt | python scripts/insert_text_to_elasticsearch_zh.py

cat /data/medg/misc/jindi/nlp/datasets/MedQA/textbooks/zh_sentence/all_books.txt | python scripts/insert_text_to_elasticsearch_zh.py

# for english
