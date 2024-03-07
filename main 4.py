import pandas as pd
import os
import streamlit as st
import pickle
import time
import pickle
from streamlit_chat import message as st_message
import openai
import json
import pandas as pd
pd.set_option('display.max_columns', None)

# Initialize the chat_history in the session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'history' not in st.session_state:
    st.session_state.history = []
if 'msg_history' not in st.session_state:
    st.session_state.msg_history = []

# Load the JSON file
with open('config.json', 'r') as file:
    data = json.load(file)
 
# Access the credentials
openai.api_key = data["api_key"]
openai.api_type = data['api_type']
openai.api_base = data['api_base']
openai.api_version = data['api_version']

os.environ['OPENAI_API_KEY'] = data["api_key"]
os.environ['OPENAI_API_BASE'] = data['api_base']
os.environ['OPENAI_API_TYPE'] = data['api_type']
os.environ['OPENAI_API_VERSION'] = data['api_version']
 
# Step 1: Read Data using Pandas
folder_path = r"C:\Users\SrinidhiJala\Downloads\Book 6 (1).xlsx"  # Update with your file path


def extract_text_from_folder(folder_path):
    df = pd.read_excel(folder_path)
    # Loop through columns and apply changes in the headers
    current_month = None
    for col in df.columns:
        if not col.startswith('Unnamed:'):
            current_month = col
        elif current_month:
            df.rename(columns={col: f'{current_month}_{col.split(":")[-1]}'}, inplace=True)

    # Modify the headers by combining with the first row values
    for col in df.columns:
        if col != 'EmployeeId':
            header_value = df[col].iloc[0]
            if pd.isna(header_value):
                df[col] = df[col].fillna(method='ffill')  # Fill NaN with the previous non-NaN value
                header_value = df[col].iloc[0]
            df.rename(columns={col: f"{col}-{header_value}"}, inplace=True)

    # Modify the headers
    prev_part = None
    prev_nan_part = None
    for col in df.columns:
        try:
            part1, part2 = col.split('-')
        except ValueError:
            continue  # Skip columns that do not contain '-'

        if part1.startswith('Unnamed'):
            part1 = prev_part
        else:
            prev_part = part1

        if part2 == 'nan':
            part2 = prev_nan_part
        else:
            prev_nan_part = part2

        df.rename(columns={col: f"{part1}-{part2}"}, inplace=True)

    df.drop(0, inplace = True)

    # Drop the first row as it has been used to modify the headers

    # Create a dictionary to store the new column names
    new_column_names = {}

    # Iterate over the columns and modify the headers
    for col in df.columns:
        new_column_names[col] = f"{col}-{df.iloc[0][col]}"

    # Rename the columns using the dictionary
    df.rename(columns=new_column_names, inplace=True)
    df.rename(columns={"EmployeeId-nan": "EmployeeId"}, inplace=True)
    df['EmployeeId'].fillna(0, inplace=True)
    df['EmployeeId'] = df['EmployeeId'].astype('int64')



    # Assuming df is your DataFrame containing the columns mentioned in your question

    # Split the column headers by hyphen
    split_headers = df.columns.str.split('-', n=1)

    # Store the second part followed by hyphen in a variable
    second_parts = []

    # Store the first part of the headers in a separate list
    first_parts = []

    # Process each header separately
    for part in split_headers:
        # If the header contains a hyphen, store the second part
        if len(part) > 1:
            second_parts.append(part[1])
            first_parts.append(part[0].rsplit('_', 1)[0])  # Extract the first part without numbers
        else:
            # If the header doesn't contain a hyphen, check if it's 'EmployeeId-nan'
            if part[0] == 'EmployeeId-nan':
                first_parts.append('EmployeeId')
                second_parts.append('nan')
            else:
                first_parts.append(part[0])
                second_parts.append('')

    # Combine first and second parts to form the final headers
    final_headers = [first + '-' + second if second else first for first, second in zip(first_parts, second_parts)]

    # Replace the original headers with the new headers
    df.columns = final_headers
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(' ', '_')
    for column in df.columns:
        df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
    df = df.drop(df.index[0])
    return df


