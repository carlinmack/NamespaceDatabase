## Namespace Database

This project is a collection of scripts that creates a database of edits for a  Wikipedia namespace.

👉 Wikipedia Research Page - [Classifying Actors on Wikipedia Talk Pages](https://meta.wikimedia.org/wiki/Research:Classifying_Actors_on_Talk_Pages#Goals)

This is challenging as Wikipedia serves its dumps in ~200MB archives
which extract to ~40GB XML files. For this reason, the aim is for the
scripts to parallelise and to only import necessary information to the database.

> If there is a feature you'd like, or a roadblock to you using this, please [create an issue!](https://github.com/carlinmack/NamespaceDatabase/issues/new)


## Contents

  * [Current Status](#Current-Status)
* [Requirements and installation](#Requirements-and-installation)
  * [Software](#Software)
  * [Hardware](#Hardware)
* [Usage](#Usage)
* [Contributions](#Contributions)

Another aim of this project is to create documentation to promote research into Wikipedia which can be performed in a variety of areas:
|                             |                                                                                                                                                                                                                                                                                                                                                                                                                 |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Classification              | Javanmardi, Sara, David W. McDonald, and Cristina V. Lopes. "Vandalism detection in Wikipedia: a high-performing, feature-rich model and its reduction through Lasso." In *Proceedings of the 7th International Symposium on Wikis and Open Collaboration*, pp. 82-90. 2011. 👉 [PDF](https://www.ics.uci.edu/~sjavanma/WikiSym-2011.pdf)                                                                       |
| Digital Humanities          | Schneider, Jodi, Alexandre Passant, and John G. Breslin. "A content analysis: How Wikipedia talk pages are used." (2012). 👉 [PDF](http://socialsemantics.org/files/publications/20100426_webs2010a.pdf)                                                                                                                                                                                                        |
| Natural Language Processing | Rawat, Charu, Arnab Sarkar, Sameer Singh, Rafael Alvarado, and Lane Rasberry. "Automatic Detection of Online Abuse and Analysis of Problematic Users in Wikipedia." In *2019 Systems and Information Engineering Design Symposium (SIEDS)*, pp. 1-6. IEEE, 2019. 👉 [PDF](https://meta.wikimedia.org/wiki/File:Automatic_Detection_of_Online_Abuse_and_Analysis_of_Problematic_Users_in_Wikipedia_preprint.pdf) |
| Network Analysis            | Massa, Paolo. "Social networks of Wikipedia." In *Proceedings of the 22nd ACM conference on Hypertext and hypermedia*, pp. 221-230. 2011. 👉 [PDF](https://www.gnuband.org/papers/social_networks_of_wikipedia/)                                                                                                                                                                                                |
| Prediction                  | Martinez-Ortuno, Sergio, Deepak Menghani, and Lars Roemheld. "Sentiment as a Predictor of Wikipedia Editor Activity." 👉 [PDF](http://cs229.stanford.edu/proj2014/Sergio%20Martinez-Ortuno,%20Deepak%20Menghani,%20Lars%20Roemheld,%20Sentiment%20as%20a%20Predictor%20of%20Wikipedia%20Editor%20Activity.pdf)                                                                                                  |


#### Current Status

This project currently:

* Allow selection of wiki, namespace, dump, among other parameters 
* Downloads dumps from the fastest mirror
* Splits them into partitions for parallel processing
* Parses, extracts and imports features in parallel into a MySQL database. Errors are logged to a log file unless it stops the parsing of the partition in which it is logged to the database.
* Allow users to be able to direct output to text file.

In the future I aim to add:

* Allow users to provide their own option files for the database so they don't have to edit code.
* Allow users to pass in a filename directly to splitwiki or parse. 

## Requirements and installation

#### Software 

You need Python >3.5 and the ability to run bash scripts. If you are on Windows you will need to install [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10). 

Additionally, you need to have a MySQL database, which you can hopefully have set up for you by an administrator. If not, start from [here](https://dev.mysql.com/doc/refman/8.0/en/installing.html). 

#### Hardware

The resulting database has at least 100x reduction in size from the extracted dump. Additionally, different namespaces have different requirements - there are relatively few edits on namespaces other than main. Therefore, it may be possible to create a database of all edits on non-main namespaces on consumer hardware. 

## Usage

Enter a command prompt in the top level of the directory, run:

```
python -m pip install -r requirements.txt
```

If a database is not set up, you can test the program with:

```
python nsdb.py --test --dryrun
```

This writes output to text files rather than the database. Due to the `test` parameter this will only download and parse one archive under 50MB. The output of this is currently not valid for creating a database as a dummy foreign key of -1 is used for user_table_id.

If a database is set up, edit the database connection in Database.py and test the connection:

```
python Database.py
```

Once this returns the database and cursor succesfully, find out the values for the parameters to be passed to nsdb.py:
* wiki is the name of the wiki, for example enwiki, frwiki, zhwiktionary, etc
* dump is the date of the dump that you want to use. Leave this blank to use the most recent. If you are planning to run this to completion, set this parameter so that your database is consistent
* namespaces is the list of namespaces which you would like to create a database for.
* dataDir parameter is where you would like the partitions to be stored. It's likely that you would want to set this to the path of external storage. If enough space is available on your computer set this to `../`.
* maxSpace is the free storage that you would like this to use
* freeCores to the number of cores you do not want the program to use

To create a list of dumps then, in parallel, download and insert the features into the database, include relevant parameters as follows:

```
python nsdb.py [-w WIKI] [-d DUMP] [-n NAMESPACES [NAMESPACES ...]] [-D DATADIR] [-s MAXSPACE] [-c FREECORES]
```

If dumps are extracted, they can also be parsed manually and it's features can be added to the database with:

```
python parse.py
```

To split the first dump in the `dumps/` folder into ~40 partitions in the `partitions/` folder run:

```
python splitwiki.py
```

👉 [Documentation of all available modules](DOCUMENTATION.md)

👉 [Schema of the database](schema.md)

## Contributions

I gladly accept contributions via GitHub pull requests! Please create an issue first so 
I can advise you :)
