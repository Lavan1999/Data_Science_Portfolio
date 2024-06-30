![Screenshot (347)](https://github.com/Lavan1999/Data_Science_Portfolio/assets/152668558/d68fba7e-88b5-4b66-b686-3db1e22be69b)

# ChatBot Application with Langchain and LLAMA2
## Overview
This ChatBot application leverages the power of Langchain and the LLAMA2 model to provide interactive AI chat capabilities. The application is built using Streamlit for the frontend interface.

# Workflow
- 1. Environment Setup
Load environment variables using the dotenv package.
Set environment variables required for Langchain tracing and API key from the .env file.
- 2. Create Chat Prompt Template
Define a chat prompt template using ChatPromptTemplate from langchain_core.prompts.
The template includes a system message stating the assistant's role and a user message that takes the user's question as input.
- 3. Streamlit Interface
Set up a simple user interface using Streamlit.
Create headers for the chatbot application.
Provide a text input box for users to enter their queries.
- 4. Initialize the LLM (Language Learning Model)
Use the Ollama class from langchain_community.llms to specify the LLAMA2 model.
Define an output parser using StrOutputParser.
- 5. Chain Components Together
Chain the prompt, LLM, and output parser together to create the chatbot response mechanism.
- 6. Handle User Input
Capture the user's query from the text input box.
If a query is provided, process it through the chained components to generate and display the response.
- 7. Display Output
Show the chatbot's response on the Streamlit interface.
# Usage
Clone the repository and navigate to the project directory.
Ensure you have Python and necessary packages installed.
Create a .env file with the required environment variables.
Run the Streamlit application using the command:
streamlit run app.py
Interact with the chatbot by entering queries in the text input box.
# Conclusion
This workflow outlines the steps for setting up and running a chatbot application using Langchain and LLAMA2. The combination of Langchain's flexible prompt handling and LLAMA2's powerful language model capabilities makes for a robust interactive AI chat experience.