def convert_to_query(query):
    msgs = []

    delimiter = "####"

    user_content = f''' User Query: {delimiter} {query} {delimiter}


You have access to a relational database table. Your task is to write SQL queries to retrieve specific information from the table based on User Query.
You have extensive expertise across a wide range of SQL topics. "When using functions like MAX(), ensure that the data types of the columns being compared are compatible. If necessary, explicitly cast columns to compatible data types using functions like CAST() or CONVERT()."
Do not answer questions which are not related to Employee_Build_Data.

&&&&

Table Name: Employee_Build_Data

&&&&

Table columns: 

'EmployeeId', 'Jan-Week_1-Build', 'Jan-Week_1-No_Build', 'Jan-Week_2-Build', 'Jan-Week_2-No_Build', 'Jan-Week_3-Build', 'Jan-Week_3-No_Build', 'Jan-Week_4-Build', 'Jan-Week_4-No_Build', 'Feb-Week_1-Build', 'Feb-Week_1-No_Build', 'Feb-Week_2-Build', 'Feb-Week_2-No_Build', 'Feb-Week_3-Build', 'Feb-Week_3-No_Build', 'Feb-Week_4-Build', 'Feb-Week_4-No_Build', 'Feb-Week_5-Build', 'Feb-Week_5-No_Build', 'Mar-Week_1-Build', 'Mar-Week_1-No_Build', 'Mar-Week_2-Build', 'Mar-Week_2-No_Build', 'Mar-Week_3-Build', 'Mar-Week_3-No_Build', 'Mar-Week_4-Build', 'Mar-Week_4-No_Build', 'Mar-Week_5-Build', 'Mar-Week_5-No_Build', 'Apr-Week_1-Build', 'Apr-Week_1-No_Build', 'Apr-Week_2-Build', 'Apr-Week_2-No_Build', 'Apr-Week_3-Build', 'Apr-Week_3-No_Build', 'Apr-Week_4-Build', 'Apr-Week_4-No_Build', 'Apr-Week_5-Build', 'Apr-Week_5-No_Build', 'May-Week_1-Build', 'May-Week_1-No_Build', 'May-Week_2-Build', 'May-Week_2-No_Build', 'May-Week_3-Build', 'May-Week_3-No_Build', 'May-Week_4-Build', 'May-Week_4-No_Build', 'June-Week_1-Build', 'June-Week_1-No_Build', 'June-Week_2-Build', 'June-Week_2-No_Build', 'June-Week_3-Build', 'June-Week_3-No_Build', 'June-Week_4-Build', 'June-Week_4-No_Build', 'June-Week_5-Build', 'June-Week_5-No_Build', 'July-Week_1-Build', 'July-Week_1-No_Build', 'July-Week_2-Build', 'July-Week_2-No_Build', 'July-Week_3-Build', 'July-Week_3-No_Build', 'July-Week_4-Build', 'July-Week_4-No_Build', 'July-Week_5-Build', 'July-Week_5-No_Build', 'Aug-Week_1-Build', 'Aug-Week_1-No_Build', 'Aug-Week_2-Build', 'Aug-Week_2-No_Build', 'Aug-Week_3-Build', 'Aug-Week_3-No_Build', 'Aug-Week_4-Build', 'Aug-Week_4-No_Build', 'Aug-Week_5-Build', 'Aug-Week_5-No_Build', 'Sep-Week_1-Build', 'Sep-Week_1-No_Build', 'Sep-Week_2-Build', 'Sep-Week_2-No_Build', 'Sep-Week_3-Build', 'Sep-Week_3-No_Build', 'Sep-Week_4-Build', 'Sep-Week_4-No_Build', 'Sep-Week_5-Build', 'Sep-Week_5-No_Build', 'Oct-Week_1-Build', 'Oct-Week_1-No_Build', 'Oct-Week_2-Build', 'Oct-Week_2-No_Build', 'Oct-Week_3-Build', 'Oct-Week_3-No_Build', 'Oct-Week_4-Build', 'Oct-Week_4-No_Build', 'Oct-Week_5-Build', 'Oct-Week_5-No_Build', 'Nov-Week_1-Build', 'Nov-Week_1-No_Build', 'Nov-Week_2-Build', 'Nov-Week_2-No_Build', 'Nov-Week_3-Build', 'Nov-Week_3-No_Build', 'Nov-Week_4-Build', 'Nov-Week_4-No_Build', 'Nov-Week_5-Build', 'Nov-Week_5-No_Build', 'Dec-Week_1-Build', 'Dec-Week_1-No_Build', 'Dec-Week_2-Build', 'Dec-Week_2-No_Build', 'Dec-Week_3-Build', 'Dec-Week_3-No_Build', 'Dec-Week_4-Build', 'Dec-Week_4-No_Build';

&&&&
Table columns description:

    EmployeeId: Represents the unique identifier for each employee.

    For each month of the year, the dataset includes columns indicating whether the employee performed specific tasks or activities ("Build") or did not perform them ("No Build") during each week of the month:

    Jan-Week_1-Build: Indicates whether the employee performed certain tasks during the first week of January.
    Jan-Week_1-No_Build: Indicates whether the employee did not perform certain tasks during the first week of January.
    Jan-Week_2-Build: Indicates whether the employee performed certain tasks during the second week of January.
    Jan-Week_2-No_Build: Indicates whether the employee did not perform certain tasks during the second week of January.
    Jan-Week_3-Build: Indicates whether the employee performed certain tasks during the third week of January.
    Jan-Week_3-No_Build: Indicates whether the employee did not perform certain tasks during the third week of January.
    Jan-Week_4-Build: Indicates whether the employee performed certain tasks during the fourth week of January.
    Jan-Week_4-No_Build: Indicates whether the employee did not perform certain tasks during the fourth week of January.
    Feb-Week_1-Build: Indicates whether the employee performed certain tasks during the first week of February.
    Feb-Week_1-No_Build: Indicates whether the employee did not perform certain tasks during the first week of February.
    ... (and so on for the remaining months and weeks of the year)
Each "Build" or "No Build" column pair represents the presence or absence of specific tasks or activities for the corresponding week within each month of the year.
When referencing column headers like 'Jan-Week_1-Build', ensure to follow this format:
- The header consists of the month abbreviation ('Jan' for January).
- The hyphen separates the month abbreviation from the week number ('Week_1').
- Finally, the purpose of the column is indicated ('Build').

Here's an example breakdown:
- 'Jan': Abbreviation for January.
- 'Week_1': Indicates the first week of the month.
- 'Build': Specifies the purpose of the column (e.g., construction activities).

Please make sure to reference column headers accurately in your queries.
"You must consider the original column names when generating alias names. The alias should reflect the content or purpose of the column."


&&&&

Datatype of columns : Int64

#####


Here are the key guidelines for your conduct:

1. Understand the user's natural language query provided. Identify the essential components such as entities, attributes, conditions, and actions mentioned within the query.

2. Develop the SQL query that aligns with the user's natural language query and the structure of the database table provided.

3. Ensure that the SQL query accurately reflects the user's requirements and retrieves the relevant information from the database table.

4."Provide only the SQL query, please don't provide any additional text."

5. Use the exact column names mentioned, do not make any changes to the column names.

6. "Please ensure that you only reference data tables and not system tables like INFORMATION_SCHEMA, etc"

7. "Please enclose column names in inverted commas"

8. Please ensure that your query is compatible with DuckDB

9. When structuring queries, remember to interpret column names accurately to represent the intended data.

10. Identify the data types of the columns involved in your SQL queries. Use explicit type casting functions (e.g., CAST(), CONVERT()) to convert data from one type to another if necessary.

11. Familiarize yourself with the syntax and requirements of SQL functions supported by your database management system (DBMS)

12. When using functions like MAX(), ensure that the data types of the columns being compared are compatible. If necessary, explicitly cast columns to compatible data types using functions like CAST() or CONVERT().

13. "verify the data types of columns being used in SQL functions like MAX, MIN, SUM, etc., and ensure compatibility among them. You must be aware of potential data type mismatches that might occur in SQL queries."

14. "You must consider the original column names when generating alias names. The alias should reflect the content or purpose of the column."

&&&&

Examples:

&&&&

1) User Query: "Please generate an SQL query to retrieve the 'Build' values for the first week of January for employee ID 1115."

   SQL Query: SELECT "Jan-Week_1-Build" FROM Employee_Build_Data WHERE EmployeeId = 1115

---------


2) User Query: "What is the average number of "Build" occurrences per week for EmployeeId 520?"

   SQL Query: SELECT 
            CAST((
                SUM("Feb-Week 1-Build") +
                SUM("Feb-Week 2-Build") +
                SUM("Feb-Week 3-Build") +
                SUM("Feb-Week 4-Build") +
                SUM("Feb-Week 5-Build")
            ) AS DECIMAL) / 5 AS Average_Build_Per_Week
            FROM 
                Employee_Build_Data
            WHERE 
                EmployeeId = 520

3) User Query: What is the SQL query to retrieve all build values for all employee IDs in the first week of January from the given dataset?

    SQL Query:     SELECT "Jan-Week_1-Build" 
                   FROM Employee_Build_Data 
                   WHERE "Jan-Week_1-Build" IS NOT NULL


            '''
    msgs.append({"role" : "system", "content" : user_content })
    response = openai.ChatCompletion.create(temperature=0, engine="gptturboekademo", messages=msgs)

    return response.choices[0]['message']['content']
