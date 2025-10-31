"""
Microsoft AutoGen Multi-Agent System with RAG for report generation
"""

import autogen
from config import OPENAI_API_KEY
from rag_retrieval import retrieve_combined_data, retrieve_sales_data, retrieve_marketing_data

# Below LLM Configuration will be used in Agent
def create_autogen_config():
    """Create AutoGen LLM configuration"""
    config_list = [
        {
            "model": "gpt-4.1-nano",
            "api_key": OPENAI_API_KEY,
        }
    ]

    llm_config = {
        "config_list": config_list,
        "temperature": 0.7, # For Randomness
        "timeout": 120, # time (in seconds) take AI model to respond
        "cache_seed": None # It won't use old result
    }

    return llm_config

# Creating Agent for Data Analysis
def create_data_analyst_agent():
    """Create a Data Analyst Agent that analyzes data"""
    
    system_message = """You are a Senior Data Analyst specializing in sales and marketing analytics.

Your responsibilities:
1. Analyze sales and marketing data provided to you
2. Identify trends, patterns, and anomalies
3. Calculate key metrics and KPIs
4. Provide data-driven insights
5. Be precise and analytical in your findings

You receive context from a RAG system containing real sales and marketing data.
Base all your analysis on this retrieved context."""
    
    analyst = autogen.AssistantAgent(
        name="data_analyst",
        system_message=system_message,
        llm_config=create_autogen_config(),
    )
    # it return analyst Agent for Data Analysis
    return analyst


# This Agent will create a Report based on Data Analysis
def create_report_writer_agent():
    """Create a Report Writer Agent that creates professional reports"""
    
    system_message = """You are a Professional Report Writer specialized in business reporting.

Your responsibilities:
1. Take analytical findings and create comprehensive reports
2. Structure reports with clear sections (Executive Summary, Key Findings, etc.)
3. Write in a professional, clear, and engaging manner
4. Provide actionable recommendations
5. Format reports properly with bullet points and sections

Create reports that executives can easily understand and act upon."""
    
    writer = autogen.AssistantAgent(
        name="report_writer",
        system_message=system_message,
        llm_config=create_autogen_config(),
    )
    
    return writer

# creates a User Proxy Agent, which acts as a bridge (middleman) between the human user (you) and other AI agents in an AutoGen system.
# This User Proxy Agent will be used to call other two agents based on needs.
def create_user_proxy():
    """Create a User Proxy Agent"""
    
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER", # Means the agent never asks for manual user input during conversations.So it runs automatically without waiting for you to type.
        max_consecutive_auto_reply=0, # Prevents it from automatically sending multiple replies in a row. It will only respond when triggered
        code_execution_config=False, # Disables any code execution. So this agent won’t try to run Python code or scripts.
        default_auto_reply="", # Sets the default reply to empty (no automatic response)
    )
    
    return user_proxy


# This function automates a data analysis + report generation process.
# query: what you want to analyze (e.g. “monthly sales trends”)
# report_type → choose "sales", "marketing", or "combined"
# n_results → how many pieces of data to retrieve (default = 8)
def generate_report_with_autogen_multiagent(query, report_type="combined", n_results=8):
    """Generate report using multi-agent AutoGen system with RAG"""
    
    print("\n[AutoGen] Starting Multi-Agent Analysis...")
    
    # Step 1: Retrieve relevant context using RAG
    if report_type == "sales":
        context = retrieve_sales_data(query, n_results=n_results)
    elif report_type == "marketing":
        context = retrieve_marketing_data(query, n_results=n_results)
    else:
        context = retrieve_combined_data(query, n_results=n_results)
    
    # Step 2: Create agents
    # analyst → analyzes data
    # writer → writes the report
    # user_proxy → acts as the go-between for communication
    analyst = create_data_analyst_agent()
    writer = create_report_writer_agent()
    user_proxy = create_user_proxy()
    
    # Step 3: First, have analyst analyze the data
    analysis_prompt = f"""Based on the following data retrieved from our database, please analyze and identify key insights:

Query: {query}

{context}

Please provide:
1. Key metrics and numbers
2. Notable trends
3. Top performers
4. Areas of concern
5. Data-driven insights"""
    
    print("[AutoGen] Agent 1 (Data Analyst) - Analyzing data...")
    
    # Analyst analyzes the data.
    # The user proxy starts a chat with the analyst agent and sends the analysis prompt.
    # max_turns=1 → means only 1 exchange happens (no long back-and-forth)
    user_proxy.initiate_chat(
        analyst,
        message=analysis_prompt,
        max_turns=1
    )
    
    # Get analyst's findings
    # Retrieves the final message (response) from the analyst agent — the analysis results.
    analyst_findings = user_proxy.last_message(analyst)["content"]
    
    # Step 4: Have writer create comprehensive report from analyst's findings
    report_prompt = f"""Based on the data analyst's findings, create a comprehensive professional report.

Original Query: {query}

Data Analyst's Findings:
{analyst_findings}

Create a detailed report with these sections:
1. Executive Summary
2. Key Findings  
3. Detailed Analysis
4. Insights and Trends
5. Recommendations

Make it professional, clear, and actionable."""
    
    print("[AutoGen] Agent 2 (Report Writer) - Creating report...")
    
    # Writer creates the report
    # The user proxy now talks to the writer agent, giving it the analyst’s findings to convert into a well-formatted report.
    # max_turns=1 → means only 1 exchange happens (no long back-and-forth)
    user_proxy.initiate_chat(
        writer,
        message=report_prompt,
        max_turns=1
    )
    
    # Get final report
    final_report = user_proxy.last_message(writer)["content"]
    
    print("[AutoGen] Multi-Agent Report Generation Complete!\n")
    
    # Returns the completed report text
    return final_report


# This function doesn’t do any new work.
# It just redirects the call to your newer function.
# If anyone still calls the old function name, just run the new one instead
def generate_report_with_rag(query, report_type="combined", n_results=5):
    """Wrapper function for backward compatibility"""
    return generate_report_with_autogen_multiagent(query, report_type, n_results)


# You provide the full question + context yourself, and it returns the AI’s answer — no RAG fetching, no writer agent involved.
# prompt_with_context → This is a full text prompt that already includes the question and data/context the agent should analyze.
def generate_custom_report(prompt_with_context):
    """Generate custom report with pre-formatted prompt"""
    analyst = create_data_analyst_agent()
    user_proxy = create_user_proxy()
    
    user_proxy.initiate_chat(analyst, message=prompt_with_context, max_turns=1)
    return user_proxy.last_message()["content"]


if __name__ == "__main__": # --> Means Only run the following code if this file is executed directly (not imported as a module)
    # Test the multi-agent system
    if OPENAI_API_KEY:
        print("="*80)
        print("Testing Microsoft AutoGen Multi-Agent System with RAG")
        print("="*80)
        
        query = "Analyze the top performing products and their sales trends"
        report = generate_report_with_autogen_multiagent(query, report_type="sales", n_results=5)
        
        print("\n" + "="*80)
        print("FINAL REPORT:")
        print("="*80)
        print(report)
    else:
        print("Please set OPENAI_API_KEY in your .env file")