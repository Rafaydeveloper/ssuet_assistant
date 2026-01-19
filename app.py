from flask import Flask, render_template, request, jsonify, flash, session, redirect, url_for
import config
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
import os
import markdown
import mysql.connector

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = "your_secret_key_here"
app.config.from_object(config)

# -------------------- SSUET Static Responses --------------------
def is_ssuet_query(text):
    keywords = [
        "ssuet", "sir syed", "university",
        "admission", "fee", "department",
        "campus", "contact"
    ]
    text = text.lower()
    return any(word in text for word in keywords)

def get_ssuet_response(user_message):
    msg = user_message.lower()
    if "admission" in msg:
        return "SSUET admissions are announced on the official website. Please check the admissions section for latest updates."
    if "fee" in msg:
        return "Fee structure varies by department. Please refer to the SSUET fee structure page."
    if "department" in msg:
        return "SSUET offers Engineering, Computing, Business, and other departments."
    return "Please visit the official SSUET website for detailed information."

# -------------------- DeepSeek / OpenRouter Client --------------------
deepseek_client = OpenAI(
    api_key=os.getenv("API_KEY"), 
    base_url="https://openrouter.ai/api/v1/"
)

def call_deepseek(user_text):
    """
    Dynamic DeepSeek API call for user messages
    """
    try:
        response = deepseek_client.chat.completions.create(
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[{"role": "user", "content": user_text}]
        )
        # Extract reply safely
        return response.choices[0].message.content
    except Exception as e:
        print("API CALL ERROR:", e)
        return "Sorry, I am temporarily unavailable. Please try again."

# -------------------- Flask Routes --------------------
@app.context_processor
def inject_config():
    return dict(config=config)

@app.route('/')
def home():    
    return redirect(url_for('login'))

@app.route('/login')
def login():
    # If already logged in, redirect to chat
    if 'user_id' in session:
        return redirect(url_for('chat_default'))
    return render_template('user.html')


# DB Functions 

def get_user(user_id):
    """Fetch user info from DB by ID"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email, created_on FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def get_chat_messages(user_id):
    """Fetch chat messages for a specific user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_message, bot_reply, created_on FROM chat_messages WHERE user_id=%s ORDER BY created_on ASC",
        (user_id,)
    )
    chats = cursor.fetchall()
    cursor.close()
    conn.close()
    return chats


def get_user_chats(user_id):
    """Fetch all chats (sidebar) for user"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, title, created_on FROM chats WHERE user_id=%s ORDER BY created_on DESC",
        (user_id,)
    )
    chats = cursor.fetchall()
    cursor.close()
    conn.close()
    return chats


def get_chat_messages(chat_id):
    """Fetch messages for a specific chat"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT user_message, bot_reply, created_on FROM chat_messages WHERE chat_id=%s ORDER BY created_on ASC",
        (chat_id,)
    )
    messages = cursor.fetchall()
    cursor.close()
    conn.close()
    return messages




# DB Operations 

def get_db_connection():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ssuet_assistance",
    charset="utf8mb4",
    collation="utf8mb4_unicode_ci"
)


# User login 

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email').strip()
    password = request.form.get('password').strip()

    if not email or not password:
        flash("Please fill all fields!", "error")
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("User already exists! try other email address", "error")
            return redirect(url_for('login'))
    # Insert user
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (%s, %s)",
            (email, password)
        )
        conn.commit()
        flash("Registration successful! You can now log in.", "success")

    except Exception as e:
        print("DB ERROR:", e)
        flash("Something went wrong!", "error")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('chat_default'))

   # ========================


@app.route('/do_login', methods=['POST'])
def do_login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash("Please fill all fields!", "error")
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email.strip(), password.strip())
        )
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            flash(f"Welcome, {user['email']}!", "success")
            return redirect(url_for('chat_default'))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for('login'))

    except Exception as e:
        print("DB ERROR:", e)
        flash("Something went wrong!", "error")
        return redirect(url_for('login'))

    finally:
        if cursor: cursor.close()
        if conn: conn.close()




# ========================
# Logout
# ========================
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login')) 

# @app.route('/chat')
# def chat_default():
#     if 'user_id' not in session:
#         flash("Please login first!", "error")
#         return redirect(url_for('login'))

#     user_id = session['user_id']

#     # Create new chat automatically
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         "INSERT INTO chats (user_id, title, created_on) VALUES (%s, %s, NOW())",
#         (user_id, "New Chat")
#     )
#     conn.commit()
#     chat_id = cursor.lastrowid
#     cursor.close()
#     conn.close()

#     # Redirect to /chat/<new_chat_id>
#     return redirect(url_for('chat_view', chat_id=chat_id))



