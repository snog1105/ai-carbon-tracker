import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AI Carbon Footprint Tracker",
    page_icon="🌍",
    layout="wide"
)

MODEL_PROFILES = {
    "Lightweight Text Model": {
        "description": (
            "Based on published research estimating the average energy used for AI text responses. "
            "Values are estimates because AI providers do not publicly share exact energy use for each prompt. "
        ),
        "rates": {
            "Short text response": 0.000047,
            "Long text generation": 0.000470,
            "Multiple regenerations": 0.001410,
            "Image generation": 0.002907
        }
    },
    "Standard Chat Model": {
        "description": (
            "General-purpose chat profile anchored to a published estimate of about "
            "0.43 Wh for a short GPT-4o-style query."
        ),
        "rates": {
            "Short text response": 0.000430,
            "Long text generation": 0.001500,
            "Multiple regenerations": 0.004500,
            "Image generation": 0.005000
        }
    },
    "Advanced Reasoning Model": {
        "description": (
            "Reasoning-heavy profile using the higher energy range reported for modern "
            "reasoning systems. Long prompts can be much more energy-intensive."
        ),
        "rates": {
            "Short text response": 0.005000,
            "Long text generation": 0.033000,
            "Multiple regenerations": 0.099000,
            "Image generation": 0.008000
        }
    },
    "Large Multimodal Model": {
        "description": (
            "High-end multimodal profile. Image generation uses the upper measured value "
            "reported in Luccioni et al., about 11.49 Wh per generated image."
        ),
        "rates": {
            "Short text response": 0.000430,
            "Long text generation": 0.003000,
            "Multiple regenerations": 0.009000,
            "Image generation": 0.011490
        }
    }
}

GRID_REGIONS = {
    "US Average": {"carbon_factor": 0.40, "description": "Average electricity grid estimate."},
    "California": {"carbon_factor": 0.20, "description": "Lower-carbon grid with more renewable energy."},
    "Texas": {"carbon_factor": 0.45, "description": "Mixed grid with significant fossil fuel use."},
    "Quebec": {"carbon_factor": 0.03, "description": "Very low-carbon grid because of hydroelectric power."},
    "India": {"carbon_factor": 0.70, "description": "Higher-carbon grid due to heavier fossil fuel use."}
}

DEFAULT_WATER_FACTOR = 0.36
PHONE_CHARGE_KWH = 0.022
LITERS_PER_US_GALLON = 3.785411784
LAPTOP_HOUR_KWH = 0.05

# EPA equivalency: 0.391 kg CO2e per mile for an average gasoline vehicle.
MILES_PER_KG_CO2 = 1 / 0.391

LED_BULB_KWH_PER_MIN = 0.010 / 60
LAPTOP_KWH_PER_MIN = 0.05 / 60


# Research-informed water estimate.
# Li et al. estimate roughly 10-50 mL of water for a medium-length
# language-model response. This tracker uses the midpoint: 25 mL.
#
# The baseline energy reference is 0.43 Wh for a standard short chat query.
# Higher-energy tasks are scaled relative to that baseline. This makes
# image generation and advanced reasoning use more water than short text.
BASE_TEXT_PROMPT_WATER_L = 0.025
BASE_TEXT_PROMPT_ENERGY_KWH = 0.000430


if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None


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
        "Low Impact": "#7DBB75",
        "Moderate Impact": "#D9A441",
        "High Impact": "#C94C4C"
    }[level]


def get_tip_options(level: str):
    if level == "No Impact":
        return [
            "You are already using AI in a relatively efficient way.",
            "Keep prompts focused and avoid unnecessary repetitions.",
            "Use smaller models when advanced reasoning is not needed."
        ]
    elif level == "Low Impact":
        return [
            "Try combining small prompts into one focused request.",
            "Use a lower-impact model for simple tasks.",
            "Avoid regenerating answers unless necessary."
        ]
    elif level == "Moderate Impact":
        return [
            "Reduce repeated prompts by planning your request first.",
            "Use advanced models only for tasks that truly require them.",
            "Choose lower-impact tasks when possible."
        ]
    return [
        "Use smaller or lighter models for routine tasks.",
        "Avoid repeated image generations or unnecessary retries.",
        "Combine tasks into one clear prompt to reduce total usage."
    ]


