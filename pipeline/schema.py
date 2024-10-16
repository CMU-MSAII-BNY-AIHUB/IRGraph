class Transcript:
    def __init__(self, header, participants_section, presentation_section, qa_section):
        self.header = header
        self.participants_section = participants_section
        self.presentation_section = presentation_section
        self.qa_section = qa_section

class Header:
    def __init__(self, company, time, quarter, currency, note, open_price, close_price, high_price, low_price, performance, year, kbw_open,kbw_close):
        self.company = sanitize(company)
        self.time = sanitize(time)
        self.quarter = sanitize(quarter)
        self.currency = currency
        self.note = sanitize(note)
        self.open_price = open_price
        self.close_price = close_price
        self.high_price = high_price
        self.low_price = low_price
        self.performance = performance
        self.year = year
        self.kbw_open =kbw_open
        self.kbw_close =kbw_close
        





class ParticipantsSection:
    def __init__(self, participants=None, name="call participants"):
        self.name = sanitize(name)
        self.__participantsDict__ = participants
        self.participants = participants.values()

    def get_participant(self, participants_id):
        return self.__participantsDict__[participants_id]


class Person:
    def __init__(self, id, company="", name="", position="", group=""):
        self.company = sanitize(company)
        self.id = id
        self.name = sanitize(name)
        self.position = sanitize(position)
        self.group = sanitize(group)

    def __repr__(self):
        return self.name + ' ' + self.position

class Statement: # Content in the schema
    def __init__(self, speaker:Person, text, topic="", sentiment="", analysis="", summary="",timeStamp = "", stockPrice="",kbw = ""):
        self.speaker = speaker
        self.text = sanitize(text)
        self.topic = sanitize(topic)
        self.sentiment = sanitize(sentiment)
        self.analysis = sanitize(analysis)
        self.summary = sanitize(summary)
        self.timeStamp = sanitize(timeStamp)
        self.stockPrice = sanitize(stockPrice)
        # self.SP500 = SP500
        self.kbw =kbw


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
    def __init__(self, id, speaker, text, topic="", sentiment="", emotion="",summary="", timeStamp = "", stockPrice="", kbw = ""):
        self.id = id
        self.speaker = speaker
        self.text = sanitize(text)
        self.topic = sanitize(topic)
        self.sentiment = sanitize(sentiment)
        # self.analysis = sanitize(analysis)
        self.emotion = sanitize(emotion)
        self.summary = sanitize(summary)
        self.followup_questions = {} # A dictionary store id-question pair: {followup_question_id: followup_question}
        self.answers = [] # A list of Answers
        self.timeStamp = sanitize(timeStamp)
        self.stockPrice = sanitize(stockPrice)
        # self.SP500 = SP500
        self.kbw =kbw
 
        

    def addfollowup(self, id, question):
        self.followup_questions[id] = question

    def getfollowup(self, id):
        return self.followup_questions[id]

    def addAnswer(self, answer):
        self.answers.append(answer)

class Answer:
    def __init__(self, id, question, speaker, text, topic="", sentiment="", emotion="", summary=""):
        self.id = id
        self.question=question
        self.speaker = speaker
        self.text = sanitize(text)
        self.topic = sanitize(topic)
        self.sentiment = sanitize(sentiment)
        # self.analysis = sanitize(analysis)
        self.emotion = sanitize(emotion)
        self.summary = sanitize(summary)


        

def sanitize(text):
    return text.replace('"', '').replace('{', '').replace('}', '') if text else ""