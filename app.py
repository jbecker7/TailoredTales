from flask import Flask, request, render_template
import translators as ts
import os
import openai

app = Flask(__name__, static_url_path='/static')
if __name__ == '__main__':
    app.run(debug=False)

openai.api_key = ""

TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6
# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Your POST handling logic here
        pass
    return render_template("index.html")



@app.route('/entry', methods=['GET', 'POST'])

def entry():
    if request.method == 'POST':
        # Your POST handling logic here
        pass
    return render_template("entry.html")


def translator(text,language):
    if language=="Chinese": 
        code='zh'
    elif language=='Spanish':
        code='es'
    result=ts.translate_text(text, translator='google',from_language=code, to_language='en')
    return result

def get_response(previous_questions_and_answers, language, level, topic, length):
    """Get a response from ChatCompletion
    Args:
        instructions: The instructions for the chat bot - this determines how it will behave
        previous_questions_and_answers: Chat history
        new_question: The new question to ask the bot
    Returns:
        The response text
    """
    dict={"HSK1/A1":1,"HSK2/A2":2, "HSK3/B1":3, "HSK4/B2":4, "HSK5/C1":5, "HSK6/C2":6}
    euro_dict={1:"A1", 2:"A2", 3:"B1", 4:"B2", 5:"C1", 6:"C2"}
    if language == "Chinese":
        input_level=f"HSK level {dict[level]}"
    if language == "Spanish":
        num=dict[level]
        input_level=f"{euro_dict[num]}"
    # build the messages
    instruction = f"Generate an interesting {language} news article on {topic} for a non native speaker with level {input_level} with length of {length} words. Do not give an intro. Do not simply give an encyclopedic description."

    messages = [
        { "role": "system", "content": instruction },
    ]
    
    # add the previous questions and answers
    for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "user", "content": question })
        messages.append({ "role": "assistant", "content": answer })
    # add the new question
    # messages.append({ "role": "user", "content": new_question })

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    return completion.choices[0].message.content

