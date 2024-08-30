import os
import psycopg2
import sqlparse
from itertools import permutations

def extract_tables_and_predicates(sql):
    parsed = sqlparse.parse(sql)[0]
    tables = {}
    where_clause = ""
    from_seen = False
    where_seen = False

    for token in parsed.tokens:
        if from_seen and not where_seen:
            if isinstance(token, sqlparse.sql.IdentifierList):
                for identifier in token.get_identifiers():
                    tables[identifier.get_real_name()] = ""
            elif isinstance(token, sqlparse.sql.Identifier):
                tables[token.get_real_name()] = ""
        if where_seen:
            where_clause += str(token)
        if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == "FROM":
            from_seen = True
        if token.ttype is sqlparse.tokens.Keyword and token.value.upper() == "WHERE":
            where_seen = True
    
    for table in tables.keys():
        if where_clause:
            conditions = []
            for condition in where_clause.split("AND"):
                if table in condition:
                    conditions.append(condition.strip())
            tables[table] = " AND ".join(conditions)
    
    return tables

def read_sql_files_from_directory(directory_path):
    sql_files = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".sql"):
            with open(os.path.join(directory_path, filename), 'r') as file:
                sql_files.append(file.read())
    return sql_files

conn = psycopg2.connect(
    dbname="imdb",
    user="postgres",
    password="",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

sql_directory = 'path_to_your_sql_directory'
sql_queries = read_sql_files_from_directory(sql_directory)

with open('info.txt', 'w') as file:
    for sql_query in sql_queries:
        tables = extract_tables_and_predicates(sql_query)

        results_cache = {}

        for i in range(2, len(tables) + 1):
            combos = permutations(tables.keys(), i)
            for combo in combos:
                combo_key = tuple(sorted(combo))  

                if combo_key not in results_cache:
                    from_clause = ', '.join(combo)
                    where_clause = ' AND '.join([tables[alias] for alias in combo if tables[alias]])

                    if where_clause:
                        query = f"SELECT COUNT(*) FROM {from_clause} WHERE {where_clause}"
                    else:
                        query = f"SELECT COUNT(*) FROM {from_clause}"

                    try:
                        cursor.execute(query)
                        count = cursor.fetchone()[0]
                        results_cache[combo_key] = count
                        print(f"Query successful for: {', '.join(combo)}, Count: {count}")
                    except psycopg2.Error as e:
                        print(f"Query failed for: {', '.join(combo)}. Error: {str(e)}")
                        results_cache[combo_key] = None

                count = results_cache.get(combo_key)
                if count is not None:
                    file.write(f"{', '.join(combo)}: {count}\n")

conn.close()
