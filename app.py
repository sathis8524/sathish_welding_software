import math
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "vmk_roofing_secret_key_2026"

# ---------------------------------------------------------
# SQLITE DATABASE CONFIGURATION
# ---------------------------------------------------------
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'vmk_roofing.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------------------------------------------------
# DATABASE MODELS
# ---------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), default='User')

class CalculationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    calc_type = db.Column(db.String(50), nullable=False)
    customer_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    city = db.Column(db.String(100))
    date = db.Column(db.String(20))
    length = db.Column(db.Float)
    width = db.Column(db.Float)
    total_sqft = db.Column(db.Float)
    roof_type = db.Column(db.String(50))
    roof_type_text = db.Column(db.String(100))
    frame_gap = db.Column(db.Float)
    specific_height = db.Column(db.Float)
    front_pillar_height = db.Column(db.Float)
    back_pillar_height = db.Column(db.Float)
    total_pillars = db.Column(db.Integer)
    pillar_summary = db.Column(db.Text)
    truss_pipes_count = db.Column(db.Integer, default=0)
    main_frame_pipes_count = db.Column(db.Integer, default=0)
    pillar_pipes_count = db.Column(db.Integer, default=0)
    purlin_pipe = db.Column(db.String(100))
    purlin_rows = db.Column(db.Integer)
    purlin_pipes_count = db.Column(db.Integer)
    overall_total_pipes = db.Column(db.Integer)
    sheet_type = db.Column(db.String(100))
    total_sheets = db.Column(db.Integer)
    labor_cost = db.Column(db.String(50))
    full_contract_cost = db.Column(db.String(50))

class WorkerEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(20))
    customer_name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    work_details = db.Column(db.Text)
    total_agreed = db.Column(db.Float, default=0.0)
    received_amount = db.Column(db.Float, default=0.0)
    customer_balance = db.Column(db.Float, default=0.0)
    workers_data = db.Column(db.JSON)