@app.route('/chat')
def chat_default():
    if 'user_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user has an existing chat (latest)
    cursor.execute(
        "SELECT id FROM chats WHERE user_id=%s ORDER BY created_on DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    if row:
        chat_id = row[0]  # use existing chat
    else:
        # create new chat only if none exists
        cursor.execute(
            "INSERT INTO chats (user_id, title, created_on) VALUES (%s, %s, NOW())",
            (user_id, "New Chat")
        )
        conn.commit()
        chat_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return redirect(url_for('chat_view', chat_id=chat_id))



@app.route('/new-chat', methods=['POST'])
def new_chat():
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert new chat
    cursor.execute(
        "INSERT INTO chats (user_id, title, created_on) VALUES (%s, %s, NOW())",
        (user_id, "New Chat")
    )
    conn.commit()

    # Get new chat_id
    chat_id = cursor.lastrowid

    cursor.close()
    conn.close()

    # Redirect to /chat/<chat_id>
    return redirect(url_for('chat_view', chat_id=chat_id))





@app.route('/get_reply', methods=["POST"])
def get_reply():
    data = request.get_json()

    user_message = data.get("message", "").strip()
    chat_id = data.get("chat_id")
    user_id = session.get('user_id')

    if not user_message:
        return jsonify({"reply": "Please type a message."})

    if not chat_id:
        return jsonify({"reply": "Chat ID missing!"})

    try:
        ai_reply = call_deepseek(user_message)

        # ✅ Convert ONCE
        html_reply = markdown.markdown(ai_reply)

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO chat_messages (chat_id, user_id, user_message, bot_reply)
            VALUES (%s, %s, %s, %s)
        """, (chat_id, user_id, user_message, html_reply))

        cursor.execute("SELECT title FROM chats WHERE id=%s", (chat_id,))
        row = cursor.fetchone()

        if row and row[0] == "New Chat":
            cursor.execute(
                "UPDATE chats SET title=%s WHERE id=%s",
                (user_message[:30], chat_id)
            )

        conn.commit()
        cursor.close()
        conn.close()

        # ✅ SAME HTML sent to frontend
        return jsonify({"reply": html_reply})

    except Exception as e:
        print("CHAT ERROR:", e)
        return jsonify({"reply": "Sorry, I am temporarily unavailable."})



@app.route('/chat_messages/<int:chat_id>')
def chat_messages(chat_id):
    messages = get_chat_messages(chat_id)
    return jsonify(messages)



@app.route('/chat/<int:chat_id>')
def chat_view(chat_id):
    if 'user_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_chats = get_user_chats(user_id)
    # Get user info
    user = get_user(user_id)  # jo aap pehle define kar chuke ho

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    # Fetch chat info
    cursor.execute("SELECT * FROM chats WHERE id=%s AND user_id=%s", (chat_id, user_id))
    chat_info = cursor.fetchone()

    # Fetch messages
    cursor.execute("""
        SELECT user_message, bot_reply, created_on 
        FROM chat_messages 
        WHERE chat_id=%s AND user_id=%s
        ORDER BY created_on ASC
    """, (chat_id, user_id))
    chat_messages = cursor.fetchall()
    
    
    cursor.close()
    conn.close()

    return render_template(
        'index.html',
        user=user,
        user_id =user_id,
        chat_info=chat_info,
        chats_messages=chat_messages,
        user_chats = user_chats, chat_id = chat_id
    )
@app.route('/delete_chat', methods=["POST"])
def delete_chat():
    data = request.get_json()
    chat_id = data.get("chat_id")
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({"error": "User not logged in"}), 401

    if not chat_id:
        return jsonify({"error": "Chat ID is required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id FROM chats WHERE id=%s AND user_id=%s",
            (chat_id, user_id)
        )
        chat = cursor.fetchone()

        if not chat:
            return jsonify({"error": "Chat not found"}), 404

        cursor.execute("DELETE FROM chat_messages WHERE chat_id=%s", (chat_id,))
        cursor.execute("DELETE FROM chats WHERE id=%s", (chat_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "success": True,
            "redirect_url": "/chat"
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Server error"}), 500









# ADMIN PANEL


@app.route('/admin')
def admin():
    if 'user_id' in session:
        user_id = session['user_id']
        user = get_user(user_id)  # previously defined function

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        # Corrected query
        cursor.execute("SELECT * FROM admin_users WHERE id=%s", (user_id,))
        user_info = cursor.fetchone()
        
         # ✅ Total admins count
        cursor.execute("SELECT COUNT(*) AS total_admins FROM admin_users")
        total_admins = cursor.fetchone()['total_admins']
        
        
        cursor.execute("SELECT COUNT(*) AS total_users FROM users")
        total_users = cursor.fetchone()['total_users']
        
        cursor.execute("SELECT COUNT(*) AS total_content FROM content")
        total_content = cursor.fetchone()['total_content']
        
        
        cursor.close()
        conn.close()

        return render_template('admin/index.html', 
                               user=user,
                               user_info=user_info,
                               total_admins= total_admins,
                               total_users= total_users,
                               total_content= total_content, user_id=user_id
                               )
    return redirect(url_for('admin_login'))


@app.route('/admin/login')
def admin_login():
    # If already logged in, redirect to chat
    if 'user_id' in session:
        return redirect(url_for('admin'))
    return render_template('admin/user.html')


@app.route('/admin-login', methods=['POST'])
def admin__login():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        flash("Please fill all fields!", "error")
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM admin_users WHERE email=%s AND password=%s",
            (email.strip(), password.strip())
        )
        user = cursor.fetchone()

        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            flash(f"Welcome, {user['email']}!", "success")
            return redirect(url_for('admin'))
        else:
            flash("Invalid email or password!", "error")
            return redirect(url_for('admin_login'))

    except Exception as e:
        print("DB ERROR:", e)
        flash("Something went wrong!", "error")
        return redirect(url_for('admin_login'))

    finally:
        if cursor: cursor.close()
        if conn: conn.close()



@app.route('/admin-register', methods=['POST'])
def admin__register():
    email = request.form.get('email').strip()
    password = request.form.get('password').strip()

    if not email or not password:
        flash("Please fill all fields!", "error")
        return redirect(url_for('login'))
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Check if user already exists
        cursor.execute("SELECT * FROM admin_users WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            flash("User already exists! try other email address", "error")
            return redirect(url_for('login'))
    # Insert user
        cursor.execute(
            "INSERT INTO admin_users (email, password) VALUES (%s, %s)",
            (email, password)
        )
        conn.commit()
        flash("Registration successful! You can now log in.", "success")

    except Exception as e:
        print("DB ERROR:", e)
        flash("Something went wrong!", "error")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin'))




@app.route('/admin/logout')
def admin__logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('admin_login')) 

@app.route('/admin/content')
def admin_content():
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    user_id = session['user_id']
    user = get_user(user_id)  # previously defined function
        
    cursor.execute("SELECT * FROM content ORDER BY id DESC")
    contents = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'admin/content/content.html',
        contents=contents,
        user = user
    )

@app.route('/admin/content/add')
def add_content():
    user_id = session['user_id']
    user = get_user(user_id)
    
    return render_template('admin/content/add_content.html', page_title = "Content", user=user)



UPLOAD_FOLDER = 'static/uploads/content'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin/add-content', methods=['POST'])
def add__content():
    title = request.form.get('title')
    short_desc = request.form.get('short_description')
    description = request.form.get('description')
    image = request.files.get('image')

    if not image or not allowed_file(image.filename):
        flash("Invalid image file!", "danger")
        return redirect(url_for('admin_content'))

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    ext = image.filename.rsplit('.', 1)[1].lower()
    filename = f"{int(datetime.now().timestamp())}.{ext}"
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            INSERT INTO content
            (title, short_description, description, image_path, image)
            VALUES (%s, %s, %s,%s, %s)
        """, (
            title,
            short_desc,
            description,
            UPLOAD_FOLDER,
            filename
        ))

        conn.commit()
        flash("Record added successfully!", "success")

    except Exception as e:
        conn.rollback()
        print("MYSQL ERROR:", e)
        flash(str(e), "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_content'))



@app.route('/admin/content/edit/<int:content_id>')
def edit_content(content_id):
    
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))
    user_id = session['user_id']
    user = get_user(user_id)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM content WHERE id=%s", (content_id,))
    content = cursor.fetchone()

    cursor.close()
    conn.close()

    if not content:
        flash("Content not found!", "danger")
        return redirect(url_for('admin_content'))

    return render_template(
        'admin/content/edit_content.html',
        content=content, page_title = "Content",
        user=user
    )


