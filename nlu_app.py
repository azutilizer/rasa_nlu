import sys
import pathlib
import argparse

import pandas as pd
import streamlit as st

from common import (
    load_interpreter,
    create_altair_chart,
    create_displacy_chart,
    fetch_info_from_message,
    fetch_attention_feats,
    make_attention_charts,
)

parser = argparse.ArgumentParser(description="")
parser.add_argument("--model_folder", default="./models", help="Pass the model folder.")
parser.add_argument("--project_folder", default="./", help="The folder where you're running from.")
args = parser.parse_args()

model_folder = args.model_folder
sys.path.append(args.project_folder)


st.markdown("# Rasa NLU Model Playground")
st.markdown("You can select a model on the left to interact with.")

model_files = [str(p.parts[-1]) for p in pathlib.Path(model_folder).glob("*.tar.gz")]
model_file = st.sidebar.selectbox("What model do you want to use", model_files)

interpreter = load_interpreter(model_folder, model_file)

text_input = st.text_input("Text Input for Model", "Hello")

blob, nlu_dict, tokens = fetch_info_from_message(
    interpreter=interpreter, text_input=text_input
)

st.markdown("## Tokens and Entities")
st.write(
    create_displacy_chart(tokens=tokens, entities=blob["entities"]),
    unsafe_allow_html=True,
)

st.markdown("## Intents")

chart_data = pd.DataFrame(blob["intent_ranking"]).sort_values("name")
p = create_altair_chart(chart_data)
st.altair_chart(p.properties(width=600))

with st.beta_expander("Full Model Specification"):
    spec = {
        f"step_{i}": {"name": type(c).__name__, "settings": c.component_config}
        for i, c in enumerate(interpreter.interpreter.pipeline)
    }
    st.write(spec)

if "DIETClassifier" in [type(_).__name__ for _ in interpreter.interpreter.pipeline]:
    with st.beta_expander("View Diet Attention Charts."):
        st.markdown(
            "These charts are meant as an advanced debugging tool for our research team. They display information from the attention mechanism inside of DIET."
        )
        diag_data, tokens = fetch_attention_feats(interpreter, text_input)
        st.altair_chart(make_attention_charts(diag_data, tokens))
