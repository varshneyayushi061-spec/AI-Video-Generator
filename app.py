"""Streamlit UI for a prompt-to-video workflow.

The app uses a LangChain prompt pipeline to turn a short user idea into a
production-ready video prompt.  Video providers are deliberately abstracted:
add your preferred provider in `generate_video` when its API is available.
"""

from __future__ import annotations

import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


load_dotenv()

PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert cinematic prompt engineer for text-to-video models.
Expand the user's idea into one polished prompt ready for the selected video model.
Include the subject, action, setting, camera movement, lighting, mood, visual style,
and only useful technical detail. Respect the requested duration and aspect ratio.
Do not add headings, explanations, or unsupported claims. Return only the final prompt.""",
        ),
        (
            "human",
            """Idea: {idea}
Video model: {video_model}
Duration: {duration_seconds} seconds
Aspect ratio: {aspect_ratio}
Style notes: {style_notes}""",
        ),
    ]
)


def build_enhancement_chain(model_name: str):
    """Build a LangChain LCEL pipeline for prompt enhancement."""
    llm = ChatOpenAI(model=model_name, temperature=0.7)
    return PROMPT_TEMPLATE | llm | StrOutputParser()


def generate_video(video_model: str, prompt: str) -> Optional[str]:
    """Send `prompt` to a video provider and return a playable video URL.

    This is the integration seam for your chosen text-to-video provider. APIs vary
    between providers and may be asynchronous, so the starter intentionally keeps
    this explicit rather than pretending one SDK works for every model.
    """
    if video_model == "API integration not configured":
        return None

    # Example implementation location:
    # if video_model == "Replicate":
    #     import replicate
    #     output = replicate.run("owner/model:version", input={"prompt": prompt})
    #     return str(output)
    raise NotImplementedError(
        f"Add the API call for {video_model!r} in generate_video() before generating videos."
    )


def main() -> None:
    st.set_page_config(page_title="AI Video Generator", page_icon="video", layout="wide")
    st.title("AI Video Generator")
    st.caption("Turn a simple idea into an enhanced video prompt, then send it to your video model.")

    with st.sidebar:
        st.header("Workflow settings")
        prompt_model = st.selectbox(
            "Prompt enhancement model",
            ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"],
            help="Uses the OpenAI API key in your .env file.",
        )
        video_model = st.selectbox(
            "Text-to-video model",
            ["API integration not configured", "Replicate", "Runway", "Luma", "Pika"],
        )
        duration_seconds = st.slider("Duration (seconds)", min_value=2, max_value=15, value=5)
        aspect_ratio = st.selectbox("Aspect ratio", ["16:9", "9:16", "1:1"])

    idea = st.text_area(
        "What video do you want to make?",
        placeholder="A tiny astronaut tending glowing flowers on the moon at sunrise",
        height=120,
    )
    style_notes = st.text_input(
        "Optional style notes",
        placeholder="e.g. cinematic, whimsical, photorealistic",
    )

    if st.button("Enhance prompt", type="primary", disabled=not idea.strip()):
        if not os.getenv("OPENAI_API_KEY"):
            st.error("Missing OPENAI_API_KEY. Add it to your .env file, then restart Streamlit.")
            return

        try:
            with st.spinner("Creating a production-ready prompt..."):
                enhanced_prompt = build_enhancement_chain(prompt_model).invoke(
                    {
                        "idea": idea,
                        "video_model": video_model,
                        "duration_seconds": duration_seconds,
                        "aspect_ratio": aspect_ratio,
                        "style_notes": style_notes or "No additional style requirements.",
                    }
                )
            st.session_state.enhanced_prompt = enhanced_prompt
        except Exception as error:
            st.error(f"Could not enhance the prompt: {error}")

    if enhanced_prompt := st.session_state.get("enhanced_prompt"):
        st.subheader("Enhanced prompt")
        edited_prompt = st.text_area("Review or edit before generation", enhanced_prompt, height=170)
        if st.button("Generate video", disabled=video_model == "API integration not configured"):
            try:
                with st.spinner(f"Submitting to {video_model}..."):
                    video_url = generate_video(video_model, edited_prompt)
                if video_url:
                    st.video(video_url)
                    st.success("Video generated.")
                else:
                    st.info("Configure a provider integration in generate_video() to generate videos.")
            except NotImplementedError as error:
                st.warning(str(error))
            except Exception as error:
                st.error(f"Video generation failed: {error}")


if __name__ == "__main__":
    main()