@app.route('/admin/content/update/<int:content_id>', methods=['POST'])
def update_content(content_id):
    title = request.form.get('title')
    short_desc = request.form.get('short_description')
    description = request.form.get('description')
    image = request.files.get('image')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if image and allowed_file(image.filename):
            ext = image.filename.rsplit('.', 1)[1].lower()
            filename = f"{int(datetime.now().timestamp())}.{ext}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            cursor.execute("""
                UPDATE content
                SET title=%s, short_description=%s, description=%s, image=%s
                WHERE id=%s
            """, (title, short_desc, description, filename, content_id))

        else:
            cursor.execute("""
                UPDATE content
                SET title=%s, short_description=%s, description=%s
                WHERE id=%s
            """, (title, short_desc, description, content_id))

        conn.commit()
        flash("Content updated successfully!", "success")

    except Exception as e:
        conn.rollback()
        print("MYSQL ERROR:", e)
        flash("Update failed!", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_content'))

@app.route('/admin/content/delete/<int:content_id>')
def delete_content(content_id):
    if 'user_id' not in session:
        return redirect(url_for('admin_login'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM content WHERE id=%s", (content_id,))
        conn.commit()

        flash("Content deleted successfully!", "success")

    except Exception as e:
        print("MYSQL ERROR:", e)
        flash("Delete failed!", "danger")

    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_content'))


@app.context_processor
def inject_contents():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, title 
            FROM content 
            ORDER BY id ASC
        """)
        contents = cursor.fetchall()

        return dict(global_contents=contents)

    except Exception as e:
        print("Context Processor Error:", e)
        return dict(global_contents=[])

    finally:
        cursor.close()
        conn.close()



