# AI Carbon Footprint Tracker

Estimate the carbon emissions, energy use, and water footprint of everyday AI prompts, in real time.

AI Carbon Footprint Tracker is a Streamlit app that turns the hidden environmental cost of AI use into clear, understandable feedback. Pick a model profile (lightweight, standard chat, advanced reasoning, or large multimodal), a task type, and an electricity grid region, and the tracker estimates:

- **Energy used** (kWh)
- **Carbon emissions** (kg CO₂e)
- **Water used** (liters)

Results are translated into relatable comparisons — phone charges, laptop hours, miles driven, LED bulb hours, microwave minutes, and TV hours — so the numbers are easy to reason about. The app also tracks your estimate history across a session and offers sustainability tips tailored to your current impact level.

## Live app

[ai-carbon-tracker.streamlit.app](https://ai-carbon-tracker.streamlit.app/)

## Why this matters

AI is becoming part of everyday life, but its environmental footprint often stays hidden. Behind every AI interaction is infrastructure that uses electricity, water, and computational power. When people cannot see that cost, it becomes difficult to make informed and sustainable choices. This tool makes the invisible visible.

## Running locally

```bash
pip install streamlit pandas
streamlit run app.py
```

## How the estimate works

- Energy per prompt × number of prompts = total energy used
- Total energy × regional carbon factor = estimated CO₂ emissions
- Total energy × water factor = estimated water usage

These are simplified prototype assumptions designed to improve awareness and support testing, not precise measurements.
