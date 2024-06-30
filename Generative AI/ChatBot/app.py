from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import Ollama
import streamlit as st 
import os
from dotenv import load_dotenv

load_dotenv()
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_API_KEY']=os.getenv('LANGCHAIN_API_KEY')

#PROMPT Template
prompt = ChatPromptTemplate.from_messages(
    [('system','You are a helpful assistant. please response to the user queries'),
     ('user','Question: {question}')
     ]
)

# streamlit framwork

st.markdown('<h1 style="color:blue;">ChatBot</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="color:violet;">Interactive AI Chat with Langchain and LLAMA2</h2>', unsafe_allow_html=True)

input_text = st.text_input('Search the topic you want')

#openAI Ollama
llm = Ollama(model='llama2')
output_parser = StrOutputParser()
chain=prompt|llm|output_parser

if input_text:
    st.write(chain.invoke({'question': input_text}))