
from neo4j import GraphDatabase
import os
import sys
from schema import *
import xml.etree.ElementTree as ET

COMPANY = "COMPANY"
EARNINGSCALL = "EARNINGSCALL"
PARTICIPANT_SECTION = "PARTICIPANT_SECTION"
PRESENTATION_SECTION = "PRESENTATION_SECTION"
QA_SECTION = "QA_SECTION"

def extract_participants(section_element, header):
    operator = Person(
            id="-1",
            name=f"{header.company} operator"
        )
    participants = {"-1": operator}
    for person_element in section_element.findall('person'):
        person = Person(
            id=person_element.get('id'),
            company=person_element.get('company'),
            name=person_element.text
        )
        participants[person_element.get('id')] = person
    par_sec = ParticipantsSection(participants)
    return par_sec

def extract_presentation(section_element, participants):
    statements = []
    for statement_element in section_element.findall('statement'):
        speaker_element = statement_element.find('speaker')
        speaker_id=speaker_element.get('id')
        sentiment = "" if not speaker_element.find('text').findall('sentiment') \
                    else speaker_element.find('text').findall('sentiment')[0].text
        topic = "" if not speaker_element.find('text').findall('topic') \
                    else speaker_element.find('text').findall('topic')[0].text
        analysis = "" if not speaker_element.find('text').findall('analysis') \
                    else speaker_element.find('text').findall('analysis')[0].text

        statement = Statement(speaker=participants.get_participant(speaker_id),
                            text=speaker_element.find('text').text,
                            topic=topic  if topic else "",
                            sentiment=sentiment if sentiment else "",
                            analysis=analysis if analysis else "")

        statements.append(statement)
    return PresentationSection(statements)

def extract_qanda(section_element, participants):
    questions = {}
    transitions = []
    for question_element in section_element.findall('question'):
        speaker_element = question_element.find('speaker')
        sentiment = "" if not speaker_element.find('text').findall('sentiment') \
                    else speaker_element.find('text').findall('sentiment')[0].text
        topic = "" if not speaker_element.find('text').findall('topic') \
                    else speaker_element.find('text').findall('topic')[0].text
        analysis = "" if not speaker_element.find('text').findall('analysis') \
            else speaker_element.find('text').findall('analysis')[0].text
        question = Question(
            id=question_element.get('id'),
            speaker=participants.get_participant(speaker_element.get('id')),
            text=speaker_element.find('text').text,
            topic=topic  if topic else "",
            sentiment=sentiment if sentiment else "",
            analysis=analysis if analysis else ""
        )
        questions[question.id] = question

    for followup_question_element in section_element.findall('followQuestion'):
        speaker_element = followup_question_element.find('speaker')
        sentiment = "" if not speaker_element.find('text').findall('sentiment') \
                    else speaker_element.find('text').findall('sentiment')[0].text
        topic = "" if not speaker_element.find('text').findall('topic') \
                    else speaker_element.find('text').findall('topic')[0].text
        analysis = "" if not speaker_element.find('text').findall('analysis') \
                    else speaker_element.find('text').findall('analysis')[0].text
        question = Question(
            id=followup_question_element.get('id'), # This is the followup question id
            speaker=participants.get_participant(speaker_element.get('id')),
            text=speaker_element.find('text').text,
            topic=topic  if topic else "",
            sentiment=sentiment if sentiment else "",
            analysis=analysis if analysis else ""
        )
        # Tie each followup question to the parent question
        questions[followup_question_element.get('question_id')].addfollowup(question.id, question)

    # Since answer element does not have an unique identifier, here we assign a global answer id to each answer,
    # including followup answers.
    global_answer_id = 0
    for answer_element in section_element.findall('answer'):
        speaker_element = answer_element.find('speaker')
        sentiment = "" if not speaker_element.find('text').findall('sentiment') \
                    else speaker_element.find('text').findall('sentiment')[0].text
        topic = "" if not speaker_element.find('text').findall('topic') \
                    else speaker_element.find('text').findall('topic')[0].text
        analysis = "" if not speaker_element.find('text').findall('analysis') \
                    else speaker_element.find('text').findall('analysis')[0].text
        answer = Answer(
            id=global_answer_id,
            question=questions[answer_element.get('id')],
            speaker=participants.get_participant(speaker_element.get('id')),
            text=speaker_element.find('text').text,
            topic=topic  if topic else "",
            sentiment=sentiment if sentiment else "",
            analysis=analysis if analysis else ""
        )
        answer.question.addAnswer(answer)
        global_answer_id += 1

    for followup_answer_element in section_element.findall('followAnswer'):
        speaker_element = followup_answer_element.find('speaker')
        followup_answer_id = followup_answer_element.get('id') # Same as f_q_id
        sentiment = "" if not speaker_element.find('text').findall('sentiment') \
                    else speaker_element.find('text').findall('sentiment')[0].text
        topic = "" if not speaker_element.find('text').findall('topic') \
                    else speaker_element.find('text').findall('topic')[0].text
        analysis = "" if not speaker_element.find('text').findall('analysis') \
                    else speaker_element.find('text').findall('analysis')[0].text
        answer = Answer(
            id=global_answer_id,
            question=questions[followup_answer_element.get('question_id')].getfollowup(followup_answer_id),
            speaker=participants.get_participant(speaker_element.get('id')),
            text=speaker_element.find('text').text,
            topic=topic  if topic else "",
            sentiment=sentiment if sentiment else "",
            analysis=analysis if analysis else ""
        )
        # Tie each followup answer to follow up question
        answer.question.addAnswer(answer)
        global_answer_id += 1

    for transition_element in section_element.findall('transition'):
        speaker_element = transition_element.find('speaker')
        transition = Transition(
            speaker=participants.get_participant("-1"), # Operator
            text=speaker_element.find('text').text if speaker_element.find('text').text else ""
        )
        transitions.append(transition)


    return QASection(transitions=transitions, questions=questions)


