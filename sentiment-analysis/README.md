# Sentiment Analysis on Earnings Call Transcript Data
This process is designed to analyze the sentiment of text data in both the Presentation and Q&A sections of the earnings call transcript, providing insights into the emotional tone conveyed in the text. This meta-analysis would enrich our knowledge graph representation. We utilize [FinBERT](https://github.com/ProsusAI/finBERT), a pre-trained language model specialized in financial sentiment analysis.

## Sentiment Analysis on the Presentation section
In this section, since the text in the is long per speaker, we assess the sentiment of each sentence. We classify the sentiment of each sentence and take the maximum score across positive, negative and neutral. Within the XML, we add 2 tags:
- `<sentiment>`: for each `<statement><speaker>` text which reflects the overall sentiment. 
- `<analysis>`: provides a comprehensive overview, breaking down the count and percentage of positive, negative, and neutral sentences. We list the specific sentences classified as negative, offering a more detailed perspective on critical points within the presentation.

## Sentiment Analysis on the Q&A section
In this section, we assesses the sentiment of each question and answer pair. The resulting sentiment analysis is encapsulated within XML tags for easy interpretation. We add 4 tags:
- `<sentiment>`: summarizes the overall sentiment for the questions, answers, and operator statements, indicating whether it is positive, negative, or neutral. 
- `<pos>`, `<neg>`, and `<neutr>`: sentiment scores for positive, negative, and neutral, respectively. A sentiment score closer to 1 indicates a stronger presence of that sentiment category within the analyzed text.

## How to Run
1. Install required packages
```bash
pip install -r requirements.txt
```

2. Put the file path in the `__main__` section of [run.py](run.py).

3. Run the script
```bash
python3 run.py
```

### Example
> Input file: [../data/sample_xml/The Bank of New York Mellon Corporation, Q3 2020 Earnings Call, Oct 16, 2020.xml](../data/sample_xml/The%20Bank%20of%20New%20York%20Mellon%20Corporation,%20Q3%202020%20Earnings%20Call,%20Oct%2016,%202020.xml)

> Output file: [xml_files/With_Sentiment_The Bank of New York Mellon Corporation, Q3 2020 Earnings Call, Oct 16, 2020.xml](../sentiment-analysis/xml_files/With_Sentiment_The%20Bank%20of%20New%20York%20Mellon%20Corporation,%20Q3%202020%20Earnings%20Call,%20Oct%2016,%202020.xml)
