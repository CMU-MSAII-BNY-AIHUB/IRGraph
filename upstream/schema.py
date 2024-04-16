class Transcript:
    def __init__(self, header, participants_section, presentation_section, qa_section):
        self.header = header
        self.participants_section = participants_section
        self.presentation_section = presentation_section
        self.qa_section = qa_section

class Header:
    def __init__(self, company, title, time, currency, note):
        self.company = sanitize(company)
        self.title = sanitize(title)
        self.time = sanitize(time)
        self.currency = currency
        self.note = sanitize(note)

class ParticipantsSection:
    def __init__(self, participants=None, name="call participants"):
        self.name = sanitize(name)
        self.__participantsDict__ = participants
        self.participants = participants.values()

    def get_participant(self, participants_id):
        return self.__participantsDict__[participants_id]


class Person:
    def __init__(self, id, position=None, group=None, name=None):
        self.position = position
        self.group = group
        self.id = id
        self.name = sanitize(name)

    def __repr__(self):
        return self.name + ' ' + self.position

class Statement: # Content in the schema
    def __init__(self, speaker:Person, text, topic="", sentiment="", analysis=""):
        self.speaker = speaker
        self.text = sanitize(text)
        self.topic = sanitize(topic)
        self.sentiment = sanitize(sentiment)
        self.analysis = sanitize(analysis)


class PresentationSection:
    def __init__(self, statements=None, name="Presentation"):
        self.name = name
        self.statements = statements if statements else []


class QASection:
    def __init__(self, transitions=None, questions=None):
        self.transitions = transitions if transitions else []
        self.__questionsDict__ = questions if questions else {}
        self.questions = questions.values()

    def get_question(self, question_id):
        return self.__questionsDict__[question_id]

class Transition:
    def __init__(self, speaker, text):
        self.speaker = speaker
        self.text = sanitize(text)

class Question:
    def __init__(self, id, speaker, text, topic="", sentiment=""):
        self.id = id
        self.speaker = speaker
        self.text = sanitize(text)
        self.topic = sanitize(topic)
        self.sentiment = sanitize(sentiment)

        self.followup_questions = {} # A dictionary store id-question pair: {followup_question_id: followup_question}
        self.answers = [] # A list of Answers

    def addfollowup(self, id, question):
        self.followup_questions[id] = question

    def getfollowup(self, id):
        return self.followup_questions[id]

    def addAnswer(self, answer):
        self.answers.append(answer)

class Answer:
    def __init__(self, id, question, speaker, text, topic="", sentiment=""):
        self.id = id
        self.question=question
        self.speaker = speaker
        self.text = sanitize(text)
        self.topic = sanitize(topic)
        self.sentiment = sanitize(sentiment)

class Transcript:
    def __init__(self, header, participants_section, presentation_section, qa_section):
        self.header = header
        self.participants_section = participants_section
        self.presentation_section = presentation_section
        self.qa_section = qa_section

class Header:
    def __init__(self, company, quarter, time, currency, note):
        self.company = sanitize(company)
        self.quarter = sanitize(quarter)
        self.time = sanitize(time)
        self.currency = currency
        self.note = sanitize(note)

class ParticipantsSection:
    def __init__(self, participants=None, name="call participants"):
        self.name = sanitize(name)
        self.__participantsDict__ = participants
        self.participants = participants.values()

    def get_participant(self, participants_id):
        return self.__participantsDict__[participants_id]


class Person:
    def __init__(self, id, company=None, name=None):
        self.company = sanitize(company)
        self.id = id
        self.name = sanitize(name)

    def __repr__(self):
        return self.name + ' ' + self.position

class Statement: # Content in the schema
    def __init__(self, speaker:Person, text, topic="", sentiment="", analysis=""):
        self.speaker = speaker
        self.text = sanitize(text)
        self.topic = sanitize(topic)
        self.sentiment = sanitize(sentiment)
        self.analysis = sanitize(analysis)


class PresentationSection:
    def __init__(self, statements=None, name="Presentation"):
        self.name = name
        self.statements = statements if statements else []


class QASection:
    def __init__(self, transitions=None, questions=None):
        self.transitions = transitions if transitions else []
        self.__questionsDict__ = questions if questions else {}
        self.questions = questions.values()

    def get_question(self, question_id):
        return self.__questionsDict__[question_id]

class Transition:
    def __init__(self, speaker, text):
        self.speaker = speaker
        self.text = sanitize(text)

class Question:
    def __init__(self, id, speaker, text, topic="", sentiment="", analysis=""):
        self.id = id
        self.speaker = speaker
        self.text = sanitize(text)
        self.topic = sanitize(topic)
        self.sentiment = sanitize(sentiment)
        self.analysis = sanitize(analysis)
        self.followup_questions = {} # A dictionary store id-question pair: {followup_question_id: followup_question}
        self.answers = [] # A list of Answers

    def addfollowup(self, id, question):
        self.followup_questions[id] = question

    def getfollowup(self, id):
        return self.followup_questions[id]

    def addAnswer(self, answer):
        self.answers.append(answer)

class Answer:
    def __init__(self, id, question, speaker, text, topic="", sentiment="", analysis=""):
        self.id = id
        self.question=question
        self.speaker = speaker
        self.text = sanitize(text)
        self.topic = sanitize(topic)
        self.sentiment = sanitize(sentiment)
        self.analysis = sanitize(analysis)

def sanitize(text):
    return text.replace('"', '').replace('{', '').replace('}', '') if text else ""