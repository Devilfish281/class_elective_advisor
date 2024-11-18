# ai_integration/ai_module.py
import json
import logging
import os
import re
import sys

from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)  # Reuse the global logger

# Initialize global variables
model = None
prompt_template = None


# TODO: sFunction to parse the content into a structured format using regex
def extract_starred_lines(input_text):
    """
    Extracts lines that contain an asterisk (*) from the input text.
    For lines starting with "**Prerequisites:**", removes all text between "**Prerequisites:**" and the first colon ":".

    Args:
        input_text (str): The multiline string to process.

    Returns:
        list: A list of lines containing at least one asterisk, with modified prerequisites lines.
    """
    # Split the input text into individual lines
    lines = input_text.split("\n")

    starred_lines = []
    for line in lines:
        stripped_line = line.strip()
        if "*" in stripped_line:
            # Check if the line starts with "**Prerequisites:**"
            if stripped_line.startswith("**Prerequisites:**"):
                # Use regex to remove text between "**Prerequisites:**" and the first colon ":"
                # This will transform "**Prerequisites:** Need to take: CPSC 335, MATH 338" to "**Prerequisites:** CPSC 335, MATH 338"
                modified_line = re.sub(
                    r"(\*\*Prerequisites:\*\*)[^:]*:\s*", r"\1 ", stripped_line
                )
                starred_lines.append(modified_line)
            else:
                starred_lines.append(stripped_line)

    return starred_lines


def parse_course_data(starred_lines):
    """
    Parses the array of starred lines and converts them into a list of dictionaries.

    Args:
        starred_lines (list): A list of lines containing course details.

    Returns:
        list: A list of dictionaries, each representing a course.
    """
    courses = []
    course = {}
    explanation_key = "**Explanation:**"
    prerequisites_key = "**Prerequisites:**"
    current_key = None
    explanation_lines = []

    for line in starred_lines:
        # Check if the line starts with a key pattern
        key_match = re.match(r"\*\*(.+?):\*\*\s*(.*)", line)
        if key_match:
            key, value = key_match.groups()
            key = key.strip()
            value = value.strip()

            if key == "Number":
                # If there's an existing course being parsed, add it to the list
                if course:
                    # If there's any accumulated explanation lines, join them
                    if explanation_lines:
                        course["Explanation"] = " ".join(explanation_lines).strip()
                        explanation_lines = []
                    courses.append(course)
                    course = {}
                course["Number"] = int(value)
                current_key = "Number"

            elif key == "Course Code":
                course["Course Code"] = value
                current_key = "Course Code"

            elif key == "Course Name":
                course["Course Name"] = value
                current_key = "Course Name"

            elif key == "Rating":
                try:
                    course["Rating"] = int(value)
                except ValueError:
                    course["Rating"] = value  # Keep as string if not an integer
                current_key = "Rating"

            elif key == "Explanation":
                explanation_lines = [value]
                current_key = "Explanation"

            elif key == "Prerequisites":
                course["Prerequisites"] = value
                current_key = "Prerequisites"

            else:
                # Handle any unexpected keys
                course[key] = value
                current_key = key

        else:
            # Handle multiline fields like Explanation
            if current_key == "Explanation":
                explanation_lines.append(line)
                course["Explanation"] = " ".join(explanation_lines).strip()

    # Add the last course after the loop ends
    if course:
        if explanation_lines:
            course["Explanation"] = " ".join(explanation_lines).strip()
        courses.append(course)

    return courses


