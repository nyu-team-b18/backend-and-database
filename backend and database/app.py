from flask import Flask, request, redirect, jsonify
from flask_cors import CORS
import oracledb

app = Flask(__name__)
CORS(app)
session = {}

cs = '''(description= (retry_count=3)(retry_delay=3)(address=(protocol=tcps)
        (port=1521)(host=adb.us-ashburn-1.oraclecloud.com))
        (connect_data=(service_name=g4ce17c11a5179b_helloadventuredb_low.adb.oraclecloud.com))
        (security=(ssl_server_dn_match=yes)))'''

conn = oracledb.connect(
    user="admin",
    password="Helloadventure123!",
    dsn=cs)  # the connection string copied from the cloud console


@app.route('/verifyRegistration', methods=["GET", "POST"])
def verifyRegistration():
    global session

    # Get registration details
    data = request.get_json()
    account_type = data['account-type']
    email = data['email']
    username = data['username']
    password = data['password']
    confirmation = data['password-confirm']

    # Check if passwords match
    if password != confirmation:
        return jsonify({
            "result": "FAIL",
            "message": "Passwords must match"
        })

    # Register admin account
    if account_type == "admin":
        # Get student group
        student_group = data['student-group']   

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE email =: temp', temp=email)
        data = cursor.fetchall()

        # If the account exists
        if data:
            cursor.close()
            return jsonify({
                "result": "FAIL",
                "message": "User already exists"
            })

        # Check if the student group is in use
        cursor.execute('SELECT * FROM admin WHERE student_group =: temp', temp=student_group)
        data = cursor.fetchall()

        # If the student group is in use
        if data:    
            cursor.close()
            return jsonify({
                "result": "FAIL", 
                "message": "Student group in use"
            })

        # Create the account
        cursor.execute('INSERT INTO admin (EMAIL, USER_NAME, PASSWORD, STUDENT_GROUP) '
                        'VALUES(:email, :username, :password, :student_group)',
                        [email, username, password, student_group])
        conn.commit()
        cursor.close()

        # Begin new session
        session['username'] = username
        session['email'] = email
        session['account-type'] = account_type

        return jsonify({
            "result": "SUCCEED"
        })

    elif account_type == "student":
        # Get student group
        student_group = data['student-group']   

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM student WHERE email =: temp', temp=email)
        data = cursor.fetchone()

        # If the account exists
        if data:
            cursor.close()
            return jsonify({
                "result": "FAIL",
                "message": "User already exists"
            })

        # Check if the student group exists
        cursor.execute('SELECT * FROM admin WHERE student_group =: temp', temp=student_group)
        data = cursor.fetchall()

        # If the student group exists
        if not data:
            cursor.close()
            return jsonify({
                "result": "FAIL",
                "message": "Student group not found"
            })

        # Create the account
        cursor.execute('INSERT INTO student (EMAIL, USER_NAME, PASSWORD, STUDENT_GROUP, PROGRESS, ASSIGNMENT) '
                        'VALUES(:email, :username, :password, :student_group, null, null)',
                        [email, username, password, student_group])
        conn.commit()
        cursor.close()

        # Begin a new session
        session['username'] = username
        session['email'] = email
        session['account-type'] = account_type

        return jsonify({
            "result": "SUCCEED",
        })

    elif account_type == "guest":
        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest WHERE email =: temp', temp=email)
        data = cursor.fetchall()

        # If the account exists
        if data:
            cursor.close()
            return jsonify({
                "result": "FAIL",
                "message": "User already exists"
            })  

        # Create the account
        cursor.execute('INSERT INTO guest (EMAIL, USER_NAME, PASSWORD, PROGRESS) '
                        'VALUES(:email, :username, :password, null)',
                        [email, username, password])
        
        # Begin new session
        session['username'] = username
        session['email'] = email
        session['account-type'] = account_type

        conn.commit()
        cursor.close()
        return jsonify({
            "result": "SUCCEED",
        })


