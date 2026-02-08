import streamlit as st
import os, requests, json
import sys
import tempfile
from pathlib import Path
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# ===== Setup Environment for CrewAI =====
def setup_crewai_environment():
    """Setup proper environment for CrewAI to work on Hugging Face Spaces"""
    # Create a directory structure where we have write permissions
    base_dir = Path("/tmp/crewai_app")
    base_dir.mkdir(exist_ok=True, parents=True)
    
    # Create .mem0 directory specifically
    mem0_dir = base_dir / ".mem0"
    mem0_dir.mkdir(exist_ok=True)
    
    # Set multiple environment variables to ensure all libraries use our directory
    os.environ["HOME"] = str(base_dir)
    os.environ["TMPDIR"] = str(base_dir)
    os.environ["TEMP"] = str(base_dir)
    os.environ["TMP"] = str(base_dir)
    os.environ["CREWAI_DATADIR"] = str(base_dir)
    
    return base_dir

# Initialize the environment
data_dir = setup_crewai_environment()

# Now we can safely import CrewAI tools
print("Attempting to import CrewAI tools...")
try:
    from crewai_tools import SerperDevTool
    print("✅ CrewAI tools imported successfully")
except Exception as e:
    print(f"❌ Import error: {str(e)}")
    print("Check the app logs for details")
    import traceback
    print(traceback.format_exc())

# LLM and SERPER Tool And API Setup


gpt_four_point_one_llm = LLM(model="gpt-4.1-2025-04-14",
                             stream=True, 
                             api_key=os.environ.get("OPENAI_API_KEY"))

gpt_four_o_llm = LLM(model="gpt-4o-2024-08-06",
                     stream=True, 
                     api_key=os.environ.get("OPENAI_API_KEY"))

claude_sonnet_four_llm = LLM(model="claude-sonnet-4-20250514",
                         stream=True, 
                         api_key=os.environ.get("ANTHROPIC_API_KEY"))

SERPER_API_KEY = os.environ.get("SERPER_API_KEY")
    
@CrewBase
class CrewaiEnterpriseArticleWritingCrew:
    """CrewaiEnterpriseArticleWriting crew"""

    agents_config = "agents.yaml"
    tasks_config = "tasks.yaml"
  
    @agent
    def planner(self) -> Agent:
        return Agent(
            llm = gpt_four_point_one_llm,
            config=self.agents_config["planner"],
            tools=[SerperDevTool(n=10)],
            verbose=True,
        )

    @agent
    def writer(self) -> Agent:
        return Agent(llm = claude_sonnet_four_llm,config=self.agents_config["writer"], verbose=True)
    
    @agent
    def editor(self) -> Agent:
        return Agent(llm = gpt_four_o_llm,config=self.agents_config["editor"], verbose=True)

    @task
    def plan(self) -> Task:
        return Task(
            config=self.tasks_config["plan"]
        )

    @task
    def write(self) -> Task:
        return Task(
            config=self.tasks_config["write"]
        )
    
    @task
    def edit(self) -> Task:
        return Task(
            config=self.tasks_config["edit"]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CrewaiEnterpriseArticleWriting crew"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
        
# Streamlit page config
st.set_page_config(
    page_title="Content Researcher And Writer - Multi-Agent Crew",
    page_icon="🚀",
    layout="wide",  # Can be "centered" or "wide"
    )

# Title and description
st.title("Researcher And Writer Crew AI Agent")
st.markdown("Generate articles about any topic using Crew AI Agents")

# sidebar
with st.sidebar:
    st.sidebar.header("Content Settings")

    # Make the text input take up more space
    topic = st.text_area("Enter your topic",height=100,placeholder='Enter the topic')

    # Add more sidebar controls if needed 
    st.markdown("### LLM Settings")
    temperature = st.slider("Temperature",0.0,1.0,0.7)

    # Add some spacing
    st.markdown("___")

    # Make the generate button more prominent in the sidebar 
    generate_button = st.button("Generate Content", type="primary", use_container_width=True)

    # Add some helpful information
    with st.expander("How to use"):
        st.markdown("""
        1. Enter your favorite topic.
        2. Play with the temperature.
        3. Click 'Generate Content' to start
        4. Wait for the AI to generate your article
        5. Download the result as the markdown file
        """)

# Main Content Area
if generate_button:
    with st.spinner('Generating content... This may take a moment.'):
        try:
            result = CrewaiEnterpriseArticleWritingCrew().crew().kickoff(inputs={"topic": topic})  # Executes the crew according to the defined flow.
            st.markdown(result)

            # Add download button
            st.download_button(label="Download Content",data=result.raw,file_name=f"{topic.lower().replace(' ','_')}_article.md",mime="text/markdown")
        except Exception as e:
            st.error(f"An error occured: {str(e)}")

st.markdown("___") # Set the footer
st.markdown("Built with CrewAI Agentic AI Framework, Streamlit, and GPT and Claude LLM Models")           