def calculate_results(
    num_prompts,
    model_profile,
    task_type,
    grid_region,
    carbon_factor,
    water_factor
):
    energy_per_prompt = MODEL_PROFILES[model_profile]["rates"][task_type]
    total_energy = energy_per_prompt * num_prompts
    carbon_emissions = total_energy * carbon_factor

    # Scale the midpoint water estimate for a standard text prompt
    # according to the selected task's energy demand.
    energy_intensity_ratio = (
        energy_per_prompt / BASE_TEXT_PROMPT_ENERGY_KWH
    )
    water_per_prompt = (
        BASE_TEXT_PROMPT_WATER_L * energy_intensity_ratio
    )

    # The existing advanced-assumption slider acts as an adjustment
    # around the default data-center water-use assumption.
    water_adjustment = water_factor / DEFAULT_WATER_FACTOR
    water_used = (
        num_prompts
        * water_per_prompt
        * water_adjustment
    )

    return energy_per_prompt, total_energy, carbon_emissions, water_used


def build_comparison_text(current, previous):
    if previous is None:
        return None

    carbon_diff = current["carbon_emissions"] - previous["carbon_emissions"]
    energy_diff = current["total_energy"] - previous["total_energy"]

    if carbon_diff < 0:
        phone_savings = abs(energy_diff) / PHONE_CHARGE_KWH
        return (
            f"Compared with your last estimate, this scenario uses "
            f"**{abs(energy_diff):.3f} fewer kWh** and emits "
            f"**{abs(carbon_diff):.3f} fewer kg CO₂e** "
            f"(about **{phone_savings:.1f} phone charges saved**)."
        )
    elif carbon_diff > 0:
        extra_phone = abs(energy_diff) / PHONE_CHARGE_KWH
        return (
            f"Compared with your last estimate, this scenario uses "
            f"**{abs(energy_diff):.3f} more kWh** and emits "
            f"**{abs(carbon_diff):.3f} more kg CO₂e** "
            f"(about **{extra_phone:.1f} additional phone charges worth of energy**)."
        )
    return "This estimate is essentially the same as your previous one."


