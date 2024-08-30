import os
import google.generativeai as genai
from dotenv import load_dotenv


class Assistant :
    def __init__(self, name,generational_config={
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        }):
        load_dotenv()
        self.name = name
        gemini_api = os.getenv('GEMINI_API_KEY')
        print(gemini_api)
        genai.configure(api_key=gemini_api)
        # Create the model
        self.generation_config = generational_config

        self.model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=self.generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
        system_instruction="System Prompt: Music Artist Race Classification\n\nTask Overview:\nYou will be provided with a list of music artists. Based on the identity of each artist or the overall identity of the group, classify the race of the artist using one of the following classifications:\n\n    White\n    Black\n    Hispanic or Latino\n    Asian\n    Native American or Alaska Native\n    Native Hawaiian or Pacific Islander\n    Middle Eastern or North African\n    Multiracial\n Indian \n Other\n\nOutput Format:\nReturn the classification in a CSV format as follows:\n\nArtist Name, Race\nArtist Name, Race\n...\n\nInstructions:\n\n    Analyze the provided artist name to determine their race based on publicly available information.\n    Use only one of the predefined classifications listed above for each artist.\n    If an artist falls into multiple racial categories, use \"Multiracial.\"\n    If the race cannot be determined or does not fit into the provided categories, use \"Other.\"\n    Return the final list in the specified CSV format.",
        )

        self.chat_session = self.model.start_chat(
        history=[
        ]
        )

    def chat(self,message): 
        response = self.chat_session.send_message(message)
        return response.text


def main():
    assistant = Assistant("Gemini")
    print("Welcome to the Gemini AI Assistant")
    while True:
        user_input = input("You: ")
        if user_input == "exit":
            break
        response = assistant.chat(user_input)
        print("Gemini:", response)

if __name__ == '__main__':
    main()