import pymysql

#from app import app
#from tables import Results
#from db_config import mysql

from flask_table import Table, Col, LinkCol
from flask import flash, render_template, request, redirect
from werkzeug import generate_password_hash, check_password_hash
from flask import Flask
from flaskext.mysql import MySQL



#************* (1) we can also put this in separate file named as "app.py" *************
#Initializing Flask Application
app = Flask(__name__)
app.secret_key = "secret key"




#************* (2) we can also put this in separate file named as "db_config.py" *************
#Initializing database Object
mysql = MySQL() 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'saad'
app.config['MYSQL_DATABASE_DB'] = 'test_db'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)



#************* (3) we can also put this in separate file named as "tables.py" *************
#Class Results shows a list of user data into tabular format on HTML template file in home page. 
#Notice how we have added two links for updating and deleting records from table data using LinkCol from flask module.
#What we want to show as a header in the HTML table. 
#We don’t want to show user_id and user_password and that’s why we use show=False as a second argument.
#We have added two links for update and delete at the rightmost column for updating and deleting existing user.
class Results(Table):
    user_id = Col('Id', show=False)
    user_name = Col('Name')
    user_email = Col('Email')
    user_password = Col('Password', show=False)
    edit = LinkCol('Edit', 'edit_view', url_kwargs=dict(id='user_id'))
    delete = LinkCol('Delete', 'delete_user', url_kwargs=dict(id='user_id'))



#************* (4) we can also put these routes in separate file named as "main.py",
# But here we have chosen to put all the code in single file *************
#Adding routes for (add), (update), (delete)
@app.route('/new_user')
def add_user_view():
	return render_template('add.html')
		
@app.route('/add', methods=['POST'])
def add_user():
	try:		
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']
		# validate the received values
		if _name and _email and _password and request.method == 'POST':
			#do not save password as a plain text
			_hashed_password = generate_password_hash(_password)
			# save edits
			sql = "INSERT INTO tbl_user(user_name, user_email, user_password) VALUES(%s, %s, %s)"
			data = (_name, _email, _hashed_password,)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			flash('User added successfully!')
			return redirect('/')
		else:
			return 'Error while adding user'
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
		
@app.route('/')
def users():
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM tbl_user")
		rows = cursor.fetchall()
		table = Results(rows)
		table.border = True
		return render_template('users.html', table=table)
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()

@app.route('/edit/<int:id>')
def edit_view(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor(pymysql.cursors.DictCursor)
		cursor.execute("SELECT * FROM tbl_user WHERE user_id=%s", id)
		row = cursor.fetchone()
		if row:
			return render_template('edit.html', row=row)
		else:
			return 'Error loading #{id}'.format(id=id)
	except Exception as e:
		print(e)
	finally:
		cursor.close()
		conn.close()

@app.route('/update', methods=['POST'])
def update_user():
	try:		
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']
		_id = request.form['id']
		# validate the received values
		if _name and _email and _password and _id and request.method == 'POST':
			#do not save password as a plain text
			_hashed_password = generate_password_hash(_password)
			# save edits
			sql = "UPDATE tbl_user SET user_name=%s, user_email=%s, user_password=%s WHERE user_id=%s"
			data = (_name, _email, _hashed_password, _id,)
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute(sql, data)
			conn.commit()
			flash('User updated successfully!')
			return redirect('/')
		else:
			return 'Error while updating user'
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
		
@app.route('/delete/<int:id>')
def delete_user(id):
	try:
		conn = mysql.connect()
		cursor = conn.cursor()
		cursor.execute("DELETE FROM tbl_user WHERE user_id=%s", (id,))
		conn.commit()
		flash('User deleted successfully!')
		return redirect('/')
	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		conn.close()
	

if __name__ == "__main__":
    app.run()