from flask import Flask, request, session, redirect, jsonify
from flask_cors import CORS
import oracledb

app = Flask(__name__)
CORS(app)

cs = '''(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=adb.us-ashburn-1.oraclecloud.com))(connect_data=(service_name=g4ce17c11a5179b_helloadventuredb_low.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))'''

conn = oracledb.connect(
    user="admin",
    password="Helloadventure123!",
    dsn=cs)  # the connection string copied from the cloud console


@app.route('/verifyRegistration', methods=["GET", "POST"])
def verifyRegistration():
    data = request.get_json()
    account_type = data['account-type']

    if account_type == "admin":
        email = request.form['email']
        user_name = request.form['username']
        password = request.form['password']
        student_group = request.form['student-group']

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE email =: temp', temp=email)
        data = cursor.fetchone()
        error = None

        if (data):
            # If the previoud query returns data, then user exists
            error = "This user has already exists"
            return jsonify({
                "result": "FAIL",
                "message": "Admin already exists"
            })

        else:  # Succeed

            cursor.execute('INSERT INTO admin (EMAIL, USER_NAME, PASSWORD, STUDENT_GROUP) '
                           'VALUES(:email, :username, :password, :student_group)',
                           [email, user_name, password, student_group])
            conn.commit()
            cursor.close()
            return jsonify({
                "result": "SUCCEED",
            })

    elif account_type == "student":
        email = request.form['email']
        user_name = request.form['username']
        password = request.form['password']
        student_group = request.form['student-group']

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM student WHERE email =: temp', temp=email)
        data = cursor.fetchone()
        error = None

        if (data):
            # If the previous query returns data, then user exists
            error = "This user has already exists"
            return jsonify({
                "result": "FAIL",
                "message": "Student already exists"
            })

        else:  # Succeed

            cursor.execute('INSERT INTO student (EMAIL, USER_NAME, PASSWORD, STUDENT_GROUP, PROGRESS, ASSIGNMENT) '
                           'VALUES(:email, :username, :password, :student_group, null, null)',
                           [email, user_name, password, student_group])
            conn.commit()
            cursor.close()
            return jsonify({
                "result": "SUCCEED",
            })

    elif account_type == "guest":
        email = request.form['email']
        user_name = request.form['username']
        password = request.form['password']

        # Check if the account already exists
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest WHERE email =: temp', temp=email)
        data = cursor.fetchone()
        error = None

        if (data):
            # If the previous query returns data, then user exists
            error = "This user has already exists"
            return jsonify({
                "result": "FAIL",
                "message": "Guest user already exists"
            })

        else:  # Succeed

            cursor.execute('INSERT INTO guest (EMAIL, USER_NAME, PASSWORD, PROGRESS) '
                           'VALUES(:email, :username, :password, null)',
                           [email, user_name, password])
            conn.commit()
            cursor.close()
            return jsonify({
                "result": "SUCCEED",
            })


@app.route('/verifyLogin', methods=["GET", "POST"])
def verifyLogin():
    data = request.get_json()
    account_type = data['account-type']
    email = request.form['email']
    password = request.form['password']

    if account_type == "admin":
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE email =: email and password =: password', [email, password])
        data = cursor.fetchone()
        error = None
        cursor.close()

        if (data):

            return jsonify({}), 200
        else:
            error = "Invalid email or password"
            return jsonify({}), 409

    elif account_type == "student":
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM student WHERE email =: email and password =: password', [email, password])
        data = cursor.fetchone()
        error = None
        cursor.close()

        if (data):

            return jsonify({}), 200
        else:
            error = "Invalid email or password"
            return jsonify({}), 409

    elif account_type == "guest":
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM guest WHERE email =: email and password =: password', [email, password])
        data = cursor.fetchone()
        error = None
        cursor.close()

        if (data):

            return jsonify({}), 200
        else:
            error = "Invalid email or password"
            return jsonify({}), 409


@app.route('/logout', methods=["GET", "POST"])
def logout():
    # TODO: Destroy all session variables
    session.pop('username')
    # redirect
    return jsonify({})


@app.route('/getAssignments', methods=["GET"])
def getAssignments():
    # Get class assignments
    assignment_id = request.form["assignment id"]
    cursor = conn.cursor()
    cursor.execute('SELECT * from ASSIGNMENT WHERE ID =: temp', temp = assignment_id)
    data = cursor.fetchone()

    return jsonify({
        'assignments': data,
    })


