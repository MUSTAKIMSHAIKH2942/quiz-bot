
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses



def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    current_question = next((q for q in PYTHON_QUESTION_LIST if q['id'] == current_question_id), None)
    
    if current_question:
        if current_question['type'] == 'multiple_choice':
            valid_choices = [choice['key'] for choice in current_question['choices']]
            if answer not in valid_choices:
                return False, "Invalid choice. Please select a valid option."
        elif current_question['type'] == 'open-ended':
            if not answer.strip():
                return False, "Your answer cannot be empty."
        else:
            return False, "Unsupported question type."
        
        session['user_answers'][current_question_id] = answer
        return True, ""
    else:
        return False, "Question not found."



def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    current_question_index = next((index for index, q in enumerate(PYTHON_QUESTION_LIST) if q['id'] == current_question_id), -1)
    
    if current_question_index != -1 and current_question_index < len(PYTHON_QUESTION_LIST) - 1:
        next_question = PYTHON_QUESTION_LIST[current_question_index + 1]
        next_question_id = next_question['id']
        return next_question, next_question_id
    else:
        return None, None  


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    user_answers = session.get('user_answers', {})
    
    total_questions = len(PYTHON_QUESTION_LIST)
    correct_answers = 0
    
    for question in PYTHON_QUESTION_LIST:
        question_id = question['id']
        correct_answer = question['answer']
        user_answer = user_answers.get(question_id)
        
        if user_answer == correct_answer:
            correct_answers += 1
    
    score = (correct_answers / total_questions) * 100
    
    final_response = f"You have completed the quiz.\nTotal Questions: {total_questions}\nCorrect Answers: {correct_answers}\nScore: {score}%"
    
    return final_response

