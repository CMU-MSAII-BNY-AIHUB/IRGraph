from summarization import Summarizer

def test_summarize():
    summarizer = Summarizer()

    # Test case 1: Summarize a question
    question = "Very good. And then as a follow-up. You've talked a little bit about your reserves at the Fed. I think on your balance sheet, your total deposits at banks, all central banks is around $54 billion. if that's the right number? Can you tell me what's the more normal number once we get into maybe a more normal environment at some point in the future? Are you -- what would be a lower number that you'd be comfortable with?"
    summary = summarizer.summarize(question, "question")
    assert isinstance(summary, str), "Summary should be a string"
    assert len(summary) > 0, "Summary should not be empty"

    # Test case 2: Summarize an answer
    answer = "Well, I'm not sure it's lower. It's interestingly -- we talk a lot about this, what is -- if we layer in the overall deposits, on average deposits are -- forget about just what's at the Fed. But just in general, what's driving the asset level is the liability side. And if we're at $125 billion, $130 billion, how much -- is that a post-pandemic normal? And it's just too hard to tell. And I think there's -- clients are, right now, they've held on to liquidity longer than what we would have anticipated and that 35 -- the USD 15 billion, the other $20 billion-ish that's in -- $20 billion, $30 billion, it's in other currencies at other central banks, it's all driven by the deposit base. And it's held in there pretty flat for a while now in that kind of $120 billion, $130 billion level."
    summary = summarizer.summarize(answer, "answer")
    assert isinstance(summary, str), "Summary should be a string"
    assert len(summary) > 0, "Summary should not be empty"

    print("All tests passed!")

test_summarize()
