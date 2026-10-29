
import logging
import os
import time
import streamlit as st
from agent import create_research_brief

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("task_agent")

st.set_page_config(
    page_title="Task Automation Research Agent",
    page_icon="🔎",
    layout="centered",
)

st.title("🔎 Task-Automation Research Agent")
st.write(
    "Enter a topic. The agent searches the web and "
    "summarizes the findings into exactly three key points."
)
st.caption(
    "Powered by DuckDuckGo search and Groq. "
    "Do not enter private or confidential information."
)

topic = st.text_input(
    "Research topic",
    placeholder="e.g., Recent applications of AI in healthcare",
)
run = st.button("Search and summarize", type="primary")

if run:
    cleaned_topic = topic.strip()

    if not cleaned_topic:
        st.warning("Please enter a research topic.")

    elif len(cleaned_topic) > 300:
        st.error("Please keep the topic under 300 characters.")

    elif not os.getenv("GROQ_API_KEY"):
        st.error("GROQ_API_KEY is not configured.")
        logger.error("API key is missing")

    else:
        started = time.perf_counter()
        logger.info("Research request received: topic=%r", cleaned_topic)

        try:
            with st.status(
                "Starting research workflow...",
                expanded=True,
            ) as status:
                st.write("Step 1/2: Searching the web...")
                brief, sources = create_research_brief(cleaned_topic)

                st.write("Step 2/2: Summarizing search results...")
                status.update(
                    label="Research completed",
                    state="complete",
                    expanded=False,
                )

            # Extract non-empty findings from the response.
            points = [
                line.strip().lstrip("-*• ").strip()
                for line in brief.splitlines()
                if line.strip().lstrip("-*• ").strip()
            ]

            if len(points) != 3:
                raise ValueError(
                    "The model did not return exactly three "
                    "non-empty findings. Please try again."
                )

            st.subheader("Three-point research brief")

            for point in points:
                st.markdown(f"- {point}")

            if sources:
                with st.expander("Sources used"):
                    for i, source in enumerate(sources, start=1):
                        st.markdown(
                            f"{i}. [{source['title']}]"
                            f"({source['url']})"
                        )

            elapsed = time.perf_counter() - started
            st.caption(f"Completed in {elapsed:.2f} seconds.")

            logger.info(
                "Research completed in %.2f seconds; sources=%d",
                elapsed,
                len(sources),
            )

        except Exception as exc:
            elapsed = time.perf_counter() - started
            logger.exception(
                "Research failed after %.2f seconds",
                elapsed,
            )
            st.error(f"Unable to complete the request: {exc}")
