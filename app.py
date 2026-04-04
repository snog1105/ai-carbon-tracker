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
# Replace these later with real data
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
    colors = {
        "No Impact": "#2E8B57",
        "Low Impact": "#9ACD32",
        "Moderate Impact": "#DAA520",
        "High Impact": "#DC143C"
    }
    return colors[level]


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
# Custom Styling
# -----------------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .impact-box {
        padding: 1rem;
        border-radius: 14px;
        color: white;
        font-weight: 600;
        text-align: center;
        margin-top: 0.5rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f5f7fa;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e6e9ef;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------
# Header
# -----------------------------------
st.markdown('<div class="main-title">Making the Invisible Visible</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">A Human-Centered AI Carbon Footprint Tracker</div>',
    unsafe_allow_html=True
)
st.write("Estimate the environmental impact of AI usage and explore more sustainable choices.")

st.divider()

# -----------------------------------
# Layout
# -----------------------------------
left_col, right_col = st.columns([1, 1.2])

# -----------------------------------
# Left Column: Inputs
# -----------------------------------
with left_col:
    st.markdown('<div class="section-header">Enter AI Usage Details</div>', unsafe_allow_html=True)

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
        <div class="info-box">
        <b>Project Goal:</b><br>
        Help users understand the hidden environmental footprint of AI and encourage more sustainable digital habits.
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------------------
# Calculate Results
# -----------------------------------
total_energy, carbon_emissions, water_used = calculate_results(
    num_prompts, model_size, task_type, energy_source
)

impact_level = get_impact_level(carbon_emissions)
impact_color = get_impact_color(impact_level)
tip = get_tip(impact_level)

# -----------------------------------
# Right Column: Results
# -----------------------------------
with right_col:
    st.markdown('<div class="section-header">Estimated Impact</div>', unsafe_allow_html=True)

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

# -----------------------------------
# Impact Scale
# -----------------------------------
st.divider()
st.markdown('<div class="section-header">Impact Scale</div>', unsafe_allow_html=True)

impact_score = min(carbon_emissions / 0.60, 1.0)
st.progress(impact_score)

scale_cols = st.columns(4)
scale_cols[0].markdown("**No Impact**")
scale_cols[1].markdown("**Low Impact**")
scale_cols[2].markdown("**Moderate Impact**")
scale_cols[3].markdown("**High Impact**")

# -----------------------------------
# Real-World Comparisons
# -----------------------------------
st.divider()
st.markdown('<div class="section-header">What Does This Mean?</div>', unsafe_allow_html=True)

phone_charges = total_energy / PHONE_CHARGE_KWH
laptop_hours = total_energy / LAPTOP_HOUR_KWH
miles_driven = carbon_emissions * MILES_PER_KG_CO2

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
st.divider()
st.markdown('<div class="section-header">Sustainability Tip</div>', unsafe_allow_html=True)
st.info(tip)

# -----------------------------------
# How It Works
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
st.divider()
st.markdown('<div class="section-header">Why This Matters</div>', unsafe_allow_html=True)
st.write(
    """
    AI is becoming part of everyday life, but its environmental footprint often stays hidden.
    This tool helps make that impact visible so people can use AI more thoughtfully and sustainably.
    """
)