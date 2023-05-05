
import oracledb
from datetime import date
import time

cs = '''(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=g4ce17c11a5179b_helloadventuredb_low.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'''

conn = oracledb.connect(
    user="admin",
    password="Helloadventure123!",
    dsn=cs)  # the connection string copied from the cloud console

print("Successfully connected to Oracle Database")

# Create a table


def verifyRegistration():
    account_type = input("account type")

    if account_type == "admin":
        email = input("email:")
        user_name = input("username:")
        password = input("password:")
        student_group = input("group:")

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM ADMIN WHERE email =: temp', temp = email)
        data = cursor.fetchone()
        error = None

        if (data):
            # If the previoud query returns data, then user exists
            error = "This user has already exists"
            return error
        else:  # Succeed

            cursor.execute('INSERT INTO ADMIN (EMAIL, USER_NAME, PASSWORD, STUDENT_GROUP) '
                           'VALUES(:email, :username, :password, :student_group)',
                           [email,user_name, password, student_group])
            conn.commit()
            cursor.close()
            print("success to create admin")
            return

    elif account_type == "student":
        email = input("email:")
        user_name = input("username:")
        password = input("password:")
        student_group = input("group:")

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM student WHERE email =: temp', temp=email)
        data = cursor.fetchone()
        error = None

        if (data):
            # If the previous query returns data, then user exists
            error = "This user has already exists"
            return error

        else:  # Succeed

            cursor.execute('INSERT INTO student (EMAIL, USER_NAME, PASSWORD, STUDENT_GROUP, PROGRESS, ASSIGNMENT) '
                           'VALUES(:email, :username, :password, :student_group, null, null)',
                           [email, user_name, password, student_group])
            conn.commit()
            cursor.close()
            print("success to create student")
            return


    elif account_type == "guest":
        email = input("email:")
        user_name = input("username:")
        password = input("password:")

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest WHERE email =: temp', temp=email)
        data = cursor.fetchone()
        error = None

        if (data):
            # If the previous query returns data, then user exists
            error = "This user has already exists"
            print(error)
            return error

        else:  # Succeed

            cursor.execute('INSERT INTO guest (EMAIL, USER_NAME, PASSWORD, PROGRESS) '
                           'VALUES(:email, :username, :password, null)',
                           [email, user_name, password])
            conn.commit()
            cursor.close()
            print("succeed create guest")
            return 



def verifyLogin():

    account_type = input("account_type:")
    email = input("email:")
    password = input("password:")

    if account_type == "admin":
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE email =: email and password =: password', [email, password])
        data = cursor.fetchone()
        error = None
        cursor.close()

        if (data):

            print("admin login")
        else:
            error = "Invalid username or password"
            print(error)

    elif account_type == "student":
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM student WHERE email =: email and password =: password', [email, password])
        data = cursor.fetchone()
        error = None
        cursor.close()

        if (data):

            print("student login")
        else:
            error = "Invalid username or password"
            print(error)
    elif account_type == "guest":
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest WHERE email =: email and password =: password', [email, password])
        data = cursor.fetchone()
        error = None
        cursor.close()

        if (data):

            print("guest login")
        else:
            error = "Invalid username or password"
            print(error)

def getstudent():
    account_type = input("accounttype:")
    if account_type == "admin":
        username = input("username:")
        cursor = conn.cursor()
        cursor.execute(
            'SELECT STUDENT.user_name, STUDENT.email from ADMIN, STUDENT where ADMIN.user_name =:username and '
            'ADMIN.student_group = STUDENT.student_group', username = username)
        data=cursor.fetchall()
        for student in data:
            print("name:", student[0])
            print("email:", student[1])
        print(data)

def createAssignment():
    title = input ("title:")
    description = input("description:")
    assignment_date = date.today()
    print(assignment_date)
    world = input("world:")
    level = input("level:")

    cursor = conn.cursor()
    # check if the assignment already exists
    cursor.execute('SELECT * from assignment where id =: temp', temp = title)
    data = cursor.fetchone()
    error = None

    if data:  # Failure
        print ("assignment already exists")


    else:  # Success
        cursor.execute('INSERT into assignment(id, description, assignment_date, world, game_level) '
                       'VALUES(:id, :description, :assignment_date, :world, :game_level)',
                       [title, description, assignment_date, world, level])
        conn.commit()
        cursor.close()
        print("success")

def getAssignmentDetails():
    # GET args
    assignment_title = input("id:")

    # Get assignment description and date
    cursor = conn.cursor()
    cursor.execute('SELECT * from assignment WHERE id =: temp ', temp = assignment_title)
    data = cursor.fetchall()
    error = None
    if data:
        print(data)
        print("description:", data[0][1])

    else:
        error = "No such assignment"
        print(error)

def getStudents():
    # Get class students
    username = input("username:")
    cursor = conn.cursor()

    cursor.execute('SELECT STUDENT.user_name, STUDENT.email from ADMIN, STUDENT where ADMIN.user_name =: username and '
                   'ADMIN.student_group = STUDENT.student_group', username = username)
    data = cursor.fetchall()
    cursor.close()
    print("data")