@app.route('/verifyLogin', methods=["GET", "POST"])
def verifyLogin():
    global session

    data = request.get_json()
    # account_type = data['account-type']
    username = data['username']
    password = data['password']

    username_index = 1

    # CHECK IF IT IS AN ADMIN ACCOUNT
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM admin WHERE user_name =: username and password =: password', [username, password])
    data = cursor.fetchone()

    print(data)

    if data:
        cursor.close()
        student_group_index = 3
        session['account-type'] = 'admin'
        session['username'] = data[username_index]
        session['student-group'] = data[student_group_index]
        
        return jsonify({}), 200
    
    # CHECK IF IT IS A STUDENT ACCOUNT
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM student WHERE user_name =: username and password =: password', [username, password])
    data = cursor.fetchone()

    if data:
        cursor.close()
        student_group_index = 5
        session['account-type'] = 'student'
        session['username'] = data[username_index]
        session['student-group'] = data[student_group_index]

        return jsonify({}), 200

    # CHECK IF IT IS A GUEST ACCOUNT
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM guest WHERE user_name =: username and password =: password', [username, password])
    data = cursor.fetchone()

    if data:
        cursor.close()
        session['account-type'] = 'guest'
        session['username'] = data[username_index]
        return jsonify({}), 200

    # Login failed
    return jsonify({}), 409


@app.route('/logout', methods=["GET", "POST"])
def logout():
    global session
    session.clear()
    
    # redirect
    return jsonify({})


@app.route('/getAssignments', methods=["GET"])
def getAssignments():
    global session
    # Get the student group
    student_group = session['student-group']

    # Get class assignments
    cursor = conn.cursor()
    cursor.execute('SELECT assign_title from ASSIGNMENT WHERE student_group =: temp', temp = student_group)
    data = cursor.fetchall()

    return jsonify({
        'assignments': data,
    })


@app.route('/getStudents', methods=["GET"])
def getStudents():
    global session

    # Get class students
    student_group = session['student-group']
    cursor = conn.cursor()

    cursor.execute('SELECT user_name FROM STUDENT where student_group =: student_group', student_group = student_group)
    data = cursor.fetchall() # a list of students
    cursor.close()

    # Get all student usernames
    student_list = []
    for student in data:
        student_list.append({
            'username': student[0],
            'name': student[0]
        })
    
    return jsonify({
        'students': student_list
    })


@app.route('/getAccountType', methods=["GET"])
def getAccountType():
    global session

    # Get account type
    try:
        account_type = session['account-type']
    except:
        account_type = 'none'
    return jsonify({'account-type': account_type})


@app.route('/getAssignmentDetails', methods=["GET"])
def getAssignmentDetails():
    global session
    student_group = session['student-group']

    # GET args
    assign_title = request.args.get('assignment')

    # Get assignment description and date
    cursor = conn.cursor()
    # check if the assignment exists
    cursor.execute('SELECT * from assignment WHERE assign_title =: assign_title AND student_group := student_group ', [assign_title, student_group])
    data = cursor.fetchall()
    
    return jsonify({
        'title': assign_title,
        'description': data[0][0],
        'date': data[0][1].strftime('%Y-%m-%d'),
        'world': data[0][2],
        'level': data[0][3]
    })


