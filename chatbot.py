from langchain_community.chat_message_histories import ChatMessageHistory #, ConversationBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field
from typing import List

from dotenv import load_dotenv
load_dotenv()

system_prompt = """You are a helpful assistant."""

# Initialize LLM
llm = ChatOpenAI(temperature=1, model="gpt-4.1-nano") # gpt-4o-mini , gpt-4.1-nano

# Create prompt template
prompt = ChatPromptTemplate.from_messages([("system", system_prompt),
                                           MessagesPlaceholder(variable_name="chat_history"),
                                           ("human", "{input}"),
                                           ])

# Initialize memory
# memory = ChatMessageHistory()
class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    '''In memory implementation of chat message history.'''

    messages: List[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: List[BaseMessage]) -> None:
        '''Add a list of messages to the stor'''
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []
store = {}
def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]

chain = prompt | llm | StrOutputParser()

chain_with_history = RunnableWithMessageHistory(
    chain,
    get_by_session_id,
    input_messages_key="input",
    history_messages_key="chat_history",
)

def chitchat(input_text, session_id):
    res = chain_with_history.invoke({"input":input_text, "session_id": session_id}, config={"configurable": {"session_id": session_id}}) # ex0
    return res

if __name__ == "__main__":
    print(chain_with_history.invoke({"input": "Hello!"}, config={"configurable": {"session_id": "testo"}}))