import duckdb
def process_message():
    context = ""
    user_message = st.session_state.input_text  # Get the user input from session state

    # Check if user_message is empty
    if not user_message:
        return

    """
    Function triggered on user input or pressing Enter.
    """
    with st.spinner("Thinking..."):
        # context = related_docs(user_message)
        
        # Convert user message to SQL query
        sql_query = convert_to_query(user_message)
        # st.write("query  &&&&&", sql_query, "&&&&")
        if ":" in sql_query:
            split_result = sql_query.rsplit(":", 1)
            sql_query = split_result[1]  
        st.write(sql_query)
        if sql_query.strip().upper().startswith("SELECT"):
            # Execute the SQL query and assign the result to context
          
            context = duckdb.query(sql_query).df()
            st.write("context", context)
            # Pass the SQL query to the chat method
            message_bot = chat(user_message, context, messages=[])  # Generate chatbot response based on input and context

            # Append the user and bot messages to the message history
            st.session_state.msg_history.append({"message": user_message, "is_user": True})
            st.session_state.msg_history.append({"message": message_bot, "is_user": False})
            # Clear the input text after processing the message
            st.session_state.input_text = ""
        else:
            message_bot = "Please ask a valid question"
            st.session_state.msg_history.append({"message": user_message, "is_user": True})
            st.session_state.msg_history.append({"message": message_bot, "is_user": False})
            st.session_state.input_text = ""



