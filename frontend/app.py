"""
Streamlit Frontend for the SEO URL Optimizer.
Provides a web UI for URL input, batch processing, and report visualization.
"""

import sys
import os

# Add parent src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import pandas as pd
import streamlit as st
from main import SEOOptimizerPipeline


st.set_page_config(
    page_title="SEO URL Optimizer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #88c7f2;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
    }
    .score-card {
        background-color:#53735a;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    .score-value {
        font-size: 3rem;
        font-weight: bold;
    }
    .grade-a { color: #28a745; }
    .grade-b { color: #17a2b8; }
    .grade-c { color: #ffc107; }
    .grade-d { color: #fd7e14; }
    .grade-f { color: #dc3545; }
</style>
""", unsafe_allow_html=True)


def init_pipeline():
    """Initialize the SEO pipeline (cached)."""
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = SEOOptimizerPipeline()
    return st.session_state.pipeline


def render_header():
    """Render the app header."""
    st.markdown('<p class="main-header">🔍 LLM-Based SEO Chunking Optimizer</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Enter a URL to automatically extract, analyze, and optimize content for search engines.</p>', unsafe_allow_html=True)
    st.divider()


def render_sidebar():
    """Render sidebar controls."""
    with st.sidebar:
        st.header("⚙️ Settings")

        st.subheader("AI Model")
        model_choice = st.selectbox(
            "Select AI Model",
            ["Mock/Demo Mode (No API Key)", "OpenAI GPT-4o", "Google Gemini"],
            index=0
        )

        if model_choice == "OpenAI GPT-4o":
            openai_key = st.text_input("OpenAI API Key", type="password")
            if openai_key:
                os.environ['OPENAI_API_KEY'] = openai_key

        elif model_choice == "Google Gemini":
            gemini_key = st.text_input("Gemini API Key", type="password")
            if gemini_key:
                os.environ['GEMINI_API_KEY'] = gemini_key

        st.subheader("Chunking Options")
        max_words = st.slider("Max Words per Paragraph", 30, 100, 60)
        snippet_words = st.slider("Max Snippet Words", 40, 80, 60)

        st.subheader("Export")
        export_format = st.selectbox("Export Format", ["JSON", "CSV", "Markdown"])

        return {
            'model': model_choice,
            'max_words': max_words,
            'snippet_words': snippet_words,
            'export_format': export_format
        }


def render_url_input():
    """Render URL input section."""
    st.header("🌐 URL Input")

    tab1, tab2 = st.tabs(["Single URL", "Batch Upload"])

    with tab1:
        url = st.text_input("Enter website URL", placeholder="https://example.com")
        process_btn = st.button("🚀 Optimize Content", type="primary")

    with tab2:
        uploaded_file = st.file_uploader("Upload CSV with URLs", type=['csv'])
        batch_btn = st.button("🚀 Process Batch", type="primary")

    return {
        'single_url': url if process_btn else None,
        'batch_file': uploaded_file if batch_btn else None
    }


def render_score_card(score: int, grade: str):
    """Render the SEO score card."""
    grade_class = f"grade-{grade[0].lower()}" if grade else "grade-f"

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-value {grade_class}">{score}</div>
            <div>SEO Score / 100</div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="score-card">
            <div class="score-value {grade_class}">{grade}</div>
            <div>Grade</div>
        """, unsafe_allow_html=True)

    with col3:
        status = "✅ Optimized" if score >= 70 else "⚠️ Needs Work"
        st.markdown(f"""
        <div class="score-card">
            <div class="score-value">{status}</div>
            <div>Status</div>
        """, unsafe_allow_html=True)


def render_readability(readability: dict):
    """Render readability metrics."""
    st.subheader("📖 Readability")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Flesch Reading Ease", readability.get('flesch_reading_ease', 0))
    with col2:
        st.metric("Grade Level", readability.get('flesch_kincaid_grade', 0))
    with col3:
        st.metric("Avg Words/Sentence", readability.get('avg_words_per_sentence', 0))
    with col4:
        st.metric("Difficulty", readability.get('difficulty', 'Unknown'))


def render_keywords(keywords: dict):
    """Render keyword analysis."""
    st.subheader("🔑 Keyword Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Top Keywords**")
        top_kws = keywords.get('top_keywords', [])[:10]
        if top_kws:
            df = pd.DataFrame(top_kws, columns=['Keyword', 'Frequency'])
            st.dataframe(df, use_container_width=True)

    with col2:
        st.write("**Densities**")
        densities = keywords.get('densities', {})
        if densities:
            df = pd.DataFrame(list(densities.items())[:10], columns=['Keyword', 'Density (%)'])
            st.dataframe(df, use_container_width=True)

    if keywords.get('suggested_keywords'):
        st.write("**💡 Suggested Keywords:**")
        st.write(", ".join(keywords['suggested_keywords']))


def render_snippets(snippets: list):
    """Render featured snippets."""
    st.subheader("✨ Featured Snippets")

    if not snippets:
        st.info("No snippets generated.")
        return

    for i, snippet in enumerate(snippets[:5]):
        with st.expander(f"Snippet {i+1}: {snippet.get('type', 'Unknown').title()}"):
            if snippet.get('type') == 'definition':
                st.write(f"**{snippet.get('term', '')}**")
                st.write(snippet.get('answer', ''))
            elif snippet.get('type') == 'list':
                for item in snippet.get('items', []):
                    st.write(f"- {item}")
            elif snippet.get('type') == 'steps':
                for j, step in enumerate(snippet.get('steps', [])):
                    st.write(f"{j+1}. {step}")
            else:
                st.write(snippet.get('answer', ''))


def render_faq(faq: list):
    """Render FAQ section."""
    st.subheader("❓ Generated FAQ")

    if not faq:
        st.info("No FAQ generated.")
        return

    for i, item in enumerate(faq[:10]):
        with st.expander(item.get('question', 'Question')):
            st.write(item.get('answer', 'No answer found.'))


def render_paa(paa: list):
    """Render People Also Ask section."""
    st.subheader("🔍 People Also Ask")

    if not paa:
        st.info("No PAA generated.")
        return

    for item in paa[:8]:
        with st.expander(item.get('question', 'Question')):
            st.write(item.get('short_answer', ''))


def render_recommendations(recommendations: list):
    """Render SEO recommendations."""
    st.subheader("💡 Recommendations")

    if not recommendations:
        st.success("No issues found! Content is well-optimized.")
        return

    for rec in recommendations:
        st.warning(rec)


def render_comparison(comparison: dict):
    """Render before/after comparison."""
    st.subheader("🔄 Before vs After")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Before**")
        st.write(f"Title: {comparison.get('title', {}).get('before', '')}")
        st.write(f"Paragraphs: {comparison.get('paragraph_count', {}).get('before', 0)}")

    with col2:
        st.write("**After**")
        st.write(f"Title: {comparison.get('title', {}).get('after', '')}")
        st.write(f"Paragraphs: {comparison.get('paragraph_count', {}).get('after', 0)}")


def render_results(result: dict):
    """Render full optimization results."""
    if 'error' in result:
        st.error(f"Error: {result['error']}")
        return

    report = result.get('report', {})

    # Score Card
    render_score_card(report.get('overall_seo_score', 0), report.get('grade', 'F'))

    st.divider()

    # Tabs for detailed views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Readability", "Keywords", "Snippets", "FAQ & PAA", "Recommendations", "Comparison"
    ])

    with tab1:
        render_readability(report.get('readability', {}))

    with tab2:
        render_keywords(report.get('keyword_analysis', {}))

    with tab3:
        render_snippets(result.get('featured_snippets', []))

    with tab4:
        render_faq(result.get('faq', []))
        render_paa(result.get('paa', []))

    with tab5:
        render_recommendations(report.get('recommendations', []))

    with tab6:
        render_comparison(result.get('comparison', {}))


def main():
    """Main Streamlit app."""
    render_header()
    settings = render_sidebar()
    inputs = render_url_input()

    pipeline = init_pipeline()

    # Process single URL
    if inputs['single_url']:
        with st.spinner("🔍 Analyzing and optimizing content..."):
            try:
                result = pipeline.process_url(inputs['single_url'])
                render_results(result)
            except Exception as e:
                st.error(f"Processing failed: {str(e)}")

    # Process batch
    if inputs['batch_file']:
        with st.spinner("🔍 Processing batch URLs..."):
            try:
                import csv
                import io

                content = inputs['batch_file'].read().decode('utf-8')
                reader = csv.DictReader(io.StringIO(content))
                urls = [row['url'] for row in reader]

                results = pipeline.process_batch(urls)

                st.success(f"Processed {len(results)} URLs")

                # Show summary
                scores = [r.get('report', {}).get('overall_seo_score', 0) for r in results if 'error' not in r]
                if scores:
                    st.write(f"Average SEO Score: {sum(scores) / len(scores):.1f}")

                # Allow download of all reports
                import json
                all_reports = [r.get('report', {}) for r in results if 'error' not in r]
                st.download_button(
                    "Download All Reports (JSON)",
                    json.dumps(all_reports, indent=2),
                    "batch_reports.json"
                )

            except Exception as e:
                st.error(f"Batch processing failed: {str(e)}")


if __name__ == '__main__':
    main()
