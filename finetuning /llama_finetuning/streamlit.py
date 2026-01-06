

'''@st.cache_resource()
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    return tokenizer, model

tokenizer, model = load_model()

SYSTEM_PROMPT = """
You are the Dubai Customs HS Code Classification Assistant.

Your job is to classify only physical products, commodities, or traded goods
that exist in your fine-tuned HS Code training data.

If the user query is not a physical product, manufactured item, commodity,
or traded good, respond with:

"I'm a Dubai Customs assistant, so please ask a question related to HS Codes."

STRICT RULES:
1. Answer ONLY using HS Codes found in your training data.
2. If the item is not found in data, reply: "I don’t have information"
3. Do NOT guess or assume.
4. When valid classification exists, return:

    HS Code:
    Reasoning:
    Duty:
    Alt Duty:
    Statistical Unit:
""".strip()

def extract_assistant_response(text):
    if "assistant" in text:
        return text.split("assistant")[-1].strip()
    return text.strip()

def classify_hs_code(user_query):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
    ]

    prompt = tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    output_ids = model.generate(
        **inputs,
        max_new_tokens=350,
        do_sample=False,
        temperature=0.0,
    )

    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return extract_assistant_response(output_text)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🇦🇪 Dubai Customs HS Code Classifier")
st.write("Enter a product name or description to classify.")

user_input = st.text_input("Product Description:", "")

if st.button("Classify") and user_input.strip():
    with st.spinner("Classifying..."):
        result = classify_hs_code(user_input)
    st.success("Classification Result:")
    st.write(result)

st.markdown("---")
st.caption("Powered by Llama 3.1 HS Code Fine-tuned Model 🚀")
'''
