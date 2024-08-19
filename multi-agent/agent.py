
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda
from langchain.schema.runnable.passthrough import RunnableAssign
from langchain_core.runnables import RunnableBranch
from utils import image2b64, extract_python_code, save_table_to_global, print_and_return, execute_and_return
from nv_api_key import get_nv_api_key

#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
get_nv_api_key()

global img_path
img_path = '/Users/zhangnan/Code/LLM-Learning/multi-agent/'+'image.png'

def execute_and_return(x):
    code = extract_python_code(x.content)[0]
    try:
        result = exec(str(code))
        #print("exec result: "+result)
    except Exception:
        print("The code is not executable, don't give up, try again!")
    return img_path

def chart_agent(image, user_input, table):

    image_b64 = image2b64(image)
    # Chart reading Runnable
    chart_reading = ChatNVIDIA(model="microsoft/phi-3-vision-128k-instruct")
    chart_reading_prompt = ChatPromptTemplate.from_template(
        'Generate underlying data table of the figure below, : <img src="data:image/png;base64,{image_b64}" />'
    )
    chart_chain = chart_reading_prompt | chart_reading

    # Instruct LLM Runnable
    # instruct_chat = ChatNVIDIA(model="nv-mistralai/mistral-nemo-12b-instruct")
    # instruct_chat = ChatNVIDIA(model="meta/llama-3.1-8b-instruct")
    #instruct_chat = ChatNVIDIA(model="ai-llama3-70b")
    instruct_chat = ChatNVIDIA(model="meta/llama-3.1-405b-instruct")

    instruct_prompt = ChatPromptTemplate.from_template(
        "Do NOT repeat my requirements already stated. Based on this table {table}, {input}" \
        "If has table string, start with 'TABLE', end with 'END_TABLE'." \
        "If has code, start with '```python' and end with '```'." \
        "Do NOT include table inside code, and vice versa."
    )
    instruct_chain = instruct_prompt | instruct_chat

    # 根据“表格”决定是否读取图表
    chart_reading_branch = RunnableBranch(
        (lambda x: x.get('table') is None, RunnableAssign({'table': chart_chain })),
        (lambda x: x.get('table') is not None, lambda x: x),
        lambda x: x
    )
    
    # 根据需求更新table
    update_table = RunnableBranch(
        (lambda x: 'TABLE' in x.content, save_table_to_global),
        lambda x: x
    )

    execute_code = RunnableBranch(
        (lambda x: '```python' in x.content, execute_and_return),
        lambda x: x
    )
    
    # 执行绘制图表的代码
    chain = (
        chart_reading_branch
        #| RunnableLambda(print_and_return)
        | instruct_chain
        #| RunnableLambda(print_and_return)
        | update_table
        | execute_code
    )

    return chain.invoke({"image_b64": image_b64, "input": user_input, "table": table})

if __name__ == "__main__":
    table = None
    image = "economic-assistance-chart.png"
    # user_input = "replace table string's 'UK' with 'United Kingdom'"
    # chart_agent(image, user_input, table)
    # print(table)
    user_input = "draw this table as stacked bar chart in python"
    result = chart_agent(image, user_input, table)
    print(result)