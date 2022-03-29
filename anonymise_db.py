    # This function will get the directory with a dialog box
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    file = filedialog.askopenfilename()
    return file

def get_export_directory():
    """ This function will get the export directory
    """
    import os
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()
    export_location = filedialog.askdirectory()
    return export_location

def anonymise_postgres_database():
    """ This function will anonymize and mask employee's informations,
    in a postgres database in order to guard confidentiality
    """
    import psycopg2
    import os
    import getpass
    import time
    import random
    import string
    import sys
    import datetime

    # Get the file with the database
    # file = get_file_with_dialog_box()

    # Get the login and password of the database
    database = input("Enter the database name: ")
    database_old = database
    user = input("Enter the user for the database: ")
    password = getpass.getpass("Enter the password for the database: ")

    # Connect to the database
    conn = psycopg2.connect(database=database, user=user, password=password, host='localhost')
    conn.autocommit = True
    cur = conn.cursor()
    print("Connected to the database: " + database)

    # terminate all other connections to the db except mine
    cur.execute("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '" + database + "' AND pid <> pg_backend_pid();")

    # Remove if it already exists and Create a copy of the database
    try: 
        cur.execute("CREATE DATABASE anonymised_" + database + " WITH TEMPLATE " + database +" OWNER " + user + ";")
        print("Database anonymised_" + database + " created")
    except:
        print("Database anonymised_" + database + " already exists")
        cur.execute("DROP DATABASE anonymised_" + database)
        conn.commit()
        print("Database anonymized_" + database + " removed")
        conn.autocommit = True
        cur.execute("CREATE DATABASE anonymised_" + database + " WITH TEMPLATE " + database +" OWNER " + user + ";")
        print("Database anonymised_" + database + " created")

    # Disconnect from the original database
    conn.commit()
    conn.close()
    # connect to the new database
    conn = psycopg2.connect(database="anonymised_" + database, user=user, password=password)
    conn.autocommit = True
    cur = conn.cursor()

    # Get the table names
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    table_names = cur.fetchall()

    # Get the column names
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema = 'public'")
    column_names = cur.fetchall()

    # Get the column names in a list
    column_names_list = []
    for column in column_names:
        column_names_list.append(column[0])

    # Get the table names in a list
    table_names_list = []
    for table in table_names:
        table_names_list.append(table[0])

    # Get the number of rows
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
    number_of_rows = cur.fetchall()

    # Get the number of rows in a list
    number_of_rows_list = []
    for row in number_of_rows:
        number_of_rows_list.append(row[0])

    # Get the number of columns
    cur.execute("SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'public'")
    number_of_columns = cur.fetchall()

    # Get the number of columns in a list
    number_of_columns_list = []
    for column in number_of_columns:
        number_of_columns_list.append(column[0])

    cur.execute("SELECT * FROM hr_employee")

    # anonymise the hr.employee table
    cur.execute("SELECT * FROM hr_employee")
    rows = cur.fetchall()
    i= 0
    for row in rows:
        # set the first name to a random string
        first_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        # set the last name to a random string
        last_name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        # set the name to a random string
        name = first_name + ' ' + last_name
        # set the birth date to a random date
        birthday = '19'+str(random.randint(10, 99))+'-'+str(random.randint(1, 12))+'-'+str(random.randint(1, 28))
        # set the cnas number as a random matriculation number
        social_security_num = str(str(birthday[2:3]).join(str(random.randint(0, 9) for _ in range(12))))[0:9]+str(i).rjust(3, "0")
        # set the job title to a random string
        job_title = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        i += 1
        # save the changes
        cur.execute("UPDATE hr_employee SET name = '"+ name +"', first_name = '" + first_name + "', last_name = '" + last_name + "', birthday = '" + birthday + "', social_security_num = '" + social_security_num + "' WHERE id = " + str(row[0]))
        
    # anonymise the res.partner table
    cur.execute("SELECT * FROM res_partner")
    rows = cur.fetchall()
    for row in rows:
        # set the name to a random string
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        # save the changes
        cur.execute("UPDATE res_partner SET name = '" + name + "' WHERE id = " + str(row[0]))

    # anonymise the hr.job table
    cur.execute("SELECT * FROM hr_job")
    rows = cur.fetchall()
    for row in rows:
        name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        # save the changes
        cur.execute("UPDATE hr_job SET name = '"+ name +"' WHERE id = " + str(row[0]))
        
    # save the database and export it to a file
    conn.commit()
    print("changes committed to the database anonymised_"+ database)

    # select export location
    export_location = get_export_directory()

    # save the db to the export diretory
    os.system("pg_dump -U " + user + " -h localhost -d " + database + " -f " + export_location + "/anonymised_" + database + ".sql")
    print("Database anonymised_" + database_old + " exported to " + export_location + "/anonymised_" + database + ".sql")

    # open folder where the file was saved 


if __name__ == "__main__":
    anonymise_postgres_database()