import logging
import os
import sys

from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)  # Reuse the global logger


def main_int_ai():
    """
    Initialize AI integration.

    This function prints messages indicating the start and completion of AI integration.
    """
    print("Initializing AI Integration...")
    print("AI Integration Initialized.")


def get_recommendations(user_preferences):
    """
    Generate recommendations based on user preferences using a ChatOpenAI model.

    :param user_preferences: str, User preferences provided as input to the AI model.
    :return: str, The content of the AI model's response.
    :raises SystemExit: If an error occurs during model creation or invocation.
    """
    prompt = f"what is:\n{user_preferences}"

    try:
        # Create a ChatOpenAI model
        model = ChatOpenAI(model="gpt-4o")
    except Exception as e:
        logger.error(f"Error during Create a ChatOpenAI model: {e}")
        sys.exit(1)

    try:
        # Invoke the model with a message
        print("****WORKING****:")
        result = model.invoke(prompt)
        print("****Full result****:")
        print(result)
        print("****Content only****:")
        print(result.content)

        return result.content

    except Exception as e:
        logger.error(f"Error during agent execution: {e}")
        sys.exit(1)