@app.route('/getStudents', methods=["GET"])
def getStudents():
    # Get class students
    username = session['username']
    cursor = conn.cursor()

    cursor.execute('SELECT STUDENT.user_name, STUDENT.email from ADMIN, STUDENT where ADMIN.user_name =: username and '
                   'ADMIN.student_group = STUDENT.student_group', username = username)
    data = cursor.fetchall() # a list of students
    cursor.close()
    return jsonify({
        'students': data
    })


@app.route('/getAccountType', methods=["GET"])
def getAccountType():
    # Get account type
    account_type = session['account-type']
    return jsonify({'account-type': account_type})

@app.route('/getAssignmentDetails', methods=["GET"])
def getAssignmentDetails():
    # GET args
    assignment_title = request.args.get('assignment')

    # Get assignment description and date
    cursor = conn.cursor()
    # check if the assignment exists
    cursor.execute('SELECT * from assignment WHERE id =: temp ', temp = assignment_title)
    data = cursor.fetchall()
    error = None
    if data:
        return jsonify({
            'title': assignment_title,
            'description': data[0][1],
            'date': data[0][2],
            'world': data[0][3],
            'level': data[0][4]
        })
    else:
        error = "No such assignment"
        return error

@app.route('/updateAssignment', methods=["GET", "POST"])
def updateAssignment():
    if (request.method == 'POST'):
        data = request.get_json()
        title, description, assignment_date = data['title'], data['description'], data['date']
        world, level = data['world'], data['level']

        # Update the assignment
        # TODO: Add query to update database at assignment title
        cursor = conn.cursor()

        #check if this assignment exists
        cursor.execute('SELECT * FROM ASSIGNMENT WHERE id =: temp', temp = title)
        data = cursor.fetchone()
        error = None

        if data: #succeed
            cursor.execute(
                'UPDATE ASSIGNMENT SET description =: new_description, assignment_date =: new_date, world =: new_world, game_level =: new_level '
                'WHERE id =: new_title', [description, assignment_date, world, level, title])
            conn.commit()
            cursor.close()
        else:
            error = "this assignment doesn't exist"
            cursor.close()
            return error


    return jsonify({})


@app.route('/createAssignment', methods=["GET", "POST"])
def createAssignment():
    data = request.get_json()
    title, description, date = data['title'], data['description'], data['date']
    world, level = data['world'], data['level']

    cursor = conn.cursor()
    # check if the assignment already exists
    cursor.execute('SELECT * from assignment where id =: temp', temp = title)
    data = cursor.fetchone()
    error = None

    if data:  # Failure
        error = "assignment already exists"
        return jsonify({}), 409

    else:  # Success
        cursor.execute('INSERT into assignment(id, description, assignment_date, world, game_level) '
                       'VALUES(:id, :description, :assignment_date, :world, :game_level)',
                       [title, description, date, world, level])
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
        else:
            error = "There was an error viewing the profile."
            return error

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
            error = "There was an error viewing the profile."
            return error

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
        else:
            error = "There was an error viewing the profile."
            return error


    return jsonify(details)


@app.route('/updateProfile', methods=['GET', 'POST'])
def updateProfile():
    # TODO: Get the account type from the session
    # TODO: Get the username from the session
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
    # TODO: Get the account type from the session
    # TODO: Get the username from the session
    account_type = session['account-type']
    username = session['username']

    cursor = conn.cursor()
    if account_type == 'admin':
        # TODO: Change all students under this admin to guest accounts
        #check if the student exists and is in thr group
        cursor.execute('SELECT student.user_name from student, admin WHERE student.student_group = admin.student_group'
                       'AND admin.user_name =: temp', temp = username)
        data = cursor.fetchall()
        if data:
            for student in data:
                cursor.execute('UPDATE student SET student_group = null WHERE user_name =: temp', temp = student[0])
                conn.commit()
                # TODO: Delete this account from admin table
            cursor.execute('DELETE FROM admin WHERE user_name =: temp', temp = username)
            conn.commit()
            cursor.close()
        else:
            error = "No such student in your group"
            return error

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
    if data:
    # TODO: Add a query to get student details
        admin_username = session['username']
        cursor.execute('SELECT student.email, student.progress FROM ADMIN, STUDENT WHERE ADMIN.student_group = STUDENT.student_group '
                       'AND STUDENT.user_name =: username and ADMIN.user_name =: admin_username', [student_username, admin_username])
        data = cursor.fetchone()
        error = None


        if data:
            email = data[0]
            progress = data[1]
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
    #Assume student already exists
    cursor.execute('SELECT assignment FROM student where user_name =: temp', temp = student_username)
    assignments = cursor.fetchall()
    return jsonify({
        'username': student_username,
        'email': email,
        'progress': progress,
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