# Text Search Solver

The text search solver uses an Elasticsearch index to score the choices in multiple choice questions. It is meant to be an example baseline [Information retrieval](https://en.wikipedia.org/wiki/Information_retrieval) solver.

## How it works

When given a question like this:

```json
{
  "stem" : "What color is the sky?",
  "choices" : [
     { "label" : "A", "text" : "red" },
     { "label" : "B", "text" : "green" },
     { "label" : "C", "text" : "blue" }
  ]
}
```

This solver will produce three queries to the Elasticsearch index:

* `What color is the sky? red`
* `What color is the sky? green`
* `What color is the sky? blue`

The Elasticsearch **score** of the first document returned is used as a confidence for each choice. For example:

* `What color is the sky? red` **Score: 0.3**
* `What color is the sky? green`  **Score: 0.1**
* `What color is the sky? blue` **Score: 0.6**

These numbers are reported directly in the response:

```json
{
   "multipleChoiceAnswer" : {
      "choiceConfidences" : [
         {
            "choice" : { "label" : "A", "text" : "red" },
            "confidence" : 0.3
         },
         {
            "choice" : { "label" : "B", "text" : "green" },
            "confidence" : 0.1
         },
         {
            "choice" : { "label" : "C", "text" : "blue" },
            "confidence" : 0.6
         }
      ]
   },
   "solverInfo" : "TextSearchSolver"
}
```

## Starting the Text Search Solver

To use the Text Search Solver, you need to populate a local Elasticsearch index with sentences.

### Start a local Elasticsearch server

Download [Elasticsearch 2.4.1](https://www.elastic.co/downloads/past-releases/elasticsearch-2-4-1) and run the server locally with out-of-the-box defaults.

At time of writing, this can be done as follows:

```
wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/zip/elasticsearch/2.4.1/elasticsearch-2.4.1.zip
unzip elasticsearch-2.4.1.zip
cd elasticsearch-2.4.1
bin/elasticsearch
```

### Configure your local Elasticsearch server

The default settings for Elasticsearch are meant for production use, involving replication and sharding. In the case of this simple solver, we'll be running it on a single machine, so the default number of replicas and shards have to be adjusted.

In addition, we want to explicitly declare that the index `knowledge` will contain documents with property `body` that should be indexed using the [Snowball analyzer](https://www.elastic.co/guide/en/elasticsearch/reference/2.4/analysis-snowball-tokenfilter.html) for word stemming.

To configure your running Elasticsearch server with these settings, issue this command:

```
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
          "analyzer": "snowball",
          "type": "string"
        }
      }
    }
  }
}'
```

### Populate your Elasticsearch server with interesting sentences

Aristo-mini includes a Python script ([insert_text_to_elasticsearch.py](/../../scripts/insert_text_to_elasticsearch.py) that will insert sentences from text files into a locally running Elasticsearch solver. To use it
you'll need to obtain a text file with sentences and use this script.

#### Obtain a text file

As an illustration of a corpus relevant to the questions that the Aristo project focuses on, we have gathered 1197377 lines of text that are loosely associated with grade school level science and loosely use grade school level terminology. The text was drawn from Simple Wiki (~1.1M lines), Simple Wiktionary (~32k lines), and the Web (~50k lines), filtered by terminology and/or subject tags (for Simple Wiki pages). These lines of text are in a single file [aristo-mini-corpus-v1.txt.gz](https://s3-us-west-2.amazonaws.com/aristo-public-data/aristo-mini-corpus-v1.txt.gz) (35MB compressed, 99MB uncompressed). The text in this corpus obtained from Simple Wiki is offered under the [CC BY-SA 3.0 license](https://creativecommons.org/licenses/by-sa/3.0/legalcode).

#### Insert sentences into the Elasticsearch index

Use the `insert-text-to-elasticsearch.py` script to operate on the above text file (assuming you saved it in `/tmp`):

   ```bash
   gzcat /tmp/aristo-mini-corpus-v1.txt.gz | scripts/insert_text_to_elasticsearch.py
   ```

This will begin issuing inserts to the Elasticsearch index running locally.

#### Watch progress and wait for the insertion program to conclude

You will see output that looks like this:

   ```
   Posted 100000 documents (11158897 bytes) to http://localhost:9200/knowledge/sentence/_bulk. Elasticsearch errors = False
   Posted 100000 documents (8940144 bytes) to http://localhost:9200/knowledge/sentence/_bulk. Elasticsearch errors = False
   ...
   Posted 100000 documents (9102358 bytes) to http://localhost:9200/knowledge/sentence/_bulk. Elasticsearch errors = False
   Posted 41860 documents (3790949 bytes) to http://localhost:9200/knowledge/sentence/_bulk. Elasticsearch errors = False
   Documents posted: 1541860
   ```

Note: the script `insert_text_to_elasticsearch.py` will break up lines into sentences by splitting on the `.` character. Because some lines contain multiple sentences, the number of documents inserted is greater than the number of lines in the file.

### Start the solver server

```bash
python aristomini/solvers/textsearch.py
```

The solver will query the locally running Elasticsearch index.

## Solver performance

You can use the Evaluation UI to submit many questions to your solver at once.

Using the above Elasticsearch settings and the `aristo-mini-corpus-v1.txt.gz` corpus, as of November 2016, here is solver's performance on the provided exams:

| Exam file                               | Score                                    |
| --------------------------------------- | ---------------------------------------- |
| AI2-8thGr-NDMC-Feb2016-Dev.jsonl        | 27 correct / 65 answered = 41% correct   |
| AI2-8thGr-NDMC-Feb2016-Train.jsonl      | 128 correct / 293 answered = 43% correct |
| AI2-Elementary-NDMC-Feb2016-Dev.jsonl   | 41 correct / 84 answered = 48% correct   |
| AI2-Elementary-NDMC-Feb2016-Train.jsonl | 196 correct / 432 answered = 45% correct |
