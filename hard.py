"""
Inside conditions.json, you will see a subset of UNSW courses mapped to their 
corresponding text conditions. We have slightly modified the text conditions
to make them simpler compared to their original versions.

Your task is to complete the is_unlocked function which helps students determine 
if their course can be taken or not. 

We will run our hidden tests on your submission and look at your success rate.
We will only test for courses inside conditions.json. We will also look over the 
code by eye.

NOTE: This challenge is EXTREMELY hard and we are not expecting anyone to pass all
our tests. In fact, we are not expecting many people to even attempt this.
For complete transparency, this is worth more than the easy challenge. 
A good solution is favourable but does not guarantee a spot in Projects because
we will also consider many other criteria.
"""
import json

# NOTE: DO NOT EDIT conditions.json
with open("./conditions.json") as f:
    CONDITIONS = json.load(f)
    f.close()


def remove_whitespace(sentence):
  """Given a string, remove the excess whitespaces 
  (including double spaces, and leading and trailing spaces)
    """
  return " ".join(sentence.split())

def clean_sentence(condition):

  """Given a string representing the prequisite of a course,
    Standarise the string for easier manipulation in later processes 
    """

  # remove excess whitespaces
  res = remove_whitespace(condition)

  # change to lowercase
  res = res.lower()

  # remove the "prerequisite" word
  res = res.replace('prerequisite: ', '')
  res = res.replace('pre-requisite: ', '')
  res = res.replace('pre-req: ', '')
  res = res.replace('prequisite: ', '')

  # remove the "completion of"
  res = res.replace('completion of ', '')

  # remove the "."
  res = res.replace('.', '')

  # change the paranthesis in "credit in (" to "{" to easily distinguish paranthesis used in the expression
  for i in range(len(res)):
    if (res[i] == '('):
      # find the word "in"
      if ((i-3) >= 0 and res[i-3]=='i' and (i-2) >= 0 and res[i-2]=='n'):
        res = res[:i] + '{' + res[i + 1:]
        # find the closing parenthesis and change it to "}"
        j = i+1
        while (res[j] != ')'):
          j += 1
        res = res[:j] + '}' + res[j + 1:]

  return res


def is_course_taken(courses_list, req_course, target_course):
  """
  Given a list of taken courses, a of the courses in the requirement, and the target course.
  Determine if the course in the requirement is already taken
  """

  course_name = req_course.lower()

  if ((len(course_name) == 4 and course_name.isdigit()) or len(course_name) == 8):
    for i in range(len(courses_list)):
      # if only 4 digits, check if the required course and the target course are in the same subject area
      if (len(course_name) == 4 and (course_name.lower() in courses_list[i].lower()) and (courses_list[i].lower()[0:4] == target_course.lower()[0:4])):
        return True
      # complete course code
      elif (len(course_name) == 8 and (course_name.lower() == courses_list[i].lower())):
        return True
  
  return False

def is_credit_reached(courses_list, condition, target_course):

  """
  Given a list of taken courses, a string of course condition in format of "x units of credit...", and the target course.
  Check if the number of credits taken on specific courses is enough to fulfill the requirement
  """
  # find out how many credits needed
  idx = 0
  num_credit = 0
  reached_credits = 0
  while(condition[idx].isdigit()):
    num_credit = (num_credit * 10) + int(condition[idx])
    idx += 1

  # n units of credits in level x xxxx courses
  if ('level' in condition):
    # find out which level required
    lvl_idx = condition.find('level') + 6
    course_lvl = 0
    while(condition[lvl_idx].isdigit()):
      course_lvl = (course_lvl * 10) + int(condition[lvl_idx])
      lvl_idx += 1

    # find out which subject area required
    subject_area_idx = lvl_idx + 1
    subject_area = condition[subject_area_idx : subject_area_idx+4]

    # calculate how many credits reached
    reached_credits = 0
    for course in courses_list:
      if (course[0:4].lower() == subject_area.lower() and int(course[4]) == course_lvl):
        reached_credits += 6

  # n units of credits in (..., ...) 
  elif ('{' in condition and '}' in condition):

    # find out the list of courses that should be taken
    req_courses_str = condition[condition.find('{')+1 : condition.find('}')]
    req_courses_list = req_courses_str.split(', ')

    # calculate how many credits reached
    reached_credits = 0
    for req_course in req_courses_list:
      if(is_course_taken(courses_list, req_course, target_course)):
        reached_credits += 6
  
  # n units of credits
  else:
    reached_credits = len(courses_list) * 6

  # check if enough credits is reached
  if (reached_credits >= num_credit):
    return True
  else:
    return False


