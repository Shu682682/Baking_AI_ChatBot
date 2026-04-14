import re
import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000/chat"
REQUEST_TIMEOUT = 60

st.set_page_config(
    page_title="Baking AI Chatbot",
    page_icon="🍰",
    layout="wide"
)

# -----------------------------
# Session State
# -----------------------------
if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_input" not in st.session_state:
    st.session_state.user_input = "I want to bake a cake for 20 people, what do I need?"

if "sidebar_servings" not in st.session_state:
    st.session_state.sidebar_servings = 8


# -----------------------------
# Helpers
# -----------------------------
def extract_servings_from_text(text: str) -> int | None:
    patterns = [
        r"(\d+)\s*人份",
        r"(\d+)\s*個人",
        r"(\d+)\s*个人",
        r"(\d+)\s*人",
        r"(\d+)\s*位",
        r"for\s+(\d+)\s+people",
        r"make\s+(\d+)\s+people",
        r"for\s+(\d+)",
        r"serves?\s+(\d+)",
        r"(\d+)\s*servings?",
        r"(\d+)\s+people"
    ]

    lowered = text.lower()

    for pattern in patterns:
        match = re.search(pattern, lowered)
        if match:
            return int(match.group(1))

    return None


def get_effective_servings(text: str, sidebar_servings: int) -> int:
    detected = extract_servings_from_text(text)
    if detected is not None:
        return detected
    return sidebar_servings


def build_prompt(base_text: str, effective_servings: int | None, diet: str, equipment: str) -> str:
    cleaned = base_text.strip()
    parts = [cleaned]

    detected_servings = extract_servings_from_text(cleaned)

    if detected_servings is None and effective_servings and effective_servings > 0:
        parts.append(f"For {effective_servings} people.")

    if diet != "None":
        parts.append(f"Dietary preference: {diet}.")

    if equipment != "No limit":
        parts.append(f"Equipment available: {equipment}.")

    return " ".join(parts).strip()


def call_chat_api(message: str) -> dict:
    response = requests.post(
        API_URL,
        json={"message": message},
        timeout=REQUEST_TIMEOUT
    )
    response.raise_for_status()
    return response.json()


def render_ingredients_table(ingredients: list[dict]) -> None:
    df = pd.DataFrame(ingredients)
    df = df.rename(columns={
        "name": "Ingredient",
        "amount": "Amount",
        "unit": "Unit"
    })
    st.dataframe(df, width="stretch", hide_index=True)


def render_steps(steps: list[str]) -> None:
    for i, step in enumerate(steps, start=1):
        with st.container(border=True):
            st.markdown(f"**Step {i}**")
            st.write(step)


def add_history(user_message: str, result: dict) -> None:
    st.session_state.chat_history.insert(0, {
        "user_message": user_message,
        "recipe_name": result.get("recipe_name", ""),
        "servings": result.get("servings", ""),
        "answer": result.get("answer", "")
    })


def set_example_prompt(prompt: str) -> None:
    st.session_state.user_input = prompt
    st.rerun()


# -----------------------------
# Header
# -----------------------------
st.title("🍰 Baking AI Chatbot")
st.caption("Find dessert recipes, scale ingredients, and get baking steps with AI assistance.")

