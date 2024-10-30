# Smart Elective Advisor: AI-Driven Course Selection Tool for CS Students

## Overview

Smart Elective Advisor is a Python-based application designed to assist undergraduate Computer Science students at California State University, Fullerton, in selecting the most suitable elective courses. Leveraging OpenAI's ChatGPT API and the LangChain framework, our tool provides personalized course recommendations through an intuitive GUI developed with Tkinter. By analyzing individual preferences and the evolving tech landscape, the Smart Elective Advisor ensures that students make informed decisions that enhance their academic journey and future career prospects.

## Features

- **AI-Powered Recommendations:** Utilizes advanced AI to suggest courses tailored to individual preferences.
- **User-Friendly Interface:** Built with Tkinter for easy navigation and interaction.
- **Local Data Management:** Employs SQLite for efficient data storage and retrieval.
- **Comprehensive Documentation:** Maintained using Sphinx for easy reference and onboarding.

## Installation

### Prerequisites

- **Python 3.12.7**
- **Poetry:** For dependency management and virtual environment setup.

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/class_elective_advisor.git
   cd class_elective_advisor
   ```

2. **Install Dependencies:**

   ```bash
   poetry install
   ```

3. **Activate the Virtual Environment:**

   ```bash
   poetry shell
   ```

4. **Set Up Environment Variables:**

   Rename the `.env.example` file to `.env` and update the variables inside with your own values.

   Create a `.env` file in the root directory and add your OpenAI API key:

   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DATABASE_PATH=electives.db
   ```

5. **Initialize the Database:**

   ```bash
   python main.py
   ```

   The above command will set up the database and launch the GUI.

## Usage

Run the application using:

```bash
python main.py
```
