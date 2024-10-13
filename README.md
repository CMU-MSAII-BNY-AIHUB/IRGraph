# Knowledge Graphs for Financial Unstructured Data through Large Language Models and Neo4j

### [Confluence](https://nyu-tmi-capstone.atlassian.net/wiki/spaces/SD/overview)

# for a simple run
1. Create the neo4j database
go to the neo4j aura Neo4j Aura to create an account and log in.

click the “new instance“ button on the page. Or if this is the first time you are using neo4j, you should be directed to the page to create your first instance. Remember to save your password somewhere!!

It takes a few minutes to create the instance. 

Copy down the connection URI which starts with neo4j+s:// for further usage.

You can click open and put the password you copied down before to connect to the instance and play around with you neo4j database

2. Run our git hub repo
Pull down the entire repo. in the root directory BKG run the following command to set up the environment 



pip install -r requirements.txt
Follow the config.ini.sample to create your config.ini file and put your instance URI and password in this file in the following format:



[NEO4J]
uri = <your neo4j instance uri>
password = <your neo4j instance password>
Go to upstreamPipeline folder. This is the folder we run our upstream pipeline to create knowledge graph database

for a simple run, download and unzip xml.rar, and put them in a folder called xml



BKG
   └── ...
   └── requirements.txt
   └── config.ini
   └── upstreamPipeline
       └── ...
       └── upstream_pipeline.py
       └── xml
           └── BK-Q1-2018.xml
           └── ...
Now you can run the below command to create from the XML file we provide and build your neo4j knowledge graph database



python upstream_pipeline.py --save-dir "xml" --generate-from-rar
For more runtime options, stay tuned…