def updateAssignment():
    title = input ("title:")
    description = input("description:")
    assignment_date = date.today()
    print(assignment_date)
    world = input("world:")
    level = input("level:")

        # Update the assignment
        # TODO: Add query to update database at assignment title
    cursor = conn.cursor()

        #check if this assignment exists
    cursor.execute('SELECT * FROM ASSIGNMENT WHERE id =: temp', temp = title)
    data = cursor.fetchone()
    print(data)
    error = None

    if data:
        cursor.execute('UPDATE ASSIGNMENT SET description =: new_description, assignment_date =: new_date, world =: new_world, game_level =: new_level '
                       'WHERE id =: new_title',[description, assignment_date, world, level, title])
        conn.commit()
        print("success")
        cursor.close()
    else:
        error = "this assignment doesn't exist"
        cursor.close()
        print(error)

def getProfile():
    # TODO: Get the account type from the session
    # TODO: Get the username from the session
    account_type = input("account:")
    username = input("username:")
    cursor = conn.cursor()

    if account_type == 'student':
        # Get the account details

        cursor.execute('SELECT user_name, email, progress from student where user_name =: temp', temp=username)
        data = cursor.fetchone()
        error = None
        cursor.close()
        if (data):
            print(data)
            details = {
                'username': data[0],
                'email': data[1],
                'progress': data[2]
            }
            print(details)
        else:
            error = "There was an error viewing the progress."
            print(error)

    elif account_type == 'admin':
        # Get the account details

        cursor.execute('SELECT user_name, email from admin where user_name =: temp', temp=username)
        data = cursor.fetchone()
        error = None
        cursor.close()
        if (data):
            print(data)
            details = {
                'username': data[0],
                'email': data[1]
            }
            print(details)
        else:
            error = "There was an error viewing the progress."
            print(error)

    else:
        # Get the account details
        cursor.execute('SELECT user_name, email, progress from guest where user_name =: temp', temp=username)
        data = cursor.fetchone()
        error = None
        cursor.close()
        if (data):
            print(data)
            details = {
                'username': data[0],
                'email': data[1],
                'progress': data[2]
            }
            print(details)
        else:
            error = "There was an error viewing the progress."
            print(error)

def updateProfile():
    # TODO: Get the account type from the session
    # TODO: Get the username from the session
    account_type = input("account:")
    username = input("username:")




    new_email = input("email:")
    new_password = input("password:")

    cursor = conn.cursor()

    if account_type == 'student':
        # Get the account details
        # TODO: Add a query to update profile information from students
        # check if email is in use
        cursor.execute('SELECT * FROM student WHERE email =: temp', temp=new_email)
        data = cursor.fetchone()
        error = None
        if (data):
            error = "Email already in use"
            print(error)

        else:
            cursor.execute('update STUDENT set email =: new_email, password =: new_password'
                           ' where user_name =: username', [new_email, new_password, username])
            conn.commit()
            print("success")
            cursor.close()

    elif account_type == 'admin':
        # Get the account details
        # TODO: Add a query to update profile information from admins
        cursor.execute('SELECT * FROM admin WHERE email =: temp', temp=new_email)
        data = cursor.fetchone()
        error = None
        if (data):
            error = "Email already in use"
            return error

        else:
            cursor.execute('update ADMIN set email =: new_email, password =: new_password'
                           ' where user_name =: username', [new_email, new_password, username])
            conn.commit()
            print("success")
            cursor.close()
    else:
        # Get the account details
        cursor.execute('SELECT * FROM GUEST WHERE email =: temp', temp=new_email)
        data = cursor.fetchone()
        error = None
        if (data):
            error = "Email already in use"
            return error

        else:
            cursor.execute('update GUEST set email =: new_email, password =: new_password'
                           ' where user_name =: username', [new_email, new_password, username])
            conn.commit()
            print("success")
            cursor.close()


def getStudentInformation():
    # GET args
    student_username = input("student username:")
    cursor = conn.cursor()
    # Get student information
    cursor.execute('SELECT * FROM STUDENT where user_name =: temp', temp = student_username)
    data = cursor.fetchone()
    if data:
    # TODO: Add a query to get student details
        admin_username = input("adminusername:")
        cursor.execute('SELECT student.email, student.progress FROM ADMIN, STUDENT WHERE ADMIN.student_group = STUDENT.student_group AND STUDENT.user_name =: username and ADMIN.user_name =: temp', [student_username, admin_username])
        data = cursor.fetchone()
        error = None


        if data:
            print(data)
        else:
            error = "Student are not in the group"
            cursor.close()
            return error
    else:
        error = "Student doesn't exist"
        cursor.close()
        return error


    # Get all completed assignments
    # TODO: Add a query that gets all assignment titles completed by this student
    cursor.execute('SELECT assignment FROM student where user_name =: temp', temp = student_username)
    assignments = cursor.fetchall()
    print(assignments)


def dropStudent():

    student_username = input("student")
    cursor = conn.cursor()

    # Delete the old student account
    # TODO: Add a query to delete the old student account

    # Remove student from current student group
    cursor.execute('UPDATE student set student_group = null WHERE user_name =: temp', temp=student_username)
    conn.commit()
    cursor.close()

    print("success")

def deleteAccount():
        # TODO: Get the account type from the session
        # TODO: Get the username from the session
    account_type = "admin"
    username = "zhilue"

    cursor = conn.cursor()
    if account_type == 'admin':
            # TODO: Change all students under this admin to guest accounts
        cursor.execute('SELECT student.user_name from student, admin WHERE student.student_group = admin.student_group AND admin.user_name =: temp', temp=username)
        data = cursor.fetchall()
        print(data)
        if data:
            for student in data:
                print(student)
                cursor.execute('UPDATE student SET student_group = null WHERE user_name =: temp', temp=student[0])
                print("success")


deleteAccount()