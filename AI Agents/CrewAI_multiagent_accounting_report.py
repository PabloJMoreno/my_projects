import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from typing import List, Dict
import pyodbc

# load environment variables and OpenAI API key
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

# setup connection to Peachtree accounting software
def extract_peachtree_data(criteria: str) -> List[Dict]:
    """
    Extracts data from Peachtree accounting software.

    Args:
        criteria (str): A string that can determine what type of data you need (e.g., "last_month_transactions", "customer_balances").

    Returns:
        List[Dict]: A list of dictionaries, where each dictionary represents a record.
    """

    print(f"Extracting Peachtree data with criteria: {criteria}...")

    conn_str = (
        r"Driver={Sage Peachtree ODBC Driver};"
        r"Company=<your_peachtree_company_path>;"  # Replace with your actual path
        r"UID=<your_username>;"  # Replace with your username
        r"PWD=<your_password>;"  # Replace with your password
    )

    try:
        cnxn = pyodbc.connect(conn_str)
        cursor = cnxn.cursor()

        if criteria == "last_month_transactions":
            sql_query = """
                SELECT 
                    Date,
                    Account,
                    Amount,
                    Type
                FROM
                    GeneralLedger
                 WHERE
                     Date >= date('now','start of month','-1 month') AND
                    Date < date('now','start of month')
            """
            cursor.execute(sql_query)
            columns = [column[0] for column in cursor.description]  # Get column names
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        elif criteria == "customer_balances":
            sql_query = """
                SELECT 
                    CustomerID,
                    Balance
                FROM
                    Customers
            """
            cursor.execute(sql_query)
            columns = [column[0] for column in cursor.description]  # Get column names
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        else:
            results = []
            print("Unknown Criteria. Please verify.")


        cnxn.close()
        print("Data extraction from Peachtree complete.\n")
        return results
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        print(f"Error during data extraction: {sqlstate}")
        return []

# 1. Setup Agents
data_extractor_agent = Agent(
    role="Peachtree Data Extractor",
    goal="Extract necessary accounting data from Peachtree software based on given criteria.",
    backstory="I am an expert at connecting to and querying Peachtree accounting software, skilled in retrieving specific data.",
    verbose=True,
    allow_delegation=False,
)

data_analyst_agent = Agent(
    role="Accounting Data Analyst",
    goal="Analyze the extracted accounting data to identify key trends and insights.",
    backstory="I am a seasoned accounting analyst with a keen eye for detail and the ability to turn raw data into meaningful analysis.",
    verbose=True,
    allow_delegation=True,
)

report_writer_agent = Agent(
    role="Accounting Report Writer",
    goal="Create a concise and informative accounting report based on the provided analysis.",
    backstory="I am an expert in financial report writing, skilled in presenting complex information in an easily understandable format.",
    verbose=True,
    allow_delegation=False,
)


# 2. Setup Tasks
extract_data_task = Task(
    description="Extract the last month's transactions and customer balances data from the Peachtree software. Use the specified function.",
    agent=data_extractor_agent,
    process=Process.sequential,
    expected_output="List of transaction dictionaries and customer balance dictionaries",
)

analyze_data_task = Task(
    description="Analyze the extracted accounting data. Focus on the last month's transactions and customer balances, identify trends and write a summary of findings.",
    agent=data_analyst_agent,
    process=Process.sequential,
    expected_output="Summary of accounting data analysis including key trends.",
)

write_report_task = Task(
    description="Create a short accounting report based on the provided analysis. The report should include the key findings from the analysis and should be easily understood by people not specialized in accounting.",
    agent=report_writer_agent,
    process=Process.sequential,
    expected_output="Concise accounting report.",
)

# 3. Define Data Extraction Task and provide the extract_peachtree_data function
class DataExtractionTask(Task):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def execute(self, tool_args={}) -> str:
        """Execute the task using the extract_peachtree_data function and return the result."""
        criteria = tool_args.get("criteria", "last_month_transactions")
        # criteria = self.description.split("from the Peachtree software.")[-1].split(" ")[1:] # this allows to extract the criteria from the description
        
        data = extract_peachtree_data(criteria)
        return str(data)

extract_data_task = DataExtractionTask(
    description="Extract the last month's transactions and customer balances data from the Peachtree software.",
    agent=data_extractor_agent,
    process=Process.sequential,
    expected_output="List of transaction dictionaries and customer balance dictionaries",
)


# 4. Create Crew
accounting_crew = Crew(
    agents=[
        data_extractor_agent,
        data_analyst_agent,
        report_writer_agent,
    ],
    tasks=[
        extract_data_task,
        analyze_data_task,
        write_report_task,
    ],
    process=Process.sequential
)


# 5. Run Crew
if __name__ == "__main__":
    report = accounting_crew.kickoff()
    print("\n\n======= ACCOUNTING REPORT =======\n")
    print(report)
    print("\n\n======= END OF REPORT =======\n")