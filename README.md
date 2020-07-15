[![Python Version](https://img.shields.io/badge/Python-3.5%2C%203.6-green.svg)](https://img.shields.io/badge/Python-3.5%2C%203.6-green.svg)


Speech Quality Subjective Evaluation
======

<p align="justify"> This repository provides four general subjective tests (MOS: mean opinion score; PK: preference test; SIM: speaker similarity test; XAB: XAB test) for voice conversion(VC) and speech synthesis (SS) evaluations. The evaluation results will output in an Excel file with statistic results. </p>  

## Subjective evaluations

<p align="justify"> For VC/SS, subjective evaluations are usually conducted. The general performance measurements of VC/SS are speech quality (the naturalness of converted/synthesized speech) and speaker similarity (the similarity between converted speech and target speech). The repository includes four types of subjective tests for VC/SS performance evaluation. Each test plays several speech files to listeners and ask them to give a specific score to evaluate each converted/synthesized file. The system will output an average score with a confidence interval of each test into a Excel file. </p>

### Mean opinion score (MOS):

- Speech quality (naturalness) evaluation
- System plays a speech file to a listener and asks him/her to give a score (1-5) to evaluate the speech quality of this speech file. 

### Speaker similarity test (SIM):

- Speaker similarity evaluation
- Proposed by the [Voice Conversion Challenge (VCC)](http://www.vc-challenge.org/) organize
- System plays a golden and a predicted speech files to a listener and asks him/her to measure that these two speeches are from the same speaker or not.  
- Four measurements are given: 1. *Definitely the same*; 2. *Maybe the same*; 3. *Maybe different*; 4. *Definitely different*.

### Preference test (PK):

- Speech quality or speaker similarity evaluations
- System plays two speech files of different methods to a listener and asks him/her to pick up the file with better performance.

### XAB test:

- Speaker similarity or speech quality evaluation
- System plays a golden file and two speech files of different methods to a listener and ask him/her to pick up the file that is more similar to the golden speech.

---
## Setup

### Install requirements

```
pip install -r requirements.txt

# For Mac user
pip install -U PyObjC 
```

### Folder structure

- data/{project}/: testing data of {project}.
- data/example/:  example speech files of XAB and MOS tests.
- results: output Excel file.
- src: source code.
- yml: testing configs and profiles.

---
## Usage
- Take project `EVAL1` as an example.

### 1. Data preparation
- Create `data/EVAL1/` folder.
- Put testing data of each method in `data/EVAL1/{method}`.
- Create data lists of all methods and put them in the same folder.

### 2. Config initialization
- Create `yml/EVAL1/`  folder
- Create `evaluation.yml`, `record.yml`, `test_system.yml`, and `text.yml` in `yml/EVAL1/` folder. 

### 3. Parse testing profile
- Create .yml format testing profile files for each testing type and subset corresponding to the `evaluation.yml` config. 
```
python run_pre.py EVAL1
```

### 4. Run evaluation
- Run evaluation and the results will be in the `/result/EVAL1_{type}.xlsx` files. Each listener's results will be in the `yml/EVAL1/{type}_{subset}_{userID}.yml` files.
- **-o {mode}**: set mode to control the output information; choice:[vc, as, others]. 
- Set mode **'vc'** will output complete details and mode **'others'** will only output overall results. 
```
python run_test.py EVAL1 -o {mode}
```

### 5. Get statistics
- Output evaluation results with statistics to the `/result/EVAL1_final_{type}.xlsx` files. 
```
python run_post.py EVAL1 -o {mode}
```

---
## COPYRIGHT

Copyright (c) 2020 Yi-Chiao Wu @ Nagoya University ([@bigpon](https://github.com/bigpon))  
E-mail: `yichiao.wu@g.sp.m.is.nagoya-u.ac.jp`  
Released under [Apache 2.0](http://www.apache.org/licenses/LICENSE-2.0)


