# This script shows how to programmatically create a quiz in the system.
# Before using this script, make sure you have created a course with at least one chapter in the system.
# The script will also ask for the user name and password of the user which should create the quiz. This user
# requires ADMIN ("lecturer") permissions within the course in which the quiz should be created.

from get_session_token import get_auth_token
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import json
import os

# ask the user if they want to interact with the local or the deployed instance of the system
use_local = None
while use_local is None:
    user_answer = input("Use deployed keycloak instance? (y/n): ")
    if user_answer == "y":
        use_local = False
    elif user_answer == "n":
        use_local = True
    else:
        print("Invalid input.")

# |-----------------------------------------------------------------------------------------------------------------
# | The following code fetches authorization data for the user by asking for username and password and then sending
# | a request to keycloak. This is not relevant for the quiz creation itself, but obviously an authorization token
# | is required to create a quiz. If you get theauth token by other means, you can also remove this part
# |-----------------------------------------------------------------------------------------------------------------

GATEWAY_URL = "http://127.0.0.1:8080/graphql" if use_local else "http://orange.informatik.uni-stuttgart.de/graphql"
KEYCLOAK_URL = "http://localhost:9009/realms/GITS/protocol/openid-connect/token" if use_local else "https://orange.informatik.uni-stuttgart.de/keycloak/"

# get auth token for the user which should create the quiz in the system
user_token = get_auth_token(use_local=use_local)

# create our graphql client to access the server with the relevant authorization header
transport = AIOHTTPTransport(url=GATEWAY_URL, headers={
    "authorization": user_token
})
client = Client(transport=transport, fetch_schema_from_transport=True)

# |-----------------------------------------------------------------------------------------------------------------
# | The following code fetches courses and chapters to the user of the script can interactively choose which course
# | and chapter the quiz should be created in. This is not relevant for the quiz creation itself, so if you already
# | know the ID of the chapter in which the quiz should be created, you can skip this part.
# |-----------------------------------------------------------------------------------------------------------------

# we query all the courses the user is a member of, and their chapters
query = gql(
    """
    query {
        currentUserInfo {
            courseMemberships {
                role
                course {
                    title
                    chapters {
                        elements {
                            id
                            title
                        }
                    }
                }
            }
        }
    }
    """)
courseRes = client.execute(query)

# Give the user a list of all courses to choose in which course the quiz should be created
# We only display courses where the user is an admin (otherwise they don't have permission to create quizzes)
courses = [membership["course"] for membership in courseRes["currentUserInfo"]["courseMemberships"] if membership["role"] == "ADMINISTRATOR"]
print("Choose the course in which you want the quiz to be created:")
for i, course in enumerate(courses):
    print(str(i) + ". " + course["title"])

# ask the user to enter the index of the course
courseIndex = -1
while courseIndex < 0 or courseIndex >= len(courses):
    try:
        courseIndex = int(input("Enter the number of the course: "))
    except ValueError:
        print("Invalid input.")

# Now ask the user which chapter to create the quiz in
chapters = courses[courseIndex]["chapters"]["elements"]
print("Choose the chapter in which you want the quiz to be created:")
for i, chapter in enumerate(chapters):
    print(str(i) + ". " + chapter["title"])

# ask the user to enter the index of the chapter
chapterIndex = -1
while chapterIndex < 0 or chapterIndex >= len(chapters):
    try:
        chapterIndex = int(input("Enter the number of the chapter: "))
    except ValueError:
        print("Invalid input.")

# THIS IS THE ALL-IMPORTANT UUID OF THE CHAPTER IN WHICH THE QUIZ WILL BE CREATED
chapterId = chapters[chapterIndex]["id"]

# |-----------------------------------------------------------------------------------------------------------------
# | The following code creates the quiz in the system. The quiz data is read from a JSON file.
# |-----------------------------------------------------------------------------------------------------------------

# Import the quiz data from the JSON file
quizJson = None
with open(os.path.join(os.path.dirname(__file__), "example_quiz.json"), "r", encoding="utf8") as f:
    quizJson = json.load(f)

# Now we can create the quiz assessment in the selected chapter
query = gql(
    """
    mutation($assessmentInput: CreateAssessmentInput!, $quizInput: CreateQuizInput!) {
        createQuizAssessment(assessmentInput: $assessmentInput, quizInput: $quizInput) {
            id
        }
    }
    """)
# get the assessment data from the JSON file
assessmentInput = quizJson["assessment"]
# set the chapter ID of the quiz to the ID of the chapter we selected above, so the quiz gets created within
# the selected chapter
assessmentInput["metadata"]["chapterId"] = chapterId
# execute the query and pass it the required arguments as defined in the query string
createQuizRes = client.execute(query, variable_values={
    "assessmentInput": assessmentInput,
    "quizInput": quizJson["quiz"]
})

# assessmentId of the quiz we created, we will need the id to identify the quiz when adding questions to
# it in further requests
assessmentId = createQuizRes["createQuizAssessment"]["id"]

# The quiz we have now created does not yet contain any questions. We can add questions to the quiz using the
# mutateQuiz() mutation and its sub-mutations. The following code adds the questions from the JSON file to the quiz.

for questionJson in quizJson["questions"]:
    if questionJson["type"] == "MULTIPLE_CHOICE":
        # query for creating a multiple choice question
        query = gql(
            """
            mutation($assessmentId: UUID!, $multipleChoiceQuestion: CreateMultipleChoiceQuestionInput!) {
                mutateQuiz(assessmentId: $assessmentId) {
                    addMultipleChoiceQuestion(input: $multipleChoiceQuestion) {
                        assessmentId
                    }
                }
            }
            """)
        # execute the query and pass it the required arguments as defined in the query string
        createQuestionRes = client.execute(query, variable_values={
            "assessmentId": assessmentId,
            "multipleChoiceQuestion": questionJson["questionData"]
        })
    elif questionJson["type"] == "ASSOCIATION":
        # query for creating an association question
        query = gql(
            """
            mutation($assessmentId: UUID!, $associationQuestion: CreateAssociationQuestionInput!) {
                mutateQuiz(assessmentId: $assessmentId) {
                    addAssociationQuestion(input: $associationQuestion) {
                        assessmentId
                    }
                }
            }
            """)
        # execute the query and pass it the required arguments as defined in the query string
        createQuestionRes = client.execute(query, variable_values={
            "assessmentId": assessmentId,
            "associationQuestion": questionJson["questionData"]
        })
    elif questionJson["type"] == "CLOZE":
        # query for creating a cloze question
        query = gql(
            """
            mutation($assessmentId: UUID!, $clozeQuestion: CreateClozeQuestionInput!) {
                mutateQuiz(assessmentId: $assessmentId) {
                    addClozeQuestion(input: $clozeQuestion) {
                        assessmentId
                    }
                }
            }
            """)
        # execute the query and pass it the required arguments as defined in the query string
        createQuestionRes = client.execute(query, variable_values={
            "assessmentId": assessmentId,
            "clozeQuestion": questionJson["questionData"]
        })
        
