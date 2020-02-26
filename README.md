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
which extract to ~30GB XML files. For this reason the aim is for the
scripts to parallelise and to remove as much unecessary information as
possible before importing to the database.

#### Current Status

This project currently downloads, extracts, splits dumps and parses them. Examples of usage will be added once the capability to build a  database is added.

## Requirements and installation

#### Software 

You need Python 3.x and the ability to run bash scripts. I highly
recommend installing [WSL on
Windows](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

#### Hardware

As the resulting database is very large development is being performed on
hardware provided by the University of Virginia. I aim to provide
functionality for normal computing hardware such that a subset of
Wikipedia could be created without the need for excessive computing power. 

## Usage

```
./talkpage.sh
```
Currently won't finish, as it will  try to download and extract all of Wikipedia's edit history.


## Contributions

I gladly accept contributions via GitHub pull requests, however please include documentation of the use case with your PR.
