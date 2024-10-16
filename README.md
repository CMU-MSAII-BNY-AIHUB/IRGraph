# IRGraph: Leveraging NLP, LLMs, and Knowledge Graphs for Investor Relations
This project commenced as a collaborative effort between Bank of New York (BNY) and Carnegie Mellon University (CMU), supported by a dedicated team of students, faculty, and practitioners. We express our gratitude to the faculty and students from the Master’s of Artificial Intelligence and Innovation program.

## Overview
Earnings calls are recurring events with important impacts on financial markets. Analysts need to identify and interpret
data from transcripts to inform reporting, advising, and planning. Quarter over quarter, Large language models (LLMs)
have helped surface insights from the text in these transcripts. However, the surrounding analysis requires connecting questions to answers through relationships between disparate information. Established techniques have shown some
limitations in providing relevant and grounded content leading to inaccurate, inexact, or incomplete findings. Knowledge
Graphs (KGs) stored in graph databases like Neo4j, help to provide context to the content through links between
companies, participants, stock price, etc. We provide a methodology for processing the unstructured data in transcripts. Using experiments related to the banking sector, we demonstrate the end-to-end process with benchmarks around several technical and business KPIs. Our open source implementation aims to enhance investor relations and communication through tools and techniques from NLP, LLMs and KGs. 

This project started with the name "BKGraph" representing the BNY stock ticker, BK, and KG representing knowledge graphs. We have broadened the scope to be "IRGraph" to represent Investor Relations. Please check our [Confluence page](https://nyu-tmi-capstone.atlassian.net/wiki/spaces/SD/overview) for more information.

## Set-Up Instructions
### 1. Create the Neo4j Database

1. Go to [Neo4j Aura](https://neo4j.com/aura/) to create an account and log in.
2. Click the "New Instance" button on the page. Or if this is the first time you are using Neo4j, you should be directed to the page to create your first instance. **Remember to save your password somewhere!!**
3. It takes a few minutes to create the instance.
4. Copy the connection URI which starts with `neo4j+s://` for further usage.
5. You can click "Open" and enter the password you copied down before to connect to the instance.
6. Start using the Neo4j database.

### 2. Run Our GitHub Repo

1. Clone the repo: `https://github.com/CMU-MSAII-BNY-AIHUB/IRGraph.git`

2. In the root directory `IRGraph`, run the following command to set up the environment:

   ```bash
   pip install -r requirements.txt
   ```

3. Follow the `config.ini.sample` to create your `config.ini` file, and put your instance URI and password in this file in the following format:

   ```ini
   [NEO4J]
   uri = <your neo4j instance uri>
   password = <your neo4j instance password>
   ```

4. Go to the `pipeline` folder. This is the folder where we run our upstream pipeline to create the knowledge graph database.

5. For a simple run, download and unzip `pipeline/xml.rar`, and put them in a folder called `xml`:

   ```
   IRGRAPH
   └── ...
   └── requirements.txt
   └── config.ini
   └── pipeline
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
