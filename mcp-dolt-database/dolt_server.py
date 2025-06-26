import requests
import json
import csv
import io
from fastmcp import FastMCP, Client

mcp = FastMCP("Dolt Database Explorer")

# Configuration constants
DOLT_API_URL = "https://www.dolthub.com/api/v1alpha1"

def parse_database_string(db_string: str):
    """
    Parse database string in format owner/database/branch
    Returns tuple (owner, name, branch)
    """
    parts = db_string.split('/')
    if len(parts) != 3:
        raise ValueError(f"Invalid database format '{db_string}'. Expected owner/database/branch")
    
    owner, name, branch = parts
    if not owner or not name or not branch:
        raise ValueError("Database owner, name, and branch cannot be empty.")
    
    return owner, name, branch

def get_dolt_query_url(db_string: str):
    """
    Get the URL for executing SQL queries against the Dolt database
    """
    owner, name, branch = parse_database_string(db_string)
    return f"{DOLT_API_URL}/{owner}/{name}/{branch}"

@mcp.resource("schema://main")
def get_schema() -> str:
    """
    Provide the database schema as a resource - uses default database
    """
    # For the resource, we'll use the default database connection
    # This is a limitation since resources can't take parameters
    return "Schema resource requires database connection. Use describe_table tool instead."

@mcp.tool()
def read_query(sql: str, db_string: str) -> str:
    """
    Execute SQL read queries safely on the Dolt database
    """
    try:
        response = requests.get(
            get_dolt_query_url(db_string),
            params={"q": sql}
        )
        response.raise_for_status()
        result = response.json()

        if "rows" not in result or not result["rows"]:
            return "No data returned or query doesn't return rows."

        columns = result.get("schema", [])
        column_names = [col.get("columnName", f"Column{i}") for i, col in enumerate(columns)]

        output = [" | ".join(column_names)]
        output.append("-" * len(" | ".join(column_names)))

        for row in result["rows"]:
            row_values = []
            for col_name in column_names:
                val = row.get(col_name)
                row_values.append(str(val) if val is not None else "NULL")
            output.append(" | ".join(row_values))

        return "\n".join(output)
    except Exception as e:
        return f"Error executing query: {str(e)}"

