# Classifying Actors on Talk Pages

[Project Page](https://meta.wikimedia.org/wiki/Research:Classifying_Actors_on_Talk_Pages#Goals)

## Contents

* [Introduction](#Introduction)
  * [Current Status](#Current-Status)
* [Requirements and installation](#Requirements-and-installation)
  * [Software](#Software)
  * [Hardware](#Hardware)
* [Usage](#Usage)
* [Contributions](#Contributions)
   
## Introduction

This project is a collection of scripts that creates a database of edits in
a namespace of Wikipedia. This is useful for analysis of language on
Wikipedia. 

This is challenging as Wikipedia serves its dumps in ~200MB archives
which extract to ~40GB XML files. For this reason, the aim is for the
scripts to parallelise and to remove as much unnecessary information as
possible before importing to the database.

#### Current Status

This project currently downloads, parses dumps and adds them to a database.

## Requirements and installation

#### Software 

You need Python 3.x and the ability to run bash scripts. I highly
recommend installing [WSL on
Windows](https://docs.microsoft.com/en-us/windows/wsl/install-win10). 

Additionally you need to have a mysql database, which you can hopefully have set up for you by an administrator. If not start from [here](https://dev.mysql.com/doc/refman/8.0/en/installing.html). 

#### Hardware

As the resulting database is very large, development is being performed on
hardware provided by the University of Virginia. I aim to provide
functionality for normal computing hardware such that a subset of
Wikipedia could be created without the need for excessive computing power. 

## Usage

To create a list of dumps, download the first, partition it and add them to a database run.

```
python talkpages.py
```


## Contributions

I gladly accept contributions via GitHub pull requests, however please include documentation of the use case with your PR.
