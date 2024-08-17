
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
import os
from tqdm import tqdm
from pathlib import Path

import getpass
import os

if not os.environ.get("NVIDIA_API_KEY", "").startswith("nvapi-"):
    os.environ["NVIDIA_API_KEY"] = "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"

### initialize ai-embed-qa-4 model
embedder = NVIDIAEmbeddings(model="NV-Embed-QA")
# Here we read in the text data and prepare them into vectorstore
ps = os.listdir("./zh_data/")
data = []
sources = []
for p in ps:
    content = ""
    if p.endswith('.txt'):
        path2file="./zh_data/"+p
        with open(path2file,encoding="utf-8") as f:
            lines=f.readlines()
            for line in lines:
                content += line
            if len(content)>=1:
                data.append(content)
                sources.append(path2file)

documents=[d for d in data if d != '\n']

# Here we create a vector store from the documents and save it to disk.
text_splitter = CharacterTextSplitter(chunk_size=400, separator=" ")
docs = []
metadatas = []

for i, d in enumerate(documents):
    splits = text_splitter.split_text(d)     
    #print(len(splits))
    docs.extend(splits)     
    metadatas.extend([{"source": sources[i]}] * len(splits))

store = FAISS.from_texts(docs, embedder , metadatas=metadatas)
store.save_local('./zh_data/nv_embedding')