typed_servings = extract_servings_from_text(st.session_state.user_input)
effective_servings = get_effective_servings(
    st.session_state.user_input,
    st.session_state.sidebar_servings
)

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.header("Controls")

    st.number_input(
        "Servings",
        min_value=1,
        step=1,
        key="sidebar_servings"
    )

    diet = st.selectbox(
        "Dietary preference",
        ["None", "Low Sugar", "Dairy Free", "Egg Free", "Nut Free", "No Egg", "Vegan"]
    )

    equipment = st.selectbox(
        "Equipment",
        ["No limit", "Oven", "Air Fryer", "Mixer only", "No oven"]
    )

    if typed_servings is not None:
        st.info(f"Detected {typed_servings} servings from your typed request. This value will be used.")
    else:
        st.caption(f"Using sidebar servings: {st.session_state.sidebar_servings}")

    st.divider()
    st.subheader("Example prompts")

    if st.button("Chocolate Cake", width="stretch"):
        set_example_prompt("I want to make a chocolate cake for 8 people")

    if st.button("Brownies", width="stretch"):
        set_example_prompt("Give me a brownie recipe for 12 people")

    if st.button("Pumpkin Pie", width="stretch"):
        set_example_prompt("我要做南瓜派5個人")

    if st.button("Tiramisu", width="stretch"):
        set_example_prompt("I want to make tiramisu for 6 people")

    if st.button("Blueberry Muffins", width="stretch"):
        set_example_prompt("I want blueberry muffins for 10 people")

    st.divider()
    st.subheader("System")
    st.code(API_URL, language="text")

    if st.button("Clear current result", width="stretch"):
        st.session_state.last_result = None
        st.rerun()

    if st.button("Clear chat history", width="stretch"):
        st.session_state.chat_history = []
        st.rerun()

# -----------------------------
# Main Input Area
# -----------------------------
left_col, right_col = st.columns([1.5, 1])

with left_col:
    st.subheader("Ask for a dessert recipe")
    st.text_input(
        "Your request",
        key="user_input"
    )

with right_col:
    st.subheader("Generated request preview")
    preview_prompt = build_prompt(
        base_text=st.session_state.user_input,
        effective_servings=effective_servings,
        diet=diet,
        equipment=equipment
    )
    st.info(preview_prompt)
    st.markdown(f"**Effective servings:** {effective_servings}")

send_clicked = st.button("Send", width="stretch")

# -----------------------------
# API Call
# -----------------------------
if send_clicked:
    final_prompt = build_prompt(
        base_text=st.session_state.user_input,
        effective_servings=effective_servings,
        diet=diet,
        equipment=equipment
    )

    if not final_prompt.strip():
        st.warning("Please enter a request first.")
    else:
        try:
            with st.spinner("Generating recipe..."):
                result = call_chat_api(final_prompt)

            st.session_state.last_result = result
            add_history(final_prompt, result)
            st.rerun()

        except requests.exceptions.Timeout:
            st.error("The request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            st.error("Could not connect to the FastAPI server. Make sure it is running.")
        except requests.exceptions.HTTPError as e:
            st.error(f"API returned an error: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")

# -----------------------------
# Results Section
# -----------------------------
result = st.session_state.last_result

if result:
    st.divider()
    st.subheader(f"🎂 {result['recipe_name']}")

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Servings", result["servings"])
    with metric_col2:
        st.metric("Ingredients Count", len(result["ingredients"]))
    with metric_col3:
        st.metric("Effective Input Servings", effective_servings)

    top_left, top_right = st.columns([1.2, 1])

    with top_left:
        st.markdown("### AI Response")
        with st.container(border=True):
            st.write(result["answer"])

    with top_right:
        st.markdown("### Ingredients")
        render_ingredients_table(result["ingredients"])

    st.markdown("### Steps")
    render_steps(result["steps"])

    with st.expander("Raw API Response"):
        st.json(result)
else:
    st.info("Enter a baking request, choose options in the sidebar, and click Send.")

# -----------------------------
# Chat History
# -----------------------------
st.divider()
st.subheader("Recent Requests")

if st.session_state.chat_history:
    for idx, item in enumerate(st.session_state.chat_history[:5], start=1):
        with st.expander(f"{idx}. {item['recipe_name']} — {item['servings']} servings"):
            st.markdown(f"**Request:** {item['user_message']}")
            st.markdown(f"**Recipe:** {item['recipe_name']}")
            st.markdown(f"**Servings:** {item['servings']}")
            st.markdown("**AI Summary:**")
            st.write(item["answer"])
else:
    st.caption("No requests yet.")