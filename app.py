from flask import Flask, request, render_template
import translators as ts
import os
import openai
from flask import jsonify
import json

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

USER_LANGUAGE=""
USER_LEVEL=""
USER_TOPIC=""
USER_LENGTH=0
PREVIOUS=""


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
    elif language=="German": 
        code='de'
    elif language =="French":
        code='fr'
    elif language =="Italian":
        code='it'
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

    if level==0: 
        instruction = f"Generate a very easy and interesting news article in {language} on {topic} for a non native speaker with length of {length} words. Do not give an intro. Do not simply give an encyclopedic description. Someone who has only studied the language for a few months should be able to read this article"
    elif level==7: 
        instruction = f"Generate a difficult, sophisticated, and interesting news article in {language} on {topic} for a non native speaker with length of {length} words. Do not give an intro. Do not simply give an encyclopedic description."
    else: 
        global USER_LANGUAGE
        global USER_LEVEL
        global USER_TOPIC
        global USER_LENGTH

        # start by storing user input
        USER_LANGUAGE=language
        USER_LEVEL=level
        USER_TOPIC=topic
        USER_LENGTH=length

        dict={"HSK1/A1":1,"HSK2/A2":2, "HSK3/B1":3, "HSK4/B2":4, "HSK5/C1":5, "HSK6/C2":6}
        euro_dict={1:"A1", 2:"A2", 3:"B1", 4:"B2", 5:"C1", 6:"C2"}
        if language == "Simplified Chinese":
            input_level=f"HSK level {dict[level]}"
        else:
            num=dict[level]
            input_level=f"{euro_dict[num]}"
        # build the messages
        instruction = f"Generate an interesting news article in {language} on {topic} for a non native speaker with level {input_level} with length of {length} words. Do not give an intro. Do not simply give an encyclopedic description."
        print(instruction)
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

def get_key(val, dict):
    for key, value in dict.items():
        if val == value:
            return key

def redo(option): 
    global USER_LEVEL

    dict={"HSK1/A1":1,"HSK2/A2":2, "HSK3/B1":3, "HSK4/B2":4, "HSK5/C1":5, "HSK6/C2":6}
    level_num=dict[USER_LEVEL]
    # level_str=get_key(level_num,dict)
    if option == "too easy": 
        level_num+=1
        if level_num==7: 
            result=get_response(PREVIOUS, USER_LANGUAGE, level_num, USER_TOPIC, USER_LENGTH)
            return result
    elif option == "too hard": 
        level_num-=1
        if level_num==0: 
            result=get_response(PREVIOUS, USER_LANGUAGE, level_num, USER_TOPIC, USER_LENGTH)
            return result
    else: 
        return None 
    new_level=get_key(level_num,dict)
    USER_LEVEL=new_level
    result=get_response(PREVIOUS, USER_LANGUAGE, new_level, USER_TOPIC, USER_LENGTH)
    return result

def take_quiz():
    prompt="""Generate a python dictionary containing a multiple choice quiz with at most 6 questions in the language of the following article and give the corresponding answer key. Make sure the quiz is in the language of the previous article. The multiple choice quiz should function like a reading comprehension quiz and should quiz the user on their comprehension of the article. Make sure that all questions can be answered solely based on the content from the previous article. Users should not be quizzed on things not mentioned in the previous article. 
            Format the response in the format of a python dictionary where the key is a string containing the question along with the choices and the value is a string containing the answer. Format it like the following: 
            quiz = {"1. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”,“2. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”,“3. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”,“4. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”,“5. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”,“6. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”,“7. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”,“8. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”,“9. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”,“10. Question \nA. optionA \nB. optionB\nC. optionC\nD. optionD\n”: “answer”}"""

    messages = [
        { "role": "system", "content": prompt },
    ]
    for question, answer in PREVIOUS[-MAX_CONTEXT_QUESTIONS:]:
        messages.append({ "role": "assistant", "content": answer })
 
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    str_dict=completion.choices[0].message.content

    messages = [
        { "role": "system", "content": f"convert this to json format {str_dict}" },
    ]
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        top_p=1,
        frequency_penalty=FREQUENCY_PENALTY,
        presence_penalty=PRESENCE_PENALTY,
    )
    json_dict=completion.choices[0].message.content
    dict = json.loads(json_dict)
    return dict

@app.route('/redo_article', methods=['POST'])
def redo_article():
    option = request.form['option']
    new_article_content = redo(option)
    return jsonify({"new_article_content": new_article_content})

@app.route('/result', methods=['POST'])
def result():
    generated_article_content = request.form['generated_article_content']
    return render_template('result.html', generated_article_content=generated_article_content)

@app.route('/generate_article', methods=['POST'])
def generate_article():
    language = request.form['languageSelect']
    difficulty = request.form['difficultySelect']
    topic = request.form['topicInput']
    length = request.form['lengthInput']

    # Perform your processing with the data, e.g., call GPT model API
    # and generate the article based on the user inputs
    generated_article_content = get_response([], language, difficulty, topic, length)
    print(generated_article_content)

    # Return the generated article content as JSON
    return jsonify({"generated_article_content": generated_article_content})