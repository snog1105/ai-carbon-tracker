import streamlit as st

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="AI Carbon Footprint Tracker",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------------
# Placeholder Research Values
# Replace later with research-backed values
# -----------------------------------
ENERGY_RATES = {
    "Small": {
        "Short text response": 0.001,
        "Long text generation": 0.003,
        "Image generation": 0.008,
        "Multiple regenerations": 0.010
    },
    "Medium": {
        "Short text response": 0.002,
        "Long text generation": 0.005,
        "Image generation": 0.012,
        "Multiple regenerations": 0.015
    },
    "Large": {
        "Short text response": 0.004,
        "Long text generation": 0.008,
        "Image generation": 0.020,
        "Multiple regenerations": 0.025
    }
}

CARBON_FACTORS = {
    "Low-carbon grid": 0.15,
    "Average grid": 0.40,
    "High-carbon grid": 0.70
}

WATER_FACTOR = 2.0  # liters per kWh

PHONE_CHARGE_KWH = 0.012
LAPTOP_HOUR_KWH = 0.05
MILES_PER_KG_CO2 = 2.5

# -----------------------------------
# Helper Functions
# -----------------------------------
def get_impact_level(carbon_emissions: float) -> str:
    if carbon_emissions < 0.05:
        return "No Impact"
    elif carbon_emissions < 0.15:
        return "Low Impact"
    elif carbon_emissions < 0.40:
        return "Moderate Impact"
    return "High Impact"


def get_impact_color(level: str) -> str:
    return {
        "No Impact": "#2E8B57",
        "Low Impact": "#84C57C",
        "Moderate Impact": "#D9A441",
        "High Impact": "#C94C4C"
    }[level]


def get_tip(level: str) -> str:
    tips = {
        "No Impact": "This is a very low-impact use of AI. Focused, efficient tasks are generally more sustainable.",
        "Low Impact": "Good choice. Keeping prompts specific can help reduce unnecessary processing.",
        "Moderate Impact": "Consider combining prompts or reducing repeated regenerations to lower energy use.",
        "High Impact": "Try using a smaller model, shortening tasks, or avoiding repeated generations when possible."
    }
    return tips[level]


def calculate_results(num_prompts: int, model_size: str, task_type: str, energy_source: str):
    energy_per_prompt = ENERGY_RATES[model_size][task_type]
    total_energy = energy_per_prompt * num_prompts
    carbon_emissions = total_energy * CARBON_FACTORS[energy_source]
    water_used = total_energy * WATER_FACTOR
    return total_energy, carbon_emissions, water_used