def add_query(cyper, query):
    return cyper + query + "\n"

def make_participant_id(id):
    return f"participant{int(id)+1}" #offset -1

def make_content_id(id):
    return f"content{id}"

def make_question_id(id):
    return f"question{int(id)+1}" #offset -1

def make_follow_question_id(q_id, follow_up_q_id):
    return f"question{int(q_id)+1}follow_up_question{int(follow_up_q_id)+1}" #offset -1

def make_answer_id(answer_id):
    return f"answer{int(answer_id)+1}" #offset -1


def main(file, driver):
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    print(file)

    tree = ET.parse(file)
    root = tree.getroot()

    header_element = root.find('header')




    # Extract header information
    header_element = root.find('header')
    header = Header(
        company=header_element.find('company').text,
        quarter=header_element.find('quarter').text,
        time=header_element.find('time').text,
        currency=header_element.find('currency').text,
        note=header_element.find('note').text
    )
    print(header.quarter)
    participants_section = None
    for section_element in root.findall('body/section'):
        if section_element.get('name') == "Call Participants" or section_element.get('name') == "call participants":
            participants_section = extract_participants(section_element, header)
        elif section_element.get('name') == "Presentation ":
            presentation_section = extract_presentation(section_element, participants_section)
        elif section_element.get('name') == "Question and Answer":
            qa_section = extract_qanda(section_element, participants_section)
        else:
            print(f"Skip tag {section_element.get('name')}")

    transcript = Transcript(header, participants_section, presentation_section, qa_section)





    def generate_query_to_add_answer(question, neo4j_question_id, parent_question=None):
        query = ""
        parent_q_id="-1" if not parent_question else parent_question.id
        if neo4j_question_id == None: neo4j_question_id = make_question_id(question.id)


        for answer in question.answers:
            neo4j_answer_id = make_answer_id(answer.id)
            neo4j_participant_id = make_participant_id(answer.speaker.id)
            q = 'CREATE (%s: ANSWER {text: "%s", sentiment: "%s", topic: "%s", analysis: "%s"}) -[:ANSWER_TO] -> (%s) \n' % \
            (neo4j_answer_id, answer.text, answer.sentiment, answer.topic, answer.analysis, neo4j_question_id) + \
                'CREATE (%s)-[:ANSWERED]->(%s) \n' % (neo4j_participant_id, neo4j_answer_id) + \
                'CREATE (%s) -[:HAS_ANSWER] -> (%s)' % (neo4j_question_id, neo4j_answer_id) + \
                'CREATE (%s)-[:WAS_ANSWERED_BY]->(%s) \n' % (neo4j_answer_id, neo4j_participant_id)
            query = add_query(query, q)

        return query


    cypher = ""
    # process_header:
    header = transcript.header
    query = \
        'MERGE (%s:COMPANY {name: "%s"}) \n' % (COMPANY, header.company) + \
        'CREATE (%s:EARNINGSCALL {name: "%s", time: "%s"}) \n' % (EARNINGSCALL, header.quarter, header.time) + \
        'CREATE (%s) -[:HAS_EARNINGS] -> (%s)' % (COMPANY, EARNINGSCALL)

    cypher = add_query(cypher, query)

    # process_participants:
    participants_section = transcript.participants_section
    query = 'CREATE (%s) -[:HAS_SECTION]-> (%s:SECTION {name: "%s"}) \n' % (EARNINGSCALL, PARTICIPANT_SECTION, PARTICIPANT_SECTION)
    for participant in participants_section.participants:
        q = 'MERGE (%s:PARTICIPANT {name: "%s", company: "%s"})' \
        % (make_participant_id(participant.id), participant.name, participant.company) + \
        'CREATE (%s) - [:HAS_PARTICIPANT] -> (%s)' % (PARTICIPANT_SECTION, make_participant_id(participant.id))
        query = add_query(query, q)

    cypher = add_query(cypher, query)


    # process_presentation:
    presentation_section = transcript.presentation_section
    query = 'CREATE (%s) -[:HAS_SECTION]-> (%s:SECTION {name: "%s"}) \n' % (EARNINGSCALL, PRESENTATION_SECTION, PRESENTATION_SECTION)
    content_id = 0
    for content in presentation_section.statements:
        q = 'CREATE (%s) -[:HAS_CONTENT]-> (%s:CONTENT {text: "%s", sentiment: "%s", topic: "%s", analysis: "%s"}) \n' \
        % (PRESENTATION_SECTION, make_content_id(content_id), content.text, content.sentiment, content.topic, content.analysis) + \
            'CREATE (%s) -[:ANNOUNCE] -> (%s) \n' % (make_participant_id(content.speaker.id), make_content_id(content_id)) + \
            'CREATE (%s) -[:HAS_PARTICIPANT] -> (%s) \n' % (PRESENTATION_SECTION, make_participant_id(content.speaker.id))

        content_id += 1
        query = add_query(query, q)

    cypher = add_query(cypher, query)

    # process_qa_section:
    # Questions
    qa_section = transcript.qa_section
    query = 'CREATE (%s) -[:HAS_SECTION]-> (%s:SECTION {name: "%s"}) \n' % (EARNINGSCALL, QA_SECTION, QA_SECTION)
    # Iterate through all questions
    for question in qa_section.questions:
        neo4j_question_id = make_question_id(question.id)
        q = 'CREATE (%s) -[:HAS_QUESTION]->(%s:QUESTION {text: "%s", sentiment: "%s", topic: "%s", analysis: "%s"}) \n' % \
        (QA_SECTION, neo4j_question_id, question.text, question.sentiment, question.topic, question.analysis) + \
            'CREATE (%s)-[:ASKED]->(%s)' % (make_participant_id(question.speaker.id), neo4j_question_id)
        query = add_query(query, q)
        answer_query = generate_query_to_add_answer(question, neo4j_question_id=neo4j_question_id)
        query = add_query(query, answer_query)
        # Iterate through all follow-up questions associated with this question
        for follow_up_question in question.followup_questions.values():
            neo4j_follow_up_question_id = make_follow_question_id(question.id, follow_up_question.id)
            f_q = 'CREATE (%s) -[:HAS_FOLLOWUP_QUESTION]->(%s:QUESTION {text: "%s", sentiment: "%s", topic: "%s", analysis: "%s"})' \
            % (make_question_id(question.id), neo4j_follow_up_question_id, follow_up_question.text, follow_up_question.sentiment, follow_up_question.topic, follow_up_question.analysis)
            query = add_query(query, f_q)
            answer_query = generate_query_to_add_answer(follow_up_question,
                                                        neo4j_question_id=neo4j_follow_up_question_id,
                                                        parent_question=question)
            query = add_query(query, answer_query)


    cypher = add_query(cypher, query)

    records, summary, keys = driver.execute_query(cypher)






if __name__ == '__main__':
    URI = "neo4j+s://bc8b6e15.databases.neo4j.io"
    AUTH = ("neo4j", "Passward")

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()

    for file in sorted(os.listdir("/home/cehong/Desktop/Capstone/AuraDB/data")):
        main(f"/home/cehong/Desktop/Capstone/AuraDB/data/{file}", driver)
        
    driver.close()
