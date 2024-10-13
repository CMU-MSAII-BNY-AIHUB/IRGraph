# Knowledge Graphs for Financial Unstructured Data through Large Language Models and Neo4j

### [Main Confluence](https://nyu-tmi-capstone.atlassian.net/wiki/spaces/SD/overview)

# Simple Run Instructions [Confluence](https://capstone-jira-confluence.atlassian.net/wiki/spaces/SD/pages/69468161/How+to+build+the+database+with+the+xml+file+we+provide)

## 1. Create the Neo4j Database

1. Go to the [Neo4j Aura](https://neo4j.com/aura/) to create an account and log in.
2. Click the "new instance" button on the page. Or if this is the first time you are using Neo4j, you should be directed to the page to create your first instance. **Remember to save your password somewhere!!**
3. It takes a few minutes to create the instance.
4. Copy down the connection URI which starts with `neo4j+s://` for further usage.
5. You can click open and enter the password you copied down before to connect to the instance and play around with your Neo4j database.

## 2. Run Our GitHub Repo

1. Pull down the entire repo. In the root directory `BKG`, run the following command to set up the environment:

   ```bash
   pip install -r requirements.txt
   ```

2. Follow the `config.ini.sample` to create your `config.ini` file, and put your instance URI and password in this file in the following format:

   ```ini
   [NEO4J]
   uri = <your neo4j instance uri>
   password = <your neo4j instance password>
   ```

3. Go to the `upstreamPipeline` folder. This is the folder where we run our upstream pipeline to create the knowledge graph database.

4. For a simple run, download and unzip `xml.rar`, and put them in a folder called `xml`:

   ```
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
   ```

5. Now you can run the below command to create from the XML file we provide and build your Neo4j knowledge graph database:

   ```bash
   python upstream_pipeline.py --save-dir "xml" --generate-from-rar
   ```

---
For more runtime options, stay tuned…
