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

The data that contains both the QAs and textbooks can be downloaded from [this google drive folder](https://drive.google.com/file/d/1oujwwaLL0MnkbwUy4gH325ulaf2HnqCc/view?usp=sharing). A bit of details of data are explained as below:

- For QAs, we have three sources: US, Mainland of China, and Taiwan District, which are put in folders, respectively. All files for QAs are in jsonl file format, where each line is a data sample as a dict. The "XX_qbank.jsonl" files contain all data samples while we also provide an official random split into train, dev, and test sets. Those files in the "metamap" folders are extracted medical related phrases using the [Metamap](https://metamap.nlm.nih.gov/) tool.

- For textbooks, we have two languages: English and simplified Chinese. For simplified Chinese, we provide two kinds of sentence spliting: one is split by sentences, and the other is split by paragraphs. 

PS: If you have any questions for the data, feel free to leave a message in the Issues.

## TO-DO:

Add the baseline code.