def to_tokens(course_list, target_course, condition):

  """
  Given a list of taken courses, a string of course condition, and the target course.
  Return a list of tokens representing a boolean expression. 
  For example, if the condition is "COMP1927 or COMP2521" and course_list = ['COMP1927'], then [True, 'or', False] will be returned
  """

  course_condition = clean_sentence(condition)
  res = []

  left_idx = 0
  right_idx = 0

  # Split sentences by its operators. 
  # For example, "COMP1927 or COMP2521" will be converted into ['COMP1927', 'or', 'COMP2521']
  while(right_idx <= len(course_condition)):

    if (right_idx == len(course_condition)):
      res.append(remove_whitespace(course_condition[left_idx:right_idx]))
      break

    elif (course_condition[right_idx] == '(' or course_condition[right_idx] == ')'):
      res.append(remove_whitespace(course_condition[left_idx:right_idx]))
      res.append(remove_whitespace(course_condition[right_idx]))
      right_idx += 1
      left_idx = right_idx

    elif (course_condition[right_idx:right_idx+2] == 'or'):
      res.append(remove_whitespace(course_condition[left_idx:right_idx]))
      res.append(remove_whitespace(course_condition[right_idx:right_idx+2]))
      right_idx += 2
      left_idx = right_idx

    elif (course_condition[right_idx:right_idx+3] == 'and'):
      res.append(remove_whitespace(course_condition[left_idx:right_idx]))
      res.append(remove_whitespace(course_condition[right_idx:right_idx+3]))
      right_idx += 3
      left_idx = right_idx

    else:
      right_idx += 1

  # remove empty strings
  for val in res:
    if (len(val) == 0):
      res.remove(val)



  # Convert to tokens
  for i in range(len(res)):
    # if not operators
    if (not(res[i] == 'and' or res[i] == 'or' or res[i] == '(' or res[i] == ')')):
      if ('credit' in res[i]):
        if (is_credit_reached(course_list, res[i], target_course)):
          res[i] = True
        else:
          res[i] = False
      else:
        if (is_course_taken(course_list, res[i], target_course)):
          res[i] = True
        else:
          res[i] = False

  # if no prerequisite, then assume the expression is always true 
  if (len(res) == 0):
    res.append(True)

  return res



def is_unlocked(courses_list, target_course):
    """Given a list of course codes a student has taken, return true if the target_course 
    can be unlocked by them.
    
    You do not have to do any error checking on the inputs and can assume that
    the target_course always exists inside conditions.json

    You can assume all courses are worth 6 units of credit
    """
    
    # get the list of tokens representing a boolean expression
    tokens = to_tokens(courses_list, target_course, CONDITIONS[target_course])

    # Evaluate the expression
    val_stack = []    # to store values
    op_stack = []     # to store operators

    # iterate through the tokens
    for token in tokens:
      # value goes to value stack
      if (type(token) is bool):
        val_stack.append(token)
      
      # store the operators
      elif (token == 'and' or token == 'or' or token == '('):
        op_stack.append(token)

      # if right parenthesis found, backtrack until the first left parenthesis and process the expression
      elif (token == ')'):
        while(op_stack[-1] != '('):
          
          # get two values and an operator, then process the operation
          curr_op = op_stack.pop()
          val1 = val_stack.pop()
          val2 = val_stack.pop()       
          new_val = False
          if (curr_op == 'and'):
            new_val = val1 and val2
          elif (curr_op == 'or'):
            new_val = val1 or val2
          
          # store the new value back to the stack
          val_stack.append(new_val)

        # pop the left parenthesis
        if (op_stack[-1] == '('):
          op_stack.pop()

    # all parenthesis should be processed at this point
    # process the rest of the expression
    while(len(op_stack) > 0):
      # get two values and an operator, then process the operation
      curr_op = op_stack.pop()
      val1 = val_stack.pop()
      val2 = val_stack.pop()
      new_val = False
      if (curr_op == 'and'):
        new_val = val1 and val2
      elif (curr_op == 'or'):
        new_val = val1 or val2
      
      # store the new value back to the stack
      val_stack.append(new_val)
    
    # if the expression is valid, the value stack should contain only the final result of the expression
    if (len(val_stack) == 1):
      return val_stack[0]
    else:
      return False





    