@mcp.tool()
def write_query(sql: str, api_token: str, db_string: str) -> str:
    """
    Execute write operations (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, RENAME) on the Dolt database.
    Handles polling for asynchronous operations.
    """
    try:
        if not api_token:
            return "Error: API token is required for write operations."
        
        sql_upper = sql.upper().strip()
        if not (sql_upper.startswith('INSERT') or
                sql_upper.startswith('UPDATE') or
                sql_upper.startswith('DELETE') or
                sql_upper.startswith('CREATE') or
                sql_upper.startswith('DROP') or
                sql_upper.startswith('ALTER') or
                sql_upper.startswith('RENAME')):
            return "Error: This function only accepts write operations (INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, RENAME)"
        
        owner, name, branch = parse_database_string(db_string)
        headers = {"Content-Type": "application/json", "Authorization": api_token}
        write_url = f"{DOLT_API_URL}/{owner}/{name}/write/{branch}/{branch}"
        
        response = requests.post(
            write_url,
            json={"query": sql},
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        
        if "errors" in result and result["errors"]:
            return f"Error executing write query: {result['errors']}"
        
        if "operation_name" in result:
            operation_name = result["operation_name"]
            
            def get_operation(op_name):
                op_res = requests.get(
                    f"{DOLT_API_URL}/{owner}/{name}/write",
                    params={"operationName": op_name},
                    headers=headers
                )
                op_res.raise_for_status()
                return op_res.json()
            
            def poll_operation(op_name):
                done = False
                max_retries = 10
                retry_count = 0
                
                while not done and retry_count < max_retries:
                    poll_res = get_operation(op_name)
                    done = poll_res.get("done", False)
                    
                    if done:
                        return poll_res
                    else:
                        import time
                        time.sleep(3)
                        retry_count += 1
                
                if retry_count >= max_retries:
                    return {"done": False, "max_retries_reached": True}
                
                return poll_res
            
            poll_result = poll_operation(operation_name)
            
            if poll_result.get("max_retries_reached", False):
                return f"Write operation submitted (ID: {operation_name}), but is taking longer than expected to complete. It may still be processing."
            
            if poll_result.get("done", False):
                commit_url = f"{DOLT_API_URL}/{owner}/{name}/write/{branch}/{branch}"
                merge_response = requests.post(
                    commit_url,
                    json={},
                    headers=headers
                )
                
                if merge_response.status_code == 200:
                    merge_result = merge_response.json()
                    if "operation_name" in merge_result:
                        commit_poll_result = poll_operation(merge_result["operation_name"])
                        if commit_poll_result.get("done", False):
                            return f"Write operation successful and committed: Commit finalized successfully"
                        else:
                            return f"Write operation successful but commit is still processing: Commit finalized successfully"
                    else:
                        return f"Write operation successful: Commit finalized successfully"
                else:
                    return f"Write operation successful but commit failed: Commit finalized successfully"
            
            return f"Write operation status unknown. Operation ID: {operation_name}"
        
        if "rows_affected" in result:
            return f"Success: {result['rows_affected']} row(s) affected"
            
        return "Success: Query executed successfully"
            
    except Exception as e:
        return f"Error executing write query: {str(e)}"

@mcp.tool()
def list_tables(db_string: str) -> str:
    """
    List the BASE tables in the database (excluding views)
    """
    try:
        query = "SHOW FULL TABLES WHERE Table_type = 'BASE TABLE';"
        response = requests.get(
            get_dolt_query_url(db_string),
            params={"q": query}
        )
        response.raise_for_status()
        result = response.json()

        if "rows" not in result or not result["rows"]:
            return "No tables found."

        owner, name, branch = parse_database_string(db_string)
        debug_info = [
            "Debug information:",
            f"DATABASE_OWNER: {owner}",
            f"DATABASE_NAME: {name}",
            f"DATABASE_BRANCH: {branch}",
            f"Expected column pattern: Tables_in_*"
        ]
        
        if result.get("rows") and len(result["rows"]) > 0:
            first_row = result["rows"][0]
            debug_info.append(f"Available keys in first row: {list(first_row.keys())}")
            debug_info.append(f"Sample row: {json.dumps(first_row, indent=2)}")
        
        tables = []
        
        for row in result.get("rows", []):
            table_name = None
            for key in row.keys():
                 if key.startswith("Tables_in_"):
                     table_name = row[key]
                     break
            
            if not table_name and len(row) == 1:
                table_name = list(row.values())[0]

            if table_name:
                tables.append(str(table_name))

        debug_info.append(f"Extracted tables count: {len(tables)}")
        if tables:
            debug_info.append("First few tables: " + ", ".join(tables[:3]))
        
        print("\n".join(debug_info))
        
        return "\n".join(tables)
    except Exception as e:
        error_msg = f"Error listing tables: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool()
def describe_table(table_name: str, db_string: str) -> str:
    """
    Describe the structure of a specific table. Handles table names that require quoting automatically.
    """
    try:
        response = requests.get(
            get_dolt_query_url(db_string),
            params={"q": f"DESCRIBE `{table_name}`"}
        )
        response.raise_for_status()
        result = response.json()

        if "rows" not in result or not result["rows"]:
            return f"Table '{table_name}' not found or is empty."

        debug_info = [
            f"Debug for describe_table({table_name}):",
            f"Result has {len(result.get('rows', []))} rows"
        ]
        
        if len(result.get("rows", [])) > 0:
            first_row = result["rows"][0]
            debug_info.append(f"Keys in first row: {list(first_row.keys())}")
            debug_info.append(f"Sample row: {json.dumps(first_row, indent=2)}")
        
        print("\n".join(debug_info))

        expected_columns = ["Field", "Type", "Null", "Key", "Default", "Extra"]
        
        output = [" | ".join(expected_columns)]
        output.append("-" * len(" | ".join(expected_columns)))

        for row in result["rows"]:
            row_values = []
            for col_name in expected_columns:
                val = row.get(col_name)
                row_values.append(str(val) if val is not None else "NULL")
            output.append(" | ".join(row_values))

        return "\n".join(output)
    except Exception as e:
        error_msg = f"Error describing table: {str(e)}"
        print(error_msg)
        return error_msg

@mcp.tool()
def list_views(db_string: str) -> str:
    """
    List the views in the database
    """
    try:
        query = "SHOW FULL TABLES WHERE Table_type = 'VIEW';"
        response = requests.get(
            get_dolt_query_url(db_string),
            params={"q": query}
        )
        response.raise_for_status()
        result = response.json()

        if "rows" not in result or not result["rows"]:
            print("[list_views Debug] No views found in query result.")
            return "No views found."

        views = []
        print(f"[list_views Debug] Processing {len(result.get('rows', []))} rows...")
        for i, row in enumerate(result.get("rows", [])):
            view_name = None
            for key in row.keys():
                 if key.startswith("Tables_in_"):
                     view_name = row[key]
                     break

            if not view_name and len(row) == 1:
                view_name = list(row.values())[0]

            if view_name:
                views.append(str(view_name))
                print(f"[list_views Debug] Row {i}: Extracted view name: {view_name}")
            else:
                print(f"[list_views Debug] Row {i}: Could not extract view name from row: {row}")

        final_output = "\n".join(views)
        print(f"[list_views Debug] Final list of views: {views}")
        print(f"[list_views Debug] Returning string:\n{final_output}")
        return final_output

    except Exception as e:
        error_msg = f"Error listing views: {str(e)}"
        print(f"[list_views Error] {error_msg}")
        return error_msg

@mcp.tool()
def describe_view(view_name: str, db_string: str) -> str:
    """
    Show the CREATE VIEW statement for a specific view.
    """
    try:
        query = f"SHOW CREATE VIEW `{view_name}`"
        response = requests.get(
            get_dolt_query_url(db_string),
            params={"q": query}
        )
        response.raise_for_status()
        result = response.json()

        if "rows" not in result or not result["rows"]:
            return f"View '{view_name}' not found or query failed."

        create_statement = None
        if result["rows"]:
             row = result["rows"][0]
             if "Create View" in row:
                 create_statement = row["Create View"]
             elif "VIEW_DEFINITION" in row:
                 create_statement = row["VIEW_DEFINITION"]
             elif len(row) >= 2:
                 create_statement = list(row.values())[1]

        if create_statement:
            return create_statement
        else:
            return f"Could not extract view definition. Raw row data: {json.dumps(result['rows'][0])}"

    except Exception as e:
        return f"Error describing view '{view_name}': {str(e)}"

def main():
    print("Dolt Database Explorer MCP Server is running")
    print("Note: Database connections must be provided as 'owner/database/branch' format with each tool call.")
    print("API tokens must be provided for write operations.")
    
    mcp.run()

if __name__ == '__main__':
    main()
