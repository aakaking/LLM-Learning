from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from voice import talk, convert_to_text
import gradio as gr
from IPython.display import Audio, display
from nv_api_key import get_nv_api_key

nvapi_key = get_nv_api_key()

def rag_model(question):
    # Load the vectorestore back.
    embedder = NVIDIAEmbeddings(model="NV-Embed-QA")
    store = FAISS.load_local("./zh_data/nv_embedding", embedder,allow_dangerous_deserialization=True)
    retriever = store.as_retriever()
    llm = ChatNVIDIA(model="meta/llama3-70b-instruct", nvidia_api_key=nvapi_key, max_tokens=512)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Answer solely based on the following context:\n<Documents>\n{context}\n</Documents>",
            ),
            ("user", "{question}"),
        ]
    )

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain.invoke(question)

def run_text_prompt(message, chat_history):
    bot_message = rag_model(message)
    edge_save_path=talk(bot_message)
    display(Audio(edge_save_path, autoplay=True))

    chat_history.append((message, bot_message))
    return edge_save_path, chat_history


def run_audio_prompt(audio, chat_history):
    if audio is None:
        return None, chat_history
    message_transcription = convert_to_text(audio)
    edge_save_path, chat_history = run_text_prompt(message_transcription, chat_history)
    return edge_save_path, chat_history

#@title Run gradio app
if __name__ == "__main__":
    # massage = "我赛车出了意外的急诊费用，我投保的平安补充门诊急诊团体医疗保险可以报销吗？"
    # bot_message = rag_model(massage)
    # print(bot_message)
    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(label="Chat with me")

        msg = gr.Textbox(label="Ask anything")
        msg.submit(run_text_prompt, [msg, chatbot], [msg, chatbot])
        with gr.Row():
            audio = gr.Audio(sources="microphone", type="filepath")

            send_audio_button = gr.Button("Send Audio", interactive=True)
            send_audio_button.click(run_audio_prompt, [audio, chatbot], [audio, chatbot])

    demo.launch(share=True,debug=True)
    