def main_int_ai():
    """
    Initialize AI integration.

    This function prints messages indicating the start and completion of AI integration.
    """
    global model, prompt_template
    print("Initializing AI Integration...")
    try:
        # Create a ChatOpenAI model
        model = ChatOpenAI(model="gpt-4o")
    except Exception as e:
        logger.error(f"Error during Create a ChatOpenAI model: {e}")
        sys.exit(1)

    # Prompt with System and Human Messages (Using Tuples)
    print("\n----- Prompt with System and Human Messages (Tuple) -----\n")
    # Prompt with System and Human Messages (Using Tuples)
    # < career path> p_career_path
    # <START Electives> p_electives
    # < degree> p_degree
    messages = [
        (
            "system",
            """Role: College counselor
    Response length: detailed
    Explanation for each elective: Provide detailed explanations for each recommended elective course, ensuring that each explanation falls within a word count range of 100 to 200 words. These explanations should comprehensively address why the elective is beneficial.
    Response Style and Voice: detailed and academic style of the response should help the student understand the importance and relevance of each elective to their career of {p_career_path}.
    career path default: AI
    Prerequisite default: have not taken
    Response output:
    Line 1: Number 1,2,3,4,etc.
    Line 2: Course Code
    Line 3: Course Name
    Line 4: Rating
    Line 5: Explanation
    Line 6: Prerequisites, if all are blank, write "None

    Example of Response output:
    **Number:** 1
    **Course Code:** CPSC 483
    **Course Name:** Introduction to Machine Learning
    **Rating:** 100
    **Explanation:** Machine Learning is a cornerstone of AI development...add the reat of the explanation here
    **Prerequisites:** CPSC 335, MATH 338 


    I am a at CSU Fullerton college student what electives should I take to be best prepared for a degree in {p_degree} and specialize in {p_career_path} related fields. I need to take 5 electives, give me 10 to choose from.
    Rate each elective from 1 to 100, with 100 being the best.
    Sort the above by Rating, best which is 100 to worst which is 1.
    Explain why the elective is good for an  {p_career_path} education in great detail: Minium 100 words to max 200 words. ensure that responses adhere to the specified word count range of 100 to 200 words for each explanation
    If the user did not enter any Electives, then all Prerequisite Need to take. Do not assume that foundational courses are completed
    For each Prerequisite show “Need to take:” or “Completed:” base on the user input of class completed. Example: Completed CPSC 131, MATH 270B, etc.
    These suggestions not only consider the student's academic history and preferences but also the potential career paths they might be interested in, such as web development, AI engineering, machine learning, or game development.
    The system aims to streamline the decision-making process, ensuring students make informed choices that will benefit their future career trajectories.
    """,
        ),
        (
            "human",
            "Here are the electives I has to choose from in the format of: 'Prerequisite1,Prerequisite2,Prerequisite3,Course,Units,Name,Description' {p_electives} .",
        ),
    ]

    prompt_template = ChatPromptTemplate.from_messages(messages)

    print("AI Integration Initialized.")


# ui/gui.py


def format_elective_string(prerequisites, units, name, description):
    """
    Formats the elective string with placeholders for prerequisites.

    Parameters:
        prerequisites (str): Comma-separated prerequisites.
        units (int): Number of units.
        name (str): Course name.
        description (str): Course description.

    Returns:
        str: Formatted elective string.
    """

    """
        Handling 'None' or Empty Prerequisites:

        If prerequisites are 'none' or empty, format as 'None,,' to serve as placeholders for Prerequisite2 and Prerequisite3.
        Handling Fewer than Three Prerequisites:

        If there are fewer than three prerequisites, append empty strings to ensure the correct number of placeholders.
        Final Formatting:

        Concatenate prerequisites, units, name, and description separated by commas.
    """

    if prerequisites.lower() == "none":
        prereq_formatted = "None,,"
    else:
        prereq_list = [p.strip() for p in prerequisites.split(",")]
        # Ensure exactly 3 prerequisites
        while len(prereq_list) < 3:
            prereq_list.append("")
        prereq_formatted = ",".join(prereq_list[:3])

    # Handle cases where prerequisites are less than 3
    if not prerequisites or prerequisites.lower() == "none":
        prereq_formatted = "None,,"
    else:
        prereq_list = [p.strip() for p in prerequisites.split(",") if p.strip()]
        # Ensure exactly 3 prerequisites by adding empty strings
        while len(prereq_list) < 3:
            prereq_list.append("")
        prereq_formatted = ",".join(prereq_list[:3])

    # Final formatted string
    formatted = f"{prereq_formatted},{units},{name},{description}"
    return formatted