@app.route('/content/<int:content_id>')
def view_content(content_id):
    
    if 'user_id' not in session:
        flash("Please login first!", "error")
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = get_user(user_id)
    user_chats = get_user_chats(user_id)
    # Get user info
    user = get_user(user_id)  # jo aap pehle define kar chuke ho

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM content WHERE id = %s", (content_id,))
    content = cursor.fetchone()

    cursor.close()
    conn.close()

    
    return render_template('admin/content/view_content.html', content=content, user_id = user_id, user_chats = user_chats, user=user)

@app.route("/admin/admins")
def admins():
    user_id = session['user_id']
    user = get_user(user_id)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, email, created_on FROM admin_users")
    admin_users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("admin/admins/admins.html", admin_users=admin_users, user=user)




@app.route("/admin/add_admin", methods=["GET", "POST"])
def add_admin():
    
    user_id = session['user_id']
    user = get_user(user_id)
        
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO admin_users (email, password, created_on) VALUES (%s, %s, NOW())",
            (email, password)
        )
        
       
        conn.commit()
        cursor.close()
        conn.close()
        flash("Admin added successfully!", "success")
        return redirect(url_for("admins"))
    return render_template("admin/admins/add_admin.html", page_title = "Admin", user=user)



@app.route("/admin/edit_admin/<int:admin_id>", methods=["GET", "POST"])
def edit_admin(admin_id):
    user_id = session['user_id']
    user = get_user(user_id)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        cursor.execute(
            "UPDATE admin_users SET email=%s, password=%s WHERE id=%s",
            (email, password, admin_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("Admin updated successfully!", "success")
        return redirect(url_for("admins"))
    cursor.execute("SELECT * FROM admin_users WHERE id=%s", (admin_id,))
    admin_info = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("admin/admins/edit_admin.html", admin_info=admin_info, user=user)



@app.route("/admin/delete_admin/<int:admin_id>")
def delete_admin(admin_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin_users WHERE id=%s", (admin_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Admin deleted successfully!", "success")
    return redirect(url_for("admins"))




# Admin users 


@app.route("/admin/chatbot_users")
def chatbot_users():
    if 'user_id' in session:
        user_id = session['user_id']
        user = get_user(user_id)
        print(user_id)
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, email, created_on FROM users")
        user_info = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("admin/chatbot_users/users.html", user_info=user_info, user=user)
    return redirect(url_for('admin_login'))





@app.route("/admin/add_user", methods=["GET", "POST"])
def add_user():
    
    user_id = session['user_id']
    user = get_user(user_id)
        
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password, created_on) VALUES (%s, %s, NOW())",
            (email, password)
        )
        
       
        conn.commit()
        cursor.close()
        conn.close()
        flash("ChatBot User added successfully!", "success")
        return redirect(url_for("chatbot_users"))
    return render_template("admin/chatbot_users/add_user.html", page_title = "ChatBot User", user=user)





@app.route("/admin/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):
    _id = session['user_id']
    user = get_user(_id)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        cursor.execute(
            "UPDATE users SET email=%s, password=%s WHERE id=%s",
            (email, password, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        flash("ChatBot User updated successfully!", "success")
        return redirect(url_for("chatbot_users"))
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user_info = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template("admin/chatbot_users/edit_user.html", user_info=user_info, user=user)



@app.route("/admin/delete_user/<int:user_id>")
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash("Admin deleted successfully!", "success")
    return redirect(url_for("chatbot_users"))




# -------------------- Run Flask App --------------------
if __name__ == '__main__':
    app.run(debug=True)