messages = []
def chat(query, doc, messages):
    # st.session_state.history
    delimiter = "####"
    # st.write(doc)
    # Append user input to history
    user_content = f''' context : 
                {delimiter} {doc} {delimiter} 

                "Extract answers only from the context".
                "Read out the value present at each cell, providing a comprehensive overview of the data."
                Construct sentences or sets of sentences for each row to describe the entity or observation.


            '''
    st.session_state.history.append({"role" : "system", "content" : '''The given context is a dataframe. Your goal is to transform a DataFrame into natural language sentences that effectively communicate the information contained in the data.
                                     Provide concise and straightforward responses that communicate the essential information without referencing DataFrame structure or column names, number of rows and columns etc.
                                    "Read out the value present at each cell, providing a comprehensive overview of the data."

                                     &&&&
                                     INSTRUCTIONS: 
                                    - Transform the DataFrame into natural language sentences that effectively communicate the information contained in the data.
                                    - Ensure the DataFrame has meaningful column names and organized data.
                                    - Treat each row as a unique entity or observation.
                                    - "Iterate through each row of the DataFrame."
                                    - "Construct sentences or sets of sentences for each row to describe the entity or observation."
                                    - Use appropriate grammar, language, and context for coherent and human-readable sentences.
                                    - Interpret even a single cell in the DataFrame as an observation or entity to be described in natural language sentences.
                                    - Avoid speculating about the meaning or context of the data; focus on presenting the available information in the DataFrame.
                                    - Omit mentioning the number of rows, columns, or any other structural details of the DataFrame unless explicitly requested.

                                    '''})
 
    st.session_state.history.append({"role" : "user", "content" : user_content})

    response = openai.ChatCompletion.create(temperature=0, engine="gptturboekademo", messages=st.session_state.history)
    user_content_escaped = user_content.replace('"', r'\"').replace('\n', r'\n')

    # Store only the response in the history
    st.session_state.history.append({"role": "assistant", "content": response.choices[0]['message']['content']})

    # Limit history to the last two elements
    if len(st.session_state.history) >= 5:
        st.session_state.history = st.session_state.history[-4:]
    if len(messages) >= 5:
        messages = messages[-4:]
    return response.choices[0]['message']['content']


# extracted_text = extract_text_from_folder(folder_path)

# save_docs(extracted_text)

st.title("Chatbot")

df = extract_text_from_folder(folder_path)
csv_file_path = 'Employee_Build_Data.csv'

df.to_csv(csv_file_path, index=False)
Employee_Build_Data = pd.read_csv(csv_file_path)


# Display conversation using columns
for i, j in enumerate(st.session_state.msg_history):
    st_message(**j, key=str(i))  # Unpack and display each message
    

user_message = st.text_input(
    "Talk to the bot",
    key="input_text",
    on_change=process_message,
)

# Check if user_message is empty
if not user_message:
    st.stop()


# # save_docs(extracted_text)

# Display conversation using columns
for i, j in enumerate(st.session_state.msg_history):
    st_message(**j, key=str(i))  # Unpack and display each message

# Streamlit UI components
user_message = st.text_input(
    "Talk to the bot",
    key="input_text",
    on_change=process_message,
)

# Check if user_message is empty
if not user_message:
    st.stop()







# // {"api_key" : "9deacc49f07c458db4c62c74f0821110",
# // "api_type" : "azure",
# // "api_base" : "https://openaiut.openai.azure.com/",
# // "api_version" : "2023-05-15" } 