# What electives should I take to be a AI Software Applications Developer ?
# What electives should I take to be a Web Developer ?
# What electives should I take to be a game Developer ?


def get_recommendations_ai(job_id, job_name, degree_name, degree_electives):
    """
    Generate recommendations based on job and degree information using a ChatOpenAI model.

    :param job_id: int, The ID of the job associated with the recommendations.
    :param job_name: str, The name of the job associated with the recommendations.
    :param degree_name: str, The name of the degree for which recommendations are generated.
    :param degree_electives: list of dict, The elective courses relevant to the degree.
    :return: str, The JSON-formatted string of course recommendations.
    :raises SystemExit: If an error occurs during model invocation or file operations.
    """
    global model, prompt_template

    logger.info("AI_ENABLED=True: Invoking AI model for recommendations.")
    logger.debug(f"Job ID: {job_id}, Job Name: {job_name}, Degree Name: {degree_name}")

    # Retrieve AI_ENABLED environment variable
    ai_enabled = os.getenv("AI_ENABLED", "False").lower() == "true"
    if ai_enabled:
        try:
            logger.info("AI_ENABLED=True: Invoking AI model for recommendations.")
            logger.debug(
                f"Job ID: {job_id}, Job Name: {job_name}, Degree Name: {degree_name}"
            )

            # Prepare the prompt with the provided parameters
            # Convert degree_electives to a formatted string
            # format of: 'Prerequisite1,Prerequisite2,Prerequisite3,Course,Units,Name,Description'
            # Format electives_str as 'Prerequisite1,Prerequisite2,Prerequisite3,Units,Name,Description'
            electives_str = "\n".join(
                [
                    format_elective_string(
                        e["prerequisites"], e["units"], e["name"], e["description"]
                    )
                    for e in degree_electives
                ]
            )
            logger.debug(f"Formatted electives_str:\n{electives_str}")

            prompt = prompt_template.invoke(
                {
                    "p_career_path": job_name,
                    "p_degree": degree_name,
                    "p_electives": electives_str,
                }
            )

            #         """
            # CPSC 335,MATH 338,,CPSC 483,3,Introduction to Machine Learning,"Design, implement and analyze machine learning algorithms, including supervised learning and unsupervised learning algorithms. Methods to address uncertainty. Projects with real-world data."
            # CPSC 131,MATH 338,,CPSC 375,3,Introduction to Data Science and Big Data ,"Techniques for data preparation, exploratory analysis, statistical modeling, machine learning and visualization. Methods for analyzing different types of data, such as natural language and time-series, from emerging applications, including Internet-of-Things. Big data platforms. Projects with real-world data."
            # CPSC 131,,,CPSC 485,3,Computational Bioinformatics,"Algorithmic approaches to biological problems. Specific topics include motif finding, genome rearrangement, DNA sequence comparison, sequence alignment, DNA sequencing, repeat finding and gene expression analysis."
            # MATH 270B,CPSC 131,,CPSC 452,3,Cryptography,"Introduction to cryptography and steganography. Encryption, cryptographic hashing, certificates, and signatures. Classical, symmetric-key, and public-key ciphers. Block modes of operation. Cryptanalysis including exhaustive search, man-in-the-middle, and birthday attacks. Programing projects involving implementation of cryptographic systems."
            # CPSC 351, CPSC 353,,CPSC 454,3,Cloud Computing and Security,"Cloud computing and cloud security, distributed computing, computer clusters, grid computing, virtual machines and virtualization, cloud computing platforms and deployment models, cloud programming and software environments, vulnerabilities and risks of cloud computing, cloud infrastructure protection, data privacy and protection."
            # CPSC 351 or CPSC 353,,,CPSC 455,3,Web Security,"Concepts of web application security. Web security mechanisms, including authentication, access control and protecting sensitive data. Common vulnerabilities, including code and SQL attacks, cross-site scripting and cross-site request forgery. Implement hands-on web application security mechanisms and security testing."
            # CPSC 351,,,CPSC 474,3,Parallel and Distributed Computing,"Concepts of distributed computing; distributed memory and shared memory architectures; parallel programming techniques; inter-process communication and synchronization; programming for parallel architectures such as multi-core and GPU platforms; project involving distributed application development."
            # CPSC 351,,,CPSC 479,3,Introduction to High Performance Computing,"Introduction to the concepts of high-performance computing and the paradigms of parallel programming in a high level programming language, design and implementation of parallel algorithms on distributed memory, machine learning techniques on large data sets, implementation of parallel algorithms."
            # CPSC 121 or MATH 320,MATH 270B or MATH 280,,CPSC 439,3,Theory of Computation,"Introduction to the theory of computation. Automata theory; finite state machines, context free grammars, and Turing machines; hierarchy of formal language classes. Computability theory and undecidable problems. Time complexity; P and NP-complete problems. Applications to software design and security."
            # MATH 250A ,,,MATH 335,3,Mathematical Probability,"Probability theory; discrete, continuous and multivariate probability distributions, independence, conditional probability distribution, expectation, moment generating functions, functions of random variables and the central limit theorem."
            # CPSC 131, MATH 150B, MATH 270B,CPSC 484,3,Principles of Computer Graphics,"Examine and analyze computer graphics, software structures, display processor organization, graphical input/output devices, display files. Algorithmic techniques for clipping, windowing, character generation and viewpoint transformation."
            # ,,,CPSC 499,3,Independent Study,"Special topic in computer science, selected in consultation with and completed under the supervision of instructor. May be repeated for a maximum of 9 units of Undergraduate credit and 6 units of Graduate credit. Requires approval by the Computer Science chair."
            # CPSC 351,CPSC 353 or CPSC 452,,CPSC 459,3,Blockchain Technologies,"Digital assets as a medium of exchange to secure financial transactions; decentralized and distributed ledgers that record verifiable transactions; smart contracts and Ethereum; Bitcoin mechanics and mining; the cryptocurrency ecosystem; blockchain mechanics and applications."
            # MATH 250B,MATH 320,CPSC 120 or CPSC 121,MATH 370,3,Mathematical Model Building,"Introduction to mathematical models in science and engineering: dimensional analysis, discrete and continuous dynamical systems, flow and diffusion models."
            # MATH 250B,MATH 320,CPSC 120 or CPSC 121,MATH 340,,Numerical Analysis,"Approximate numerical solutions of systems of linear and nonlinear equations, interpolation theory, numerical differentiation and integration, numerical solution of ordinary differential equations. Computer coding of numerical methods."
            # CPSC 351,,,CPSC 456,3,Network Security Fundamentals,"Learn about vulnerabilities of network protocols, attacks targeting confidentiality, integrity and availability of data transmitted across networks, and methods for diagnosing and closing security gaps through hands-on exercises."
            # CPSC 351,,,CPSC 458,3,Malware Analysis,"Introduction to principles and practices of malware analysis. Topics include static and dynamic code analysis, data decoding, analysis tools, debugging, shellcode analysis, reverse engineering of stealthy malware and written presentation of analysis results."
            # CPSC 332,,,CPSC 431,3,Database and Applications,"Database design and application development techniques for a real world system. System analysis, requirement specifications, conceptual modeling, logic design, physical design and web interface development. Develop projects using contemporary database management system and web-based application development platform."
            # CPSC 332,,,CPSC 449,3,Web Back-End Engineering,"Design and architecture of large-scale web applications. Techniques for scalability, session management and load balancing. Dependency injection, application tiers, message queues, web services and REST architecture. Caching and eventual consistency. Data models, partitioning and replication in relational and non-relational databases."
            # CPSC 240,,,CPSC 440,3,Computer System Architecture,"Computer performance, price/performance, instruction set design and examples. Processor design, pipelining, memory hierarchy design and input/output subsystems."
            # CPSC 131 ,,,CPSC 349 ,3, Web Front-End Engineering ,"Concepts and architecture of interactive web applications, including markup, stylesheets and behavior. Functional and object-oriented aspects of JavaScript. Model-view design patterns, templates and frameworks. Client-side technologies for asynchronous events, real-time interaction and access to back-end web services."
            # CPSC 131,,,CPSC 411,3,Mobile Device Application Programming,"Introduction to developing applications for mobile devices, including but not limited to runtime environments, development tools and debugging tools used in creating applications for mobile devices. Use emulators in lab. Students must provide their own mobile devices."
            # CPSC 362,,,CPSC 464,3,Software Architecture,"Basic principles and practices of software design and architecture. High-level design, software architecture, documenting software architecture, software and architecture evaluation, software product lines and some considerations beyond software architecture."
            # CPSC 362,,,CPSC 462,3,Software Design,"Concepts of software modeling, software process and some tools. Object-oriented analysis and design and Unified process. Some computer-aided software engineering (CASE) tools will be recommended to use for doing homework assignments."
            # CPSC 362,,,CPSC 463,3,Software Testing,"Software testing techniques, reporting problems effectively and planning testing projects. Students apply what they learned throughout the course to a sample application that is either commercially available or under development."
            # CPSC 362,,,CPSC 466,3,Software Process,"Practical guidance for improving the software development process. How to establish, maintain and improve software processes. Exposure to agile processes, ISO 12207 and CMMI."
            # CPSC 386,CPSC 484,,CPSC 486,3,Game Programming,"Survey of data structures and algorithms used for real-time rendering and computer game programming. Build upon existing mathematics and programming knowledge to create interactive graphics programs."
            # CPSC 486,,,CPSC 489,3,Game Development Project,"Individually or in teams, students design, plan and build a computer game."
            # CPSC 121,,,CPSC 386,3,Introduction to Game Design and Production,"Current and future technologies and market trends in game design and production. Game technologies, basic building tools for games and the process of game design, development and production."
            # ,,,CPSC 301,2,Programming Lab Practicum ,"Intensive programming covering concepts learned in lower-division courses. Procedural and object oriented design, documentation, arrays, classes, file input/output, recursion, pointers, dynamic variables, data and file structures."

            # """,
            #     }
            # )

            print("---Working---")
            result = model.invoke(prompt)
            print("---DONE---")

            logger.debug("---Raw AI Response---")
            logger.debug(result.content)

            # Print the raw content from the result to see its structure
            print("---Raw Result Content---")
            print(
                result.content
            )  # Add this line to check what the raw response looks like

            # Extract lines containing '*'
            starred_lines = extract_starred_lines(result.content)

            # Print the resulting array
            logger.debug("---Lines containing '*': Extracted---")
            for idx, line in enumerate(starred_lines, start=1):
                logger.debug(line)

            # Parse the raw data
            courses = parse_course_data(starred_lines)

            logger.debug("---Parsed Courses---")
            logger.debug(courses)

            # Convert the list of courses to JSON
            json_data = json.dumps(courses, indent=4)

            # Print the JSON data
            print("Print the JSON data:")
            print(json_data)

            # After converting to JSON
            with open("courses.json", "w", encoding="utf-8") as json_file:
                json_file.write(json_data)
                logger.info("AI recommendations written to courses.json")

            return json_data

        except Exception as e:
            logger.error(
                f"Error during Prompt with System and Human Messages (Tuple):OpenAI agent execution: {e}"
            )
            sys.exit(1)
    else:
        try:
            logger.info("AI_ENABLED=False: Loading recommendations from courses.json")

            # Load the existing courses.json file
            with open("courses.json", "r", encoding="utf-8") as json_file:
                courses = json.load(json_file)

            if not isinstance(courses, list):
                logger.error("Loaded courses.json is not a list.")
                raise ValueError("Loaded courses.json is not a list.")

            logger.info("Recommendations loaded successfully from courses.json")

            # Convert the list of courses to JSON string
            json_data = json.dumps(courses, indent=4)

            return json_data  # Return the JSON-formatted string

        except FileNotFoundError:
            logger.error("courses.json file not found and AI_ENABLED=False.")
            # Depending on your application's needs, you might want to handle this differently
            raise FileNotFoundError(
                "courses.json file not found. Please enable AI or generate recommendations first."
            )
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding courses.json: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading courses.json: {e}")
            raise