st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, #f3fbf6 0%, #edf7f0 35%, #f8fcf9 100%);
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }

    .hero-wrap {
        background: linear-gradient(135deg, #16362b 0%, #20483a 55%, #2c5e4d 100%);
        border-radius: 26px;
        padding: 2.1rem 2rem 1.8rem 2rem;
        color: white;
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.12);
        margin-bottom: 1.2rem;
        border: 1px solid rgba(255,255,255,0.08);
    }

    .hero-kicker {
        text-transform: uppercase;
        letter-spacing: 0.12em;
        font-size: 0.8rem;
        opacity: 0.85;
        margin-bottom: 0.8rem;
        color: #f4fff7;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.05;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #dcefe3;
        max-width: 850px;
        margin-bottom: 1.2rem;
    }

    .hero-badge-row {
        display: flex;
        gap: 0.7rem;
        flex-wrap: wrap;
        margin-top: 0.4rem;
    }

    .hero-badge {
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.14);
        color: #f4fff7;
        border-radius: 999px;
        padding: 0.42rem 0.85rem;
        font-size: 0.9rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #173A2D;
        margin-top: 0.15rem;
        margin-bottom: 0.75rem;
    }

    .custom-card {
        background: rgba(255,255,255,0.96);
        border: 1px solid #e3efe6;
        border-radius: 20px;
        padding: 1.2rem;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        backdrop-filter: blur(6px);
    }

    .mini-card {
        background: rgba(255,255,255,0.96);
        border: 1px solid #e3efe6;
        border-radius: 18px;
        padding: 1rem;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.04);
        height: 100%;
    }

    .soft-box {
        background: #f4fbf6;
        border: 1px solid #d9eadf;
        border-radius: 14px;
        padding: 1rem;
        color: #254737;
        margin-top: 0.8rem;
    }

    .impact-box {
        padding: 0.9rem;
        border-radius: 14px;
        color: white !important;
        font-weight: 700;
        text-align: center;
        font-size: 1.05rem;
        margin-top: 0.7rem;
        margin-bottom: 0.8rem;
    }

    .compare-box {
        background: #f7fbf8;
        border: 1px solid #dfeee4;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        color: #234636;
        margin-top: 0.8rem;
    }

    .impact-scale-wrap {
        margin-top: 0.8rem;
        margin-bottom: 0.2rem;
    }

    .impact-scale-bar {
        position: relative;
        width: 100%;
        height: 22px;
        border-radius: 999px;
        background: linear-gradient(
            90deg,
            #2E8B57 0%,
            #84C57C 35%,
            #D9A441 70%,
            #C94C4C 100%
        );
        box-shadow: inset 0 0 0 1px rgba(0,0,0,0.08);
    }

    .impact-scale-marker {
        position: absolute;
        top: -6px;
        width: 4px;
        height: 34px;
        background: #173A2D;
        border-radius: 4px;
        transform: translateX(-50%);
    }

    .impact-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: #4E7564;
        margin-top: 0.45rem;
    }

    .info-grid-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #173A2D;
        margin-bottom: 0.35rem;
    }

    .info-grid-text {
        color: #406555;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .footer-note {
        text-align: center;
        color: #5B7769;
        font-size: 0.95rem;
        margin-top: 0.8rem;
        margin-bottom: 0.4rem;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e3efe6;
        padding: 0.85rem;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        border-radius: 12px !important;
    }

    .streamlit-expanderHeader {
        font-weight: 600;
        color: #173A2D;
    }

    @media screen and (max-width: 768px) {
        p, span, div, label, small,
        [data-testid="stMarkdownContainer"],
        [data-testid="stWidgetLabel"],
        [data-testid="stCaptionContainer"] {
            color: #18382F !important;
            opacity: 1 !important;
        }

        [data-testid="stMetric"] *,
        .custom-card *,
        .mini-card *,
        .soft-box *,
        .compare-box * {
            color: #18382F !important;
            opacity: 1 !important;
        }

        .hero-wrap *,
        .hero-title,
        .hero-subtitle,
        .hero-kicker,
        .hero-badge {
            color: #ffffff !important;
            opacity: 1 !important;
        }

        div[data-baseweb="select"] > div {
            color: #FFFFFF !important;
            opacity: 1 !important;
        }

        div[data-baseweb="select"] span {
            color: #FFFFFF !important;
            opacity: 1 !important;
        }

        div[data-baseweb="menu"] * {
            color: #FFFFFF !important;
            opacity: 1 !important;
        }

        button[data-baseweb="tab"] *,
        button[data-baseweb="tab"] {
            opacity: 1 !important;
        }

        .impact-box,
        .impact-box * {
            color: #ffffff !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="hero-wrap">
        <div class="hero-kicker">Human-Centered AI • Sustainability • Behavior Change</div>
        <h1 class="hero-title">AI Carbon Footprint Tracker: Making the Invisible Visible</h1>
        <p class="hero-subtitle">
            Estimate the carbon emissions, energy use, and water footprint of AI prompts in real time, and explore how clearer feedback can encourage more thoughtful, sustainable digital habits.
        </p>
        <div class="hero-badge-row">
            <div class="hero-badge">Energy Use</div>
            <div class="hero-badge">Carbon Emissions</div>
            <div class="hero-badge">Water Consumption</div>
            <div class="hero-badge">Regional Grid Impact</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

c1, c2 = st.columns(2)

with c1:
    st.markdown(
        """
        <div class="mini-card">
            <h3 class="info-grid-title">What this tool does</h3>
            <div class="info-grid-text">
                It estimates the environmental footprint of AI use and turns abstract technical data into understandable, user-facing feedback.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with c2:
    st.markdown(
        """
        <div class="mini-card">
            <h3 class="info-grid-title">Why it matters</h3>
            <div class="info-grid-text">
                Most users never see the hidden energy, water, or carbon cost behind everyday AI interactions.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

tracker_tab, insights_tab, why_tab = st.tabs(["Tracker", "Insights", "Why This Matters"])

with tracker_tab:
    left_col, right_col = st.columns([1, 1.2], gap="large")

    with left_col:
        st.markdown('<h2 class="section-title">🌱 AI Usage Details</h2>', unsafe_allow_html=True)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)

        num_prompts = st.slider(
            "Number of AI prompts",
            min_value=1,
            max_value=500,
            value=25,
            step=1,
            help="Choose how many times a user interacts with the AI in one usage scenario."
        )
        st.caption("More prompts usually increase total energy use and environmental impact.")

        model_profile = st.selectbox(
            "Model profile",
            list(MODEL_PROFILES.keys()),
            help="Choose the type of AI system being used."
        )
        st.caption(MODEL_PROFILES[model_profile]["description"])

        task_type = st.selectbox(
            "Task type",
            [
                "Short text response",
                "Long text generation",
                "Multiple regenerations",
                "Image generation"
            ],
            help="Different AI tasks require different levels of computation."
        )
        st.caption("Image generation and repeated regenerations are usually more resource-intensive.")

        grid_region = st.selectbox(
            "Electricity grid region",
            list(GRID_REGIONS.keys()),
            help="Different regions use different energy sources, so the same AI task can create different emissions depending on where the electricity comes from."
        )
        st.caption(GRID_REGIONS[grid_region]["description"])
        st.caption("The same AI task can have a different environmental impact depending on where the electricity comes from.")

        with st.expander("Advanced Assumptions"):
            st.write("Use these controls to test how changing assumptions affects the output.")

            carbon_factor = st.slider(
                "Carbon factor (kg CO₂e per kWh)",
                min_value=0.01,
                max_value=1.00,
                value=float(GRID_REGIONS[grid_region]["carbon_factor"]),
                step=0.01,
                help="This estimates how much carbon is produced per unit of electricity used."
            )

            water_factor = st.slider(
                "Water factor (liters per kWh)",
                min_value=0.0,
                max_value=5.0,
                value=float(DEFAULT_WATER_FACTOR),
                step=0.01
            )

        st.markdown(
            """
            <div class="soft-box">
                <b>Project Goal:</b><br>
                Help users understand the hidden environmental footprint of AI and encourage more sustainable digital habits through clear, real-time feedback.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    energy_per_prompt, total_energy, carbon_emissions, water_used = calculate_results(
        num_prompts=num_prompts,
        model_profile=model_profile,
        task_type=task_type,
        grid_region=grid_region,
        carbon_factor=carbon_factor,
        water_factor=water_factor
    )

    impact_level = get_impact_level(carbon_emissions)
    impact_color = get_impact_color(impact_level)

    water_used_gallons = water_used / LITERS_PER_US_GALLON
    phone_charges = total_energy / PHONE_CHARGE_KWH
    laptop_minutes = total_energy / LAPTOP_KWH_PER_MIN
    miles_driven = carbon_emissions * MILES_PER_KG_CO2
    led_bulb_minutes = total_energy / LED_BULB_KWH_PER_MIN

    current_result = {
        "num_prompts": num_prompts,
        "model_profile": model_profile,
        "task_type": task_type,
        "grid_region": grid_region,
        "carbon_factor": carbon_factor,
        "water_factor": water_factor,
        "energy_per_prompt": energy_per_prompt,
        "total_energy": total_energy,
        "carbon_emissions": carbon_emissions,
        "water_used": water_used_gallons,
        "impact_level": impact_level
    }

    previous_result = st.session_state.last_result
    comparison_text = build_comparison_text(current_result, previous_result)

    if (
        previous_result is None
        or previous_result["num_prompts"] != current_result["num_prompts"]
        or previous_result["model_profile"] != current_result["model_profile"]
        or previous_result["task_type"] != current_result["task_type"]
        or previous_result["grid_region"] != current_result["grid_region"]
        or previous_result["carbon_factor"] != current_result["carbon_factor"]
        or previous_result["water_factor"] != current_result["water_factor"]
    ):
        st.session_state.history.append(current_result.copy())
        st.session_state.last_result = current_result.copy()

    with right_col:
        st.markdown('<h2 class="section-title">🌍 Estimated Impact</h2>', unsafe_allow_html=True)
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)

        r1, r2 = st.columns(2)
        with r1:
            st.metric("Energy Used", f"{total_energy:.3f} kWh")
            st.metric("Water Used", f"{water_used_gallons:.2f} gallons")
        with r2:
            st.metric("Carbon Emissions", f"{carbon_emissions:.3f} kg CO₂e")
            st.metric("Impact Level", impact_level)

        st.markdown(
            f"""
            <div class="soft-box">
                <b>Selected Grid Region:</b> {grid_region}<br>
                <b>Carbon Factor:</b> {carbon_factor:.2f} kg CO₂e per kWh<br>
                The same AI usage can create different emissions depending on the electricity grid.
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="impact-box" style="background-color:{impact_color};">
                {impact_level}
            </div>
            """,
            unsafe_allow_html=True
        )

        impact_position = min(carbon_emissions / 0.60, 1.0) * 100
        st.markdown(
            f"""
            <div class="impact-scale-wrap">
                <div class="impact-scale-bar">
                    <div class="impact-scale-marker" style="left:{impact_position}%;"></div>
                </div>
                <div class="impact-labels">
                    <span>No Impact</span>
                    <span>Low Impact</span>
                    <span>Moderate Impact</span>
                    <span>High Impact</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### What Does This Mean?")

        top_left, top_right = st.columns(2)
        with top_left:
            st.metric("Fully Charged Smartphones", f"{phone_charges:.1f}")
        with top_right:
            st.metric("Laptop Minutes", f"{laptop_minutes:.1f}")

        bottom_left, bottom_right = st.columns(2)
        with bottom_left:
            st.metric("Miles Driven", f"{miles_driven:.2f}")
        with bottom_right:
            st.metric("LED Bulb Minutes", f"{led_bulb_minutes:.1f}")

        st.markdown(
            """
            <div style="text-align:center; color:#6c757d; font-size:0.85rem; margin-top:0.6rem;">
                These comparisons are research-informed estimates designed to make AI's environmental impact easier to understand.
                Fully Charged Smartphones represents the equivalent number of complete smartphone charges, and water is shown in U.S. gallons.
                Actual environmental impact varies depending on the AI model, hardware, and data center used.
            </div>
            """,
            unsafe_allow_html=True,
        )

        if comparison_text:
            st.markdown(
                f"""
                <div class="compare-box">
                    <b>Compared with your last estimate:</b><br>{comparison_text}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<h2 class="section-title">💡 Sustainability Tips</h2>', unsafe_allow_html=True)
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    tip_options = get_tip_options(impact_level)
    tip_choice = st.selectbox(
        "Choose a tip to explore",
        options=[f"Tip {i+1}" for i in range(len(tip_options))]
    )
    tip_index = int(tip_choice.split()[-1]) - 1
    st.info(tip_options[tip_index])

    st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("How this estimate works"):
        st.write(
            """
            This tracker uses simplified prototype assumptions to estimate environmental impact.

            **Calculation logic**
            - Published per-prompt energy estimate × number of prompts = total energy used
            - Total energy × regional carbon factor = estimated CO₂ emissions
            - A 25 mL midpoint estimate for a standard text prompt is scaled by the selected task's energy intensity
            - Estimated water is converted from liters to U.S. gallons using 3.785411784 liters per gallon

            **Important limitation**
            The water estimate is research-informed, not a direct measurement. Published
            studies provide ranges for text prompts, but providers generally do not publish
            exact water use for every model and image-generation system. The tracker scales
            the text-prompt midpoint by energy intensity to create a consistent comparison.
            """
        )

with insights_tab:
    st.markdown('<h2 class="section-title">📈 Estimate History and Trends</h2>', unsafe_allow_html=True)
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)

    history_df = pd.DataFrame(st.session_state.history)
    if not history_df.empty:
        history_df = history_df.reset_index().rename(columns={"index": "Run"})
        history_df["Run"] = history_df["Run"] + 1

        st.write("This chart compares your recent estimate runs across carbon, energy, and water.")
        chart_df = history_df[["Run", "carbon_emissions", "total_energy", "water_used"]].rename(columns={"water_used": "water_used_gallons"}).set_index("Run")
        st.line_chart(chart_df)

        st.write("Recent estimate history:")
        st.dataframe(
            history_df[[
                "Run", "model_profile", "task_type", "grid_region",
                "num_prompts", "carbon_emissions",
                "total_energy", "water_used", "impact_level"
            ]].rename(columns={"water_used": "water_used_gallons"}),
            use_container_width=True
        )
    else:
        st.write("Your estimate history will appear here after you interact with the tracker.")

    st.markdown('</div>', unsafe_allow_html=True)

with why_tab:
    st.markdown('<h2 class="section-title">🌎 Why This Matters</h2>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="custom-card">
            <b>AI is becoming part of everyday life, but its environmental footprint often stays hidden.</b>
            <br><br>
            Behind every AI interaction is infrastructure that uses electricity, water, and computational power.
            When people cannot see that cost, it becomes difficult to make informed and sustainable choices.
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<h2 class="section-title">Key Takeaway</h2>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="soft-box">
            The goal is not to discourage innovation. The goal is to help users understand the hidden cost of AI
            so they can use it more thoughtfully and responsibly.
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    '<div class="footer-note">Designed to make the hidden environmental cost of AI easier to understand.</div>',
    unsafe_allow_html=True
)