# -----------------------------------
# Styling
# -----------------------------------
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background: linear-gradient(180deg, #edf7f0 0%, #f8fcf9 100%);
    }

    /* Main content width and padding */
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Typography */
    .hero-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        color: #173A2D;
        margin-bottom: 0.15rem;
    }

    .hero-subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #4E7564;
        margin-bottom: 1.6rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #173A2D;
        margin-top: 0.2rem;
        margin-bottom: 0.8rem;
    }

    /* Card style */
    .custom-card {
        background: #ffffff;
        border: 1px solid #e3efe6;
        border-radius: 18px;
        padding: 1.2rem;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }

    /* Soft info box */
    .soft-box {
        background: #f3fbf5;
        border: 1px solid #d9eadf;
        border-radius: 14px;
        padding: 1rem;
        color: #254737;
        margin-top: 0.8rem;
    }

    /* Impact badge */
    .impact-box {
        padding: 0.9rem;
        border-radius: 14px;
        color: white;
        font-weight: 700;
        text-align: center;
        font-size: 1.05rem;
        margin-top: 0.9rem;
        margin-bottom: 0.2rem;
    }

    /* Footer */
    .footer-note {
        text-align: center;
        color: #5B7769;
        font-size: 0.95rem;
        margin-top: 0.8rem;
        margin-bottom: 0.4rem;
    }

    /* Streamlit metric cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e3efe6;
        padding: 0.85rem;
        border-radius: 14px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }

    /* Rounded inputs */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        border-radius: 12px !important;
    }

    /* Make expander cleaner */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #173A2D;
    }

    /* Hide default top padding around title anchors */
    h1, h2, h3 {
        padding-top: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# Header
# -----------------------------------
st.markdown('<div class="hero-title">Making the Invisible Visible</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">A Human-Centered AI Carbon Footprint Tracker</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="custom-card">
        This tool estimates the environmental impact of AI use and helps users explore more sustainable choices through clear, real-time feedback.
    </div>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# Main Layout
# -----------------------------------
left_col, right_col = st.columns([1, 1.15], gap="large")

# -----------------------------------
# Inputs Section
# -----------------------------------
with left_col:
    st.markdown('<div class="section-title">🌱 Enter AI Usage Details</div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    num_prompts = st.slider(
        "Number of AI prompts",
        min_value=1,
        max_value=500,
        value=25,
        step=1
    )

    model_size = st.selectbox(
        "Model size",
        ["Small", "Medium", "Large"]
    )

    task_type = st.selectbox(
        "Task type",
        [
            "Short text response",
            "Long text generation",
            "Image generation",
            "Multiple regenerations"
        ]
    )

    energy_source = st.selectbox(
        "Electricity source",
        ["Low-carbon grid", "Average grid", "High-carbon grid"]
    )

    st.markdown(
        """
        <div class="soft-box">
        <b>Project Goal:</b><br>
        Help users understand the hidden environmental footprint of AI and encourage more sustainable digital habits.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# Calculations
# -----------------------------------
total_energy, carbon_emissions, water_used = calculate_results(
    num_prompts, model_size, task_type, energy_source
)

impact_level = get_impact_level(carbon_emissions)
impact_color = get_impact_color(impact_level)
tip = get_tip(impact_level)

phone_charges = total_energy / PHONE_CHARGE_KWH
laptop_hours = total_energy / LAPTOP_HOUR_KWH
miles_driven = carbon_emissions * MILES_PER_KG_CO2

# -----------------------------------
# Results Section
# -----------------------------------
with right_col:
    st.markdown('<div class="section-title">🌍 Estimated Impact</div>', unsafe_allow_html=True)
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    r1, r2 = st.columns(2)
    with r1:
        st.metric("Energy Used", f"{total_energy:.3f} kWh")
        st.metric("Water Used", f"{water_used:.2f} liters")
    with r2:
        st.metric("Carbon Emissions", f"{carbon_emissions:.3f} kg CO₂e")
        st.metric("Impact Level", impact_level)

    st.markdown(
        f"""
        <div class="impact-box" style="background-color:{impact_color};">
            {impact_level}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# Impact Scale
# -----------------------------------
st.markdown('<div class="section-title">📊 Impact Scale</div>', unsafe_allow_html=True)
st.markdown('<div class="custom-card">', unsafe_allow_html=True)

impact_score = min(carbon_emissions / 0.60, 1.0)
st.progress(impact_score)

scale_cols = st.columns(4)
with scale_cols[0]:
    st.markdown("**No Impact**")
with scale_cols[1]:
    st.markdown("**Low Impact**")
with scale_cols[2]:
    st.markdown("**Moderate Impact**")
with scale_cols[3]:
    st.markdown("**High Impact**")

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------
# Real-world Comparisons
# -----------------------------------
st.markdown('<div class="section-title">🔍 What Does This Mean?</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Phone Charges Equivalent", f"{phone_charges:.1f}")
with c2:
    st.metric("Laptop Hours Equivalent", f"{laptop_hours:.1f}")
with c3:
    st.metric("Miles Driven Equivalent", f"{miles_driven:.2f}")

# -----------------------------------
# Sustainability Tip
# -----------------------------------
st.markdown('<div class="section-title">💡 Sustainability Tip</div>', unsafe_allow_html=True)
st.info(tip)

# -----------------------------------
# Transparency / Method
# -----------------------------------
with st.expander("How this estimate works"):
    st.write(
        """
        This tracker uses simplified estimates to approximate the environmental impact of AI usage.

        **Calculation logic**
        - Energy per task × number of prompts = total energy used
        - Total energy × carbon factor = estimated CO₂ emissions
        - Total energy × water factor = estimated water usage

        These values are currently placeholders and should be replaced with research-based assumptions.
        """
    )

# -----------------------------------
# Why This Matters
# -----------------------------------
st.markdown('<div class="section-title">🌎 Why This Matters</div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="custom-card">
        AI is becoming part of everyday life, but its environmental footprint often stays hidden.
        This tool helps make that impact visible so people can use AI more thoughtfully and sustainably.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    '<div class="footer-note">Designed to make the hidden environmental cost of AI easier to understand.</div>',
    unsafe_allow_html=True
)