@app.route('/updateAssignment', methods=["GET", "POST"])
def updateAssignment():
    if (request.method == 'POST'):
        global session
        student_group = session['student-group']

        data = request.get_json()
        assign_title = data['title']
        assign_description = data['description']
        due_date = data['date']
        world = data['world']
        game_level = data['level']

        # Update the assignment
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE ASSIGNMENT SET assign_description =: assign_description, due_date = TO_DATE(:due_date, 'YYYY-MM-DD'), world =: world, game_level =: game_level
            WHERE assign_title =: assign_title AND student_group =: student_group""", [assign_description, due_date, world, game_level, assign_title, student_group])
        conn.commit()
        cursor.close()


    return jsonify({})


@app.route('/createAssignment', methods=["GET", "POST"])
def createAssignment():
    global session
    student_group = session['student-group']

    data = request.get_json()
    assign_title = data['title']
    assign_description = data['description']
    due_date = data['date']
    world = data['world']
    game_level = data['level']
    
    cursor = conn.cursor()
    # check if the assignment already exists
    cursor.execute('SELECT * from assignment where assign_title =: title AND student_group =: student_group', 
                   [assign_title, student_group])
    data = cursor.fetchone()

    if data:  # Failure, assignment already exists
        cursor.close()
        return jsonify({}), 409

    else:  # Success
        cursor.execute(f"""INSERT into assignment(assign_description, due_date, world, game_level, student_group, assign_title) 
                            VALUES(:assign_description, TO_DATE(:due_date, 'YYYY-MM-DD'), :world, :game_level, :student_group, :assign_title)""",
                       [assign_description, due_date, world, game_level, student_group, assign_title])
        conn.commit()
        cursor.close()
        return jsonify({}), 200


@app.route('/getProfile', methods=["GET"])
def getProfile():
    # TODO: Get the account type from the session
    # TODO: Get the username from the session
    account_type = session['account-type']
    username = session['username']
    cursor = conn.cursor()

    details = {}

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

    return jsonify(details)


@app.route('/updateProfile', methods=['GET', 'POST'])
def updateProfile():
    global session

    account_type = session['account-type']
    username = session['username']

    data = request.get_json()
    new_email, new_password = data['email'], data['password']

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
            return error

        else:
            cursor.execute('update STUDENT set email =: new_email, password =: new_password'
                           ' where user_name =: username', [new_email, new_password, username])
            conn.commit()
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
            cursor.close()

    return jsonify({})


@app.route("/deleteAccount", methods=["GET", "DELETE"])
def deleteAccount():
    global session

    # Get account details
    account_type = session['account-type']
    username = session['username']

    cursor = conn.cursor()
    if account_type == 'admin':
        # # TODO: Change all students under this admin to guest accounts
        # #check if the student exists and is in thr group
        # cursor.execute('SELECT student.user_name from student, admin WHERE student.student_group = admin.student_group'
        #                'AND admin.user_name =: temp', temp = username)
        # data = cursor.fetchall()
        # if data:
        #     for student in data:
        #         cursor.execute('UPDATE student SET student_group = null WHERE user_name =: temp', temp = student[0])
        #         conn.commit()
        #         # TODO: Delete this account from admin table
        cursor.execute('DELETE FROM admin WHERE user_name =: temp', temp = username)
        conn.commit()
        cursor.close()
    elif account_type == 'guest':
        # TODO: Delete this account from guest table
        cursor.execute('DELETE FROM guest WHERE user_name =: temp', temp = username)
        conn.commit()
        cursor.close()


    # TODO: Destroy all session variables
    session.clear()
    return jsonify({})


@app.route("/getStudentInformation", methods=["GET"])
def getStudentInformation():
    # GET args
    student_username = request.args.get('username')
    cursor = conn.cursor()
    # Get student information
    cursor.execute('SELECT * FROM STUDENT where user_name =: temp', temp = student_username)
    data = cursor.fetchone()

    email = data[0]

    # Get all completed assignments
    # TODO: Add a query that gets all assignment titles completed by this student
    #Assume student already exists
    cursor.execute('SELECT assignment FROM student where user_name =: temp', temp = student_username)
    assignments = cursor.fetchall()
    return jsonify({
        'username': student_username,
        'email': email,
        'assignments': assignments
    })


@app.route("/dropStudent", methods=["GET", "POST"])
def dropStudent():
    data = request.get_json()
    student_username = data['username']
    cursor = conn.cursor()

    #Remove student from current student group
    cursor.execute('UPDATE student set student_group = null WHERE user_name =: temp', temp = student_username)
    conn.commit()
    cursor.close()

    return jsonify({})


app.secret_key = 'some other random key'

if __name__ == '__main__':
    app.run('127.0.0.1', 5000, debug=True)
    session['test'] = 10