with app.app_context():
    db.create_all()

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ---------------------------------------------------------
# AUTH ROUTES (Database Integrated)
# ---------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        mobile = request.form.get('mobile', '').strip()
        password = request.form.get('password', '').strip()

        if not full_name or not email or not mobile or not password:
            flash("அனைத்து விவரங்களையும் (Fields) நிரப்பவும்!", "danger")
            return render_template('register.html')

        if User.query.filter_by(email=email).first():
            flash("இந்த ஈமெயில் ஐடி ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது!", "warning")
            return render_template('register.html')

        if User.query.filter_by(mobile=mobile).first():
            flash("இந்த மொபைல் எண் ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது!", "warning")
            return render_template('register.html')

        new_user = User(full_name=full_name, email=email, mobile=mobile, password=password, role='User')
        db.session.add(new_user)
        db.session.commit()

        flash("Registration Successful! இப்போது லாகின் செய்யலாம்.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        password = request.form.get('password', '').strip()

        found_user = User.query.filter((User.email == user_input) | (User.mobile == user_input)).first()

        if found_user and found_user.password == password:
            session['user_logged_in'] = True
            session['email'] = found_user.email
            session['full_name'] = found_user.full_name
            flash(f"வரவேற்கிறோம் {found_user.full_name}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("தவறான ஈமெயில்/மொபைல் எண் அல்லது பாஸ்வேர்ட்!", "danger")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        new_password = request.form.get('new_password', '').strip()

        found_user = User.query.filter((User.email == user_input) | (User.mobile == user_input)).first()

        if found_user:
            found_user.password = new_password
            db.session.commit()
            flash("பாஸ்வேர்ட் மாற்றப்பட்டது! லாகின் செய்யவும்.", "success")
            return redirect(url_for('login'))
        else:
            flash("இந்த ஈமெயில் அல்லது மொபைல் எண் பதிவில் இல்லை!", "danger")
            return render_template('forgot_password.html')

    return render_template('forgot_password.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("வெற்றிகரமாக வெளியேறிவிட்டீர்கள்!", "info")
    return redirect(url_for('login'))

# ---------------------------------------------------------
# CALCULATOR ROUTES
# ---------------------------------------------------------
@app.route('/truss_calculator', methods=['GET', 'POST'])
def truss_calculator():
    result = None
    if request.method == 'POST':
        try:
            customer_name = request.form.get('customer_name', 'Guest Customer')
            location = request.form.get('location', '')
            city = request.form.get('city', '')

            length = float(request.form.get('length', 0))
            width = float(request.form.get('width', 0))
            roof_type = request.form.get('roof_type', 'double_slope')
            frame_gap = float(request.form.get('frame_gap', 4))

            specific_height = float(request.form.get('specific_height', 3))
            front_pillar_height = float(request.form.get('front_pillar_height', 10))
            back_pillar_height = float(request.form.get('back_pillar_height', 8))

            purlin_pipe = request.form.get('purlin_pipe', '1.5x1.5 Square Pipe')
            purlin_gap = float(request.form.get('purlin_gap', 3))
            sheet_type = request.form.get('sheet_type', 'Color Coated Sheet')

            labor_rate_sqft = float(request.form.get('labor_rate', 25))
            full_contract_rate_sqft = float(request.form.get('contract_rate', 180))

            total_sqft = length * width
            num_frames = math.ceil(length / frame_gap) + 1

            if roof_type == 'double_slope':
                half_width = width / 2.0
                rafter_length = math.sqrt((half_width ** 2) + (specific_height ** 2))
                truss_pipe_length_per_frame = (rafter_length * 2) + width + (specific_height * 1.5)
                roof_type_text = "A-Type Double Slope Truss"
            elif roof_type == 'single_slope':
                rafter_length = math.sqrt((width ** 2) + (specific_height ** 2))
                truss_pipe_length_per_frame = rafter_length + width + specific_height
                roof_type_text = "Single Slope Truss"
            else:
                rafter_length = width * 1.05
                truss_pipe_length_per_frame = (rafter_length * 2) + (specific_height * 2)
                roof_type_text = "Curved / Box Truss"

            total_truss_feet = truss_pipe_length_per_frame * num_frames
            truss_pipes_count = math.ceil((total_truss_feet * 1.10) / 20.0)

            support_type = request.form.get('support_type', 'all_pillars')
            pillars_one_side = int(math.ceil(length / 10.0)) + 1 if length > 0 else 2

            if roof_type == 'double_slope':
                total_pillars = pillars_one_side if support_type == 'one_side_wall' else pillars_one_side * 2
                total_pillar_feet = total_pillars * front_pillar_height
                pillar_summary = f"மொத்தம் {total_pillars} தூண்கள் (உயரம்: {front_pillar_height} அடி)"
            else:
                if support_type == 'one_side_wall':
                    total_pillars = pillars_one_side
                    total_pillar_feet = total_pillars * back_pillar_height
                    pillar_summary = f"மொத்தம் {total_pillars} தூண்கள் (உயரம்: {back_pillar_height} அடி)"
                else:
                    total_pillars = pillars_one_side * 2
                    total_pillar_feet = (pillars_one_side * front_pillar_height) + (pillars_one_side * back_pillar_height)
                    pillar_summary = f"உயரமான தூண் ({front_pillar_height} அடி): {pillars_one_side}, குறைவான தூண் ({back_pillar_height} அடி): {pillars_one_side}"

            pillar_pipes_count = math.ceil((total_pillar_feet * 1.05) / 20.0) if total_pillar_feet > 0 else 0

            total_slope_width = rafter_length * (2 if roof_type == 'double_slope' else 1)
            purlin_rows = math.ceil(total_slope_width / purlin_gap) + 1
            total_purlin_feet = purlin_rows * length
            purlin_pipes_count = math.ceil((total_purlin_feet * 1.05) / 20.0)

            overall_total_pipes = truss_pipes_count + pillar_pipes_count + purlin_pipes_count

            sheet_width_coverage = 3.0
            sheets_per_row = math.ceil(length / sheet_width_coverage)
            total_sheets = sheets_per_row * (2 if roof_type == 'double_slope' else 1)

            labor_cost = round(total_sqft * labor_rate_sqft)
            full_contract_cost = round(total_sqft * full_contract_rate_sqft)

            new_calc = CalculationHistory(
                user_email=session.get('email', 'guest'),
                calc_type='Truss',
                customer_name=customer_name,
                location=location,
                city=city,
                date=datetime.now().strftime("%d-%m-%Y"),
                length=length,
                width=width,
                total_sqft=total_sqft,
                roof_type=roof_type,
                roof_type_text=roof_type_text,
                frame_gap=frame_gap,
                specific_height=specific_height,
                front_pillar_height=front_pillar_height,
                back_pillar_height=back_pillar_height,
                total_pillars=total_pillars,
                pillar_summary=pillar_summary,
                truss_pipes_count=truss_pipes_count,
                pillar_pipes_count=pillar_pipes_count,
                purlin_pipe=purlin_pipe,
                purlin_rows=purlin_rows,
                purlin_pipes_count=purlin_pipes_count,
                overall_total_pipes=overall_total_pipes,
                sheet_type=sheet_type,
                total_sheets=total_sheets,
                labor_cost=f"{labor_cost:,}",
                full_contract_cost=f"{full_contract_cost:,}"
            )
            db.session.add(new_calc)
            db.session.commit()
            result = new_calc

        except Exception as e:
            flash(f"பிழை ஏற்பட்டது: {str(e)}")

    return render_template('truss_calculator.html', result=result)

@app.route('/roof_calculator', methods=['GET', 'POST'])
def roof_calculator():
    result = None
    if request.method == 'POST':
        try:
            customer_name = request.form.get('customer_name', 'Guest Customer')
            location = request.form.get('location', '')
            city = request.form.get('city', '')

            length = float(request.form.get('length', 0))
            width = float(request.form.get('width', 0))
            roof_type = request.form.get('roof_type', 'single_slope')
            frame_gap = float(request.form.get('frame_gap', 4))

            specific_height = float(request.form.get('specific_height', 2))
            front_pillar_height = float(request.form.get('front_pillar_height', 10))
            back_pillar_height = float(request.form.get('back_pillar_height', 8))

            purlin_pipe = request.form.get('purlin_pipe', '1.5x1.5 Square Pipe')
            purlin_gap = float(request.form.get('purlin_gap', 3))
            sheet_type = request.form.get('sheet_type', 'Color Coated Sheet')

            labor_rate_sqft = float(request.form.get('labor_rate', 20))
            full_contract_rate_sqft = float(request.form.get('contract_rate', 150))

            total_sqft = length * width
            num_frames = math.ceil(length / frame_gap) + 1

            if roof_type == 'double_slope':
                half_width = width / 2.0
                rafter_length = math.sqrt((half_width ** 2) + (specific_height ** 2))
                main_frame_pipes_feet = rafter_length * 2 * num_frames
                roof_type_text = "Double Slope Roofing"
            elif roof_type == 'single_slope':
                rafter_length = math.sqrt((width ** 2) + (specific_height ** 2))
                main_frame_pipes_feet = rafter_length * num_frames
                roof_type_text = "Single Slope Roofing"
            else:
                rafter_length = width * 1.05
                main_frame_pipes_feet = rafter_length * num_frames
                roof_type_text = "Flat / Curved Roofing"

            main_frame_pipes_count = math.ceil((main_frame_pipes_feet * 1.08) / 20.0)

            support_type = request.form.get('support_type', 'all_pillars')
            pillars_one_side = int(math.ceil(length / 10.0)) + 1 if length > 0 else 2

            if roof_type == 'double_slope':
                total_pillars = pillars_one_side if support_type == 'one_side_wall' else pillars_one_side * 2
                total_pillar_feet = total_pillars * front_pillar_height
                pillar_summary = f"மொத்தம் {total_pillars} தூண்கள் (உயரம்: {front_pillar_height} அடி)"
            else:
                if support_type == 'one_side_wall':
                    total_pillars = pillars_one_side
                    total_pillar_feet = total_pillars * back_pillar_height
                    pillar_summary = f"மொத்தம் {total_pillars} தூண்கள் (உயரம்: {back_pillar_height} அடி)"
                else:
                    total_pillars = pillars_one_side * 2
                    total_pillar_feet = (pillars_one_side * front_pillar_height) + (pillars_one_side * back_pillar_height)
                    pillar_summary = f"உயரமான தூண் ({front_pillar_height} அடி): {pillars_one_side}, குறைவான தூண் ({back_pillar_height} அடி): {pillars_one_side}"

            pillar_pipes_count = math.ceil((total_pillar_feet * 1.05) / 20.0) if total_pillar_feet > 0 else 0

            total_slope_width = rafter_length * (2 if roof_type == 'double_slope' else 1)
            purlin_rows = math.ceil(total_slope_width / purlin_gap) + 1
            total_purlin_feet = purlin_rows * length
            purlin_pipes_count = math.ceil((total_purlin_feet * 1.05) / 20.0)

            overall_total_pipes = main_frame_pipes_count + pillar_pipes_count + purlin_pipes_count

            sheet_width_coverage = 3.0
            sheets_per_row = math.ceil(length / sheet_width_coverage)
            total_sheets = sheets_per_row * (2 if roof_type == 'double_slope' else 1)

            labor_cost = round(total_sqft * labor_rate_sqft)
            full_contract_cost = round(total_sqft * full_contract_rate_sqft)

            new_calc = CalculationHistory(
                user_email=session.get('email', 'guest'),
                calc_type='Roofing',
                customer_name=customer_name,
                location=location,
                city=city,
                date=datetime.now().strftime("%d-%m-%Y"),
                length=length,
                width=width,
                total_sqft=total_sqft,
                roof_type=roof_type,
                roof_type_text=roof_type_text,
                frame_gap=frame_gap,
                specific_height=specific_height,
                front_pillar_height=front_pillar_height,
                back_pillar_height=back_pillar_height,
                total_pillars=total_pillars,
                pillar_summary=pillar_summary,
                main_frame_pipes_count=main_frame_pipes_count,
                pillar_pipes_count=pillar_pipes_count,
                purlin_pipe=purlin_pipe,
                purlin_rows=purlin_rows,
                purlin_pipes_count=purlin_pipes_count,
                overall_total_pipes=overall_total_pipes,
                sheet_type=sheet_type,
                total_sheets=total_sheets,
                labor_cost=f"{labor_cost:,}",
                full_contract_cost=f"{full_contract_cost:,}"
            )
            db.session.add(new_calc)
            db.session.commit()
            result = new_calc

        except Exception as e:
            flash(f"பிழை ஏற்பட்டது: {str(e)}")

    return render_template('roof_calculator.html', result=result)

# ---------------------------------------------------------
# WORKER ENTRY ROUTE
# ---------------------------------------------------------
@app.route('/worker_entry', methods=['GET', 'POST'])
@app.route('/attendance', methods=['GET', 'POST'])
def worker_entry():
    if not session.get('user_logged_in'):
        flash("பணியாளர் பதிவை அணுக முதலில் லாகின் செய்யவும்!", "warning")
        return redirect(url_for('login'))

    current_user_email = session.get('email')

    if request.method == 'POST':
        try:
            attendance_date = request.form.get('attendance_date') or datetime.now().strftime("%Y-%m-%d")
            customer_name = request.form.get('customer_name', '').strip()
            location = request.form.get('location', '').strip()
            work_details = request.form.get('work_details', '').strip()

            total_agreed = float(request.form.get('total_agreed') or 0)
            received_amount = float(request.form.get('received_amount') or 0)
            customer_balance = total_agreed - received_amount

            workers_list = []
            for i in range(1, 6):
                w_name = request.form.get(f'worker{i}_name', '').strip()
                if w_name:
                    w_wage = float(request.form.get(f'worker{i}_wage') or 0)
                    w_paid = float(request.form.get(f'worker{i}_paid') or 0)
                    w_balance = w_wage - w_paid

                    workers_list.append({
                        'name': w_name,
                        'wage': w_wage,
                        'paid': w_paid,
                        'balance': w_balance
                    })

            if workers_list or customer_name:
                new_entry = WorkerEntry(
                    user_email=current_user_email,
                    date=attendance_date,
                    customer_name=customer_name,
                    location=location,
                    work_details=work_details,
                    total_agreed=total_agreed,
                    received_amount=received_amount,
                    customer_balance=customer_balance,
                    workers_data=workers_list
                )
                db.session.add(new_entry)
                db.session.commit()

            return redirect(url_for('worker_entry'))

        except Exception as e:
            print(f"Error saving entry: {e}")

    user_workers = WorkerEntry.query.filter_by(user_email=current_user_email).order_by(WorkerEntry.id.desc()).all()
    today_str = datetime.now().strftime("%Y-%m-%d")
    return render_template('worker_entry.html', workers=user_workers, today_date=today_str)

@app.route('/history')
def history():
    if not session.get('user_logged_in'):
        flash("வரலாற்றைப் பார்க்க முதலில் லாகின் செய்யவும்!", "warning")
        return redirect(url_for('login'))

    current_user_email = session.get('email')
    user_history = CalculationHistory.query.filter_by(user_email=current_user_email).order_by(CalculationHistory.id.desc()).all()
    return render_template('history.html', history=user_history)

@app.route('/estimate_detail/<int:item_id>')
def estimate_detail(item_id):
    item = CalculationHistory.query.get(item_id)
    if item:
        return render_template('estimate_detail.html', item=item)
    else:
        flash("கஸ்டமர் விவரங்கள் கிடைக்கவில்லை!")
        return redirect(url_for('history'))

# ---------------------------------------------------------
# DEVELOPER CONTROL ROUTE
# ---------------------------------------------------------
@app.route('/developer_control', methods=['GET', 'POST'])
def developer_control():
    authenticated = session.get('developer_authenticated', False)
    msg = None

    if request.method == 'POST':
        master_key = request.form.get('master_key')
        action = request.form.get('action')

        if master_key:
            if master_key == '8524':
                session['developer_authenticated'] = True
                authenticated = True
                msg = "Super Developer Authentication Successful!"
            else:
                msg = "❌ Invalid Master Secret Key!"

        elif authenticated:
            if action == 'save_settings':
                msg = "விகிதங்கள் சேமிக்கப்பட்டன!"
            elif action == 'clear_history':
                CalculationHistory.query.delete()
                db.session.commit()
                msg = "அனைத்து மதிப்பீட்டு வரலாறுகளும் அழிக்கப்பட்டன!"
            elif action == 'clear_workers':
                WorkerEntry.query.delete()
                db.session.commit()
                msg = "அனைத்து பணிப் பதிவுகளும் அழிக்கப்பட்டன!"
            elif action == 'clear_all':
                CalculationHistory.query.delete()
                WorkerEntry.query.delete()
                db.session.commit()
                msg = "அனைத்து தரவுகளும் ரீசெட் செய்யப்பட்டன!"

    all_users = User.query.all()
    all_worker_logs = WorkerEntry.query.order_by(WorkerEntry.id.desc()).all()

    total_pending = sum(item.customer_balance for item in all_worker_logs if item.customer_balance)
    stats = {
        'total_estimates': CalculationHistory.query.count(),
        'total_worker_entries': WorkerEntry.query.count(),
        'total_pending_balance': f"{total_pending:,.2f}"
    }

    return render_template(
        'developer_control.html',
        authenticated=authenticated,
        msg=msg,
        users=all_users,
        logs=all_worker_logs,
        stats=stats
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)