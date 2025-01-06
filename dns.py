import streamlit as st
import pandas as pd
from domain_research_crew import DomainResearchCrew
import plotly.express as px
from datetime import datetime
import time

# Set page config
st.set_page_config(
    page_title="Domain Research Assistant",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
        font-weight: bold;
    }
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .highlight {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

class DomainResearchUI:
    def __init__(self):
        self.crew = DomainResearchCrew()
        if 'stage' not in st.session_state:
            st.session_state.stage = 'input'
        if 'selected_names' not in st.session_state:
            st.session_state.selected_names = []
        if 'final_results' not in st.session_state:
            st.session_state.final_results = None

    def render_header(self):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<p class="big-font">🔍 Domain Research Assistant</p>', unsafe_allow_html=True)
            st.markdown("---")

    def render_progress(self):
        stages = ['Input', 'Name Selection', 'Analysis']
        current_stage = {'input': 1, 'selection': 2, 'analysis': 3}[st.session_state.stage]
        
        progress = current_stage / len(stages)
        st.progress(progress)
        
        cols = st.columns(len(stages))
        for idx, (col, stage) in enumerate(zip(cols, stages)):
            with col:
                if idx + 1 < current_stage:
                    st.markdown(f"✅ {stage}")
                elif idx + 1 == current_stage:
                    st.markdown(f"🔄 {stage}")
                else:
                    st.markdown(f"⏳ {stage}")

    def render_input_stage(self):
        with st.container():
            st.markdown("### What kind of domain are you looking for?")
            
            col1, col2 = st.columns([2, 1])
            with col1:
                domain_type = st.text_input(
                    "Describe your business or project",
                    placeholder="e.g., tech startup, food blog, fitness coaching..."
                )
                
                industry = st.selectbox(
                    "Select your industry",
                    ["Technology", "E-commerce", "Healthcare", "Education", "Entertainment", "Other"]
                )
                
            with col2:
                st.markdown("#### Preferences")
                max_length = st.slider("Maximum domain length", 5, 20, 15)
                include_numbers = st.checkbox("Include numbers")
                
            if st.button("Generate Names", type="primary"):
                with st.spinner("Generating domain suggestions..."):
                    initial_results = self.crew.process_domain_request(
                        f"{domain_type} in {industry} industry"
                    )
                    print("initial results are " + str(initial_results))
                    st.session_state.initial_names = initial_results['initial_names']
                    st.session_state.stage = 'selection'

    def render_selection_stage(self):
        st.markdown("### Select Your Preferred Names")
        
        if 'initial_names' in st.session_state:
            cols = st.columns(2)
            
            for idx, name in enumerate(st.session_state.initial_names):
                with cols[idx % 2]:
                    st.markdown(f"""
                    <div class="highlight">
                        <h4>{name}</h4>
                        <p style="color: gray; font-size: 14px;">Length: {len(name)} characters</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.checkbox(f"Select {name}", key=f"select_{name}"):
                        if name not in st.session_state.selected_names:
                            st.session_state.selected_names.append(name)
            
            st.markdown("---")
            st.markdown("### Selected Names")
            st.markdown(", ".join(st.session_state.selected_names) if st.session_state.selected_names else "No names selected yet")
            
            if len(st.session_state.selected_names) >= 2 and st.button("Proceed with Analysis", type="primary"):
                with st.spinner("Analyzing selected domains..."):
                    final_results = self.crew.process_domain_request(
                        "domain analysis",
                        st.session_state.selected_names
                    )
                    st.session_state.final_results = final_results
                    st.session_state.stage = 'analysis'

    def render_analysis_stage(self):
        if not st.session_state.final_results:
            st.error("No analysis results available")
            return

        st.markdown("### Analysis Results")
        
        # Available Domains Section
        st.subheader("🌐 Available Domains")
        available_domains = st.session_state.final_results['available_domains']
        if available_domains:
            for domain in available_domains:
                st.markdown(f"""
                <div class="highlight">
                    <h4>{domain}</h4>
                    <p style="color: green;">✓ Available</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No available domains found")

        # Market Research Section
        st.subheader("📊 Market Research")
        for domain, research in st.session_state.final_results['market_research'].items():
            with st.expander(f"Research for {domain}"):
                st.markdown(research['raw_analysis'])

        # Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Start Over"):
                st.session_state.clear()
                st.experimental_rerun()
        with col2:
            if st.button("Export Results"):
                # Create timestamp for filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Convert results to DataFrame
                results_df = pd.DataFrame({
                    'Domain': available_domains,
                    'Status': ['Available'] * len(available_domains),
                    'Research': [st.session_state.final_results['market_research'].get(domain, {}).get('raw_analysis', '') 
                               for domain in available_domains]
                })
                # Create download button
                st.download_button(
                    label="Download CSV",
                    data=results_df.to_csv(index=False),
                    file_name=f'domain_research_{timestamp}.csv',
                    mime='text/csv'
                )

    def run(self):
        self.render_header()
        self.render_progress()
        
        if st.session_state.stage == 'input':
            self.render_input_stage()
        elif st.session_state.stage == 'selection':
            self.render_selection_stage()
        elif st.session_state.stage == 'analysis':
            self.render_analysis_stage()

if __name__ == "__main__":
    app = DomainResearchUI()
    app.run()