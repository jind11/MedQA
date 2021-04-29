# MedQA
Code and data for MedQA

This is the data and baseline source code for the paper: [Jin, Di, et al. "What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams." arXiv preprint arXiv:2009.13081 (2020)](https://arxiv.org/abs/2009.13081). If you would like to use the data or code, please cite the paper:

```
@article{jin2020disease,
  title={What Disease does this Patient Have? A Large-scale Open Domain Question Answering Dataset from Medical Exams},
  author={Jin, Di and Pan, Eileen and Oufattole, Nassim and Weng, Wei-Hung and Fang, Hanyi and Szolovits, Peter},
  journal={arXiv preprint arXiv:2009.13081},
  year={2020}
}
```

## Data

The data that contains both the QAs and textbooks can be downloaded from [this google drive folder](https://drive.google.com/file/d/1ImYUSLk9JbgHXOemfvyiDiirluZHPeQw/view?usp=sharing). A bit of details of data are explained as below:

- For QAs, we have three sources: US, Mainland of China, and Taiwan District, which are put in folders, respectively. All files for QAs are in jsonl file format, where each line is a data sample as a dict. The "XX_qbank.jsonl" files contain all data samples while we also provide an official random split into train, dev, and test sets. Those files in the "metamap" folders are extracted medical related phrases using the [Metamap](https://metamap.nlm.nih.gov/) tool. 

- For QAs, we also include the "4_options" version in for US and Mainland of China since we reported results for 4 options in the paper.

- For textbooks, we have two languages: English and simplified Chinese. For simplified Chinese, we provide two kinds of sentence spliting: one is split by sentences, and the other is split by paragraphs. 

PS: If you have any questions for the data, feel free to leave a message in the Issues.

## How to use the Source Code:

### IR Baseline

The IR baseline code is in the folder of "IR". This baseline code is adapted from the ["aristo-mini"](https://github.com/allenai/aristo-mini) repository. To experiment you'll need python 3.6. Then follow these steps.

1. Install the requirements:

```
cd IR
pip install -r requirements.txt
```

2. Add the project to your PYTHONPATH

```
export PYTHONPATH=$PYTHONPATH:`pwd`
```

3. Start a local Elasticsearch server

Download Elasticsearch 2.4.1 and run the server locally with out-of-the-box defaults. This can be done as follows:

```
wget https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/zip/elasticsearch/2.4.1/elasticsearch-2.4.1.zip
unzip elasticsearch-2.4.1.zip
cd elasticsearch-2.4.1
bin/elasticsearch
```

4. Configure your local Elasticsearch server

To configure your running Elasticsearch server for processing English corpus, issue this command:

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
          "type": "string",
          "similarity":"BM25"
        }
      }
    }
  }
}'
```

While for Chinese corpus, run this command:

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
          "analyzer": "smartcn",
          "type": "string",
          "similarity":"BM25"
        }
      }
    }
  }
}'
```

5. Populate your Elasticsearch server with your medical textbooks

In this step, we need to inject all medical textbooks into the server so that it will act as a knowledge base for IR. In the "IR/scripts" folder, the file of "insert_text_to_elasticsearch.py" is for processing English textbooks while "insert_text_to_elasticsearch_zh.py" is for Chinese corpus.

```
cat ${PATH_TO_TEXTBOOKS} | python scripts/insert_text_to_elasticsearch.py
```

6. Start the solver server

In this step, we run the following command to start answering the medical questions by matching each pair of concatenated question and answer candidate to the knowledge base, obtaining the corressponding matching score (i.e., BM25 matching score), and ranking the answer candidates by the matching scores. This script has two arguments to be specified: "data_path": the path to the medical quesiton data; "topn": we would like to get the top_n matched snippets from the knowledge base.

```
python aristomini/solvers/textsearch.py --data_path PATH_TO_QUESTIONS_DATA --topn TOP_N_MATCHING_SCORES_TO_FETCH
```

PS: In the "aristomini/solvers" folder, we also include a file named "textsearch_logIR.py" file, which is almost the same as "textsearch.py" except that it also logs some intermediate matching results for model analysis besides outputing the scores. Besdies, we also include files of "pmi.py" and "pmi_exe.py", which are for the PMI baseline model.
