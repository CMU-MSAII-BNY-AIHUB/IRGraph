import sentiment_analysis_xml as SA

if __name__ == "__main__":
    xml_file_path = '../data/sample_xml/The Bank of New York Mellon Corporation, Q3 2020 Earnings Call, Oct 16, 2020.xml'
    SA.complete_sentiment_tagging(xml_file_path)