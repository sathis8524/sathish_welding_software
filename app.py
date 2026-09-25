import math
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = "vmk_roofing_secret_key_2026"

# ---------------------------------------------------------
# GLOBAL IN-MEMORY DATABASE
# ---------------------------------------------------------
HISTORY_DATA = []
WORKER_DATA = []

# ---------------------------------------------------------
# ROUTES
# ---------------------------------------------------------
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/home')
def home():
    return render_template('home.html')


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         password = request.form.get('password')
#         return redirect(url_for('dashboard'))
#     return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ---------------------------------------------------------
# USERS DATABASE & AUTH ROUTES
# ---------------------------------------------------------

# பயனர்களின் தரவை சேமிக்க (Dummy In-Memory Data)
USERS_DB = {
    'sathish_admin': {
        'full_name': 'Sathish V',
        'email': 'sathish@example.com',
        'mobile': '9876543210',
        'password': '123',
        'role': 'Super Developer'
    }
}

# 1. REGISTER ROUTE (புதிய பயனர் பதிவு)
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

        # ஈமெயில் அல்லது மொபைல் ஏற்கனவே உள்ளதா என சரிபார்த்தல்
        for user in USERS_DB.values():
            if user.get('email') == email:
                flash("இந்த ஈமெயில் ஐடி ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது!", "warning")
                return render_template('register.html')
            if user.get('mobile') == mobile:
                flash("இந்த மொபைல் எண் ஏற்கனவே பதிவு செய்யப்பட்டுள்ளது!", "warning")
                return render_template('register.html')

        # புதிய பயனரைச் சேமித்தல்
        USERS_DB[email] = {
            'full_name': full_name,
            'email': email,
            'mobile': mobile,
            'password': password,
            'role': 'User'
        }

        flash("Registration Successful! பதிவு வெற்றிகரமாக முடிந்தது. இப்போது லாகின் செய்யலாம்.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')


# 2. LOGIN ROUTE (ஈமெயில் அல்லது மொபைல் எண் + பாஸ்வேர்ட் வைத்து லாகின்)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()  # Email or Mobile
        password = request.form.get('password', '').strip()

        found_user = None
        for user in USERS_DB.values():
            if (user.get('email') == user_input or user.get('mobile') == user_input) and user.get('password') == password:
                found_user = user
                break

        if found_user:
            session['user_logged_in'] = True
            session['email'] = found_user['email']
            session['full_name'] = found_user['full_name']
            flash(f"வரவேற்கிறோம் {found_user['full_name']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("தவறான ஈமெயில்/மொபைல் எண் அல்லது பாஸ்வேர்ட்!", "danger")
            return render_template('login.html')

    return render_template('login.html')


# 3. FORGOT PASSWORD ROUTE (பாஸ்வேர்ட் ரீசெட் செய்யும் பகுதி)
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip() # Email or Mobile
        new_password = request.form.get('new_password', '').strip()

        found_user = None
        for user in USERS_DB.values():
            if user.get('email') == user_input or user.get('mobile') == user_input:
                found_user = user
                break

        if found_user:
            # புதிய பாஸ்வேர்ட்டை அப்டேட் செய்தல்
            found_user['password'] = new_password
            flash("உங்கள் பாஸ்வேர்ட் வெற்றிகரமாக மாற்றப்பட்டது! புதிய பாஸ்வேர்ட் மூலம் லாகின் செய்யவும்.", "success")
            return redirect(url_for('login'))
        else:
            flash("இந்த ஈமெயில் அல்லது மொபைல் எண் பதிவில் இல்லை!", "danger")
            return render_template('forgot_password.html')

    return render_template('forgot_password.html')


# 4. LOGOUT ROUTE (வெளியேறுதல்)
@app.route('/logout')
def logout():
    session.clear()
    flash("வெற்றிகரமாக வெளியேறிவிட்டீர்கள்!", "info")
    return redirect(url_for('login'))

# ---------------------------------------------------------
# 1. TRUSS CALCULATOR ROUTE
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

            # Calculation Logic
            total_sqft = length * width
            num_frames = math.ceil(length / frame_gap) + 1

            # Rafter length calculation
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

            # --- Pillars Calculation (10 feet spacing & High/Low Slope logic) ---
            support_type = request.form.get('support_type', 'all_pillars')
            pillars_one_side = int(math.ceil(length / 10.0)) + 1 if length > 0 else 2

            if roof_type == 'double_slope':
                if support_type == 'one_side_wall':
                    total_pillars = pillars_one_side
                else:
                    total_pillars = pillars_one_side * 2
                total_pillar_feet = total_pillars * front_pillar_height
                pillar_summary = f"மொத்தம் {total_pillars} தூண்கள் (உயரம்: {front_pillar_height} அடி)"
            else:
                if support_type == 'one_side_wall':
                    total_pillars = pillars_one_side
                    total_pillar_feet = total_pillars * back_pillar_height
                    pillar_summary = f"மொத்தம் {total_pillars} தூண்கள் (உயரம்: {back_pillar_height} அடி)"
                else:
                    high_pillars_count = pillars_one_side
                    low_pillars_count = pillars_one_side
                    total_pillars = high_pillars_count + low_pillars_count
                    total_pillar_feet = (high_pillars_count * front_pillar_height) + (low_pillars_count * back_pillar_height)
                    pillar_summary = f"உயரமான தூண் ({front_pillar_height} அடி): {high_pillars_count} எண்கள், குறைவான தூண் ({back_pillar_height} அடி): {low_pillars_count} எண்கள் (மொத்தம்: {total_pillars} தூண்கள்)"

            pillar_pipes_count = math.ceil((total_pillar_feet * 1.05) / 20.0) if total_pillar_feet > 0 else 0

            # Purlins
            total_slope_width = rafter_length * (2 if roof_type == 'double_slope' else 1)
            purlin_rows = math.ceil(total_slope_width / purlin_gap) + 1
            total_purlin_feet = purlin_rows * length
            purlin_pipes_count = math.ceil((total_purlin_feet * 1.05) / 20.0)

            overall_total_pipes = truss_pipes_count + pillar_pipes_count + purlin_pipes_count

            # Sheets
            sheet_width_coverage = 3.0
            sheets_per_row = math.ceil(length / sheet_width_coverage)
            total_sheets = sheets_per_row * (2 if roof_type == 'double_slope' else 1)

            # Costs
            labor_cost = round(total_sqft * labor_rate_sqft)
            full_contract_cost = round(total_sqft * full_contract_rate_sqft)

            result = {
                'id': len(HISTORY_DATA),
                'user_email': session.get('email', 'guest'),  # லாகின் செய்த பயனரின் ஈமெயில்
                'calc_type': 'Truss',
                'customer_name': customer_name,
                'location': location,
                'city': city,
                'date': datetime.now().strftime("%d-%m-%Y"),
                'length': length,
                'width': width,
                'total_sqft': total_sqft,
                'roof_type': roof_type,
                'roof_type_text': roof_type_text,
                'frame_gap': frame_gap,
                'specific_height': specific_height,
                'front_pillar_height': front_pillar_height,
                'back_pillar_height': back_pillar_height,
                'total_pillars': total_pillars,
                'pillar_summary': pillar_summary,
                'truss_pipes_count': truss_pipes_count,
                'pillar_pipes_count': pillar_pipes_count,
                'purlin_pipe': purlin_pipe,
                'purlin_rows': purlin_rows,
                'purlin_pipes_count': purlin_pipes_count,
                'overall_total_pipes': overall_total_pipes,
                'sheet_type': sheet_type,
                'total_sheets': total_sheets,
                'labor_cost': f"{labor_cost:,}",
                'full_contract_cost': f"{full_contract_cost:,}"
            }

            HISTORY_DATA.insert(0, result)

        except Exception as e:
            flash(f"பிழை ஏற்பட்டது: {str(e)}")

    return render_template('truss_calculator.html', result=result)


# ---------------------------------------------------------
# 2. ROOF CALCULATOR ROUTE
# ---------------------------------------------------------
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

            # --- Pillars Calculation (10 feet spacing & High/Low Slope logic) ---
            support_type = request.form.get('support_type', 'all_pillars')
            pillars_one_side = int(math.ceil(length / 10.0)) + 1 if length > 0 else 2

            if roof_type == 'double_slope':
                if support_type == 'one_side_wall':
                    total_pillars = pillars_one_side
                else:
                    total_pillars = pillars_one_side * 2
                total_pillar_feet = total_pillars * front_pillar_height
                pillar_summary = f"மொத்தம் {total_pillars} தூண்கள் (உயரம்: {front_pillar_height} அடி)"
            else:
                if support_type == 'one_side_wall':
                    total_pillars = pillars_one_side
                    total_pillar_feet = total_pillars * back_pillar_height
                    pillar_summary = f"மொத்தம் {total_pillars} தூண்கள் (உயரம்: {back_pillar_height} அடி)"
                else:
                    high_pillars_count = pillars_one_side
                    low_pillars_count = pillars_one_side
                    total_pillars = high_pillars_count + low_pillars_count
                    total_pillar_feet = (high_pillars_count * front_pillar_height) + (low_pillars_count * back_pillar_height)
                    pillar_summary = f"உயரமான தூண் ({front_pillar_height} அடி): {high_pillars_count} எண்கள், குறைவான தூண் ({back_pillar_height} அடி): {low_pillars_count} எண்கள் (மொத்தம்: {total_pillars} தூண்கள்)"

            pillar_pipes_count = math.ceil((total_pillar_feet * 1.05) / 20.0) if total_pillar_feet > 0 else 0

            # Purlins
            total_slope_width = rafter_length * (2 if roof_type == 'double_slope' else 1)
            purlin_rows = math.ceil(total_slope_width / purlin_gap) + 1
            total_purlin_feet = purlin_rows * length
            purlin_pipes_count = math.ceil((total_purlin_feet * 1.05) / 20.0)

            overall_total_pipes = main_frame_pipes_count + pillar_pipes_count + purlin_pipes_count

            # Sheets
            sheet_width_coverage = 3.0
            sheets_per_row = math.ceil(length / sheet_width_coverage)
            total_sheets = sheets_per_row * (2 if roof_type == 'double_slope' else 1)

            labor_cost = round(total_sqft * labor_rate_sqft)
            full_contract_cost = round(total_sqft * full_contract_rate_sqft)

            result = {
                'id': len(HISTORY_DATA),
                'user_email': session.get('email', 'guest'),  # லாகின் செய்த பயனரின் ஈமெயில்
                'calc_type': 'Roofing',
                'customer_name': customer_name,
                'location': location,
                'city': city,
                'date': datetime.now().strftime("%d-%m-%Y"),
                'length': length,
                'width': width,
                'total_sqft': total_sqft,
                'roof_type': roof_type,
                'roof_type_text': roof_type_text,
                'frame_gap': frame_gap,
                'specific_height': specific_height,
                'front_pillar_height': front_pillar_height,
                'back_pillar_height': back_pillar_height,
                'total_pillars': total_pillars,
                'pillar_summary': pillar_summary,
                'main_frame_pipes_count': main_frame_pipes_count,
                'pillar_pipes_count': pillar_pipes_count,
                'purlin_pipe': purlin_pipe,
                'purlin_rows': purlin_rows,
                'purlin_pipes_count': purlin_pipes_count,
                'overall_total_pipes': overall_total_pipes,
                'sheet_type': sheet_type,
                'total_sheets': total_sheets,
                'labor_cost': f"{labor_cost:,}",
                'full_contract_cost': f"{full_contract_cost:,}"
            }

            HISTORY_DATA.insert(0, result)

        except Exception as e:
            flash(f"பிழை ஏற்பட்டது: {str(e)}")

    return render_template('roof_calculator.html', result=result)


# ---------------------------------------------------------
# 3. WORKER ENTRY ROUTE
# ---------------------------------------------------------
@app.route('/worker_entry', methods=['GET', 'POST'])
@app.route('/attendance', methods=['GET', 'POST'])
def worker_entry():
    if request.method == 'POST':
        try:
            attendance_date = request.form.get('attendance_date') or datetime.now().strftime("%Y-%m-%d")
            customer_name = request.form.get('customer_name', '')
            location = request.form.get('location', '')
            work_details = request.form.get('work_details', '')

            total_agreed = float(request.form.get('total_agreed') or 0)
            received_amount = float(request.form.get('received_amount') or 0)
            customer_balance = total_agreed - received_amount

            workers_list = []
            for i in range(1, 6):
                w_name = request.form.get(f'worker{i}_name', '').strip()
                if w_name:
                    w_status = request.form.get(f'worker{i}_status', 'Present')
                    w_wage = float(request.form.get(f'worker{i}_wage') or 0)
                    w_advance = float(request.form.get(f'worker{i}_advance') or 0)
                    w_balance = (w_wage - w_advance) if w_status == 'Present' else (0 - w_advance)

                    workers_list.append({
                        'name': w_name,
                        'status': w_status,
                        'wage': w_wage,
                        'advance': w_advance,
                        'balance': w_balance
                    })

            if workers_list or customer_name:
                WORKER_DATA.insert(0, {
                    'date': attendance_date,
                    'customer_name': customer_name,
                    'location': location,
                    'work_details': work_details,
                    'total_agreed': total_agreed,
                    'received_amount': received_amount,
                    'customer_balance': customer_balance,
                    'workers': workers_list
                })

            return redirect(url_for('worker_entry'))

        except Exception as e:
            print(f"Error saving entry: {e}")

    today_str = datetime.now().strftime("%Y-%m-%d")
    return render_template('worker_entry.html', workers=WORKER_DATA, today_date=today_str)


# ---------------------------------------------------------
# 4. HISTORY ROUTE
# ---------------------------------------------------------
@app.route('/history')
def history():
    # பயனர் லாகின் செய்யவில்லை என்றால் லாகின் பக்கத்திற்கு மாற்றும்
    if not session.get('user_logged_in'):
        flash("வரலாற்றைப் பார்க்க முதலில் லாகின் செய்யவும்!", "warning")
        return redirect(url_for('login'))

    current_user_email = session.get('email')
    
    # லாகின் செய்த நபரின் எஸ்டிமேட்களை மட்டும் பிரித்தெடுக்கும்
    user_history = [item for item in HISTORY_DATA if item.get('user_email') == current_user_email]

    return render_template('history.html', history=user_history)

# ---------------------------------------------------------
# 5. ESTIMATE DETAIL ROUTE
# ---------------------------------------------------------
@app.route('/estimate_detail/<int:item_id>')
def estimate_detail(item_id):
    if 0 <= item_id < len(HISTORY_DATA):
        item = HISTORY_DATA[item_id]
        return render_template('estimate_detail.html', item=item)
    else:
        flash("கஸ்டமர் விவரங்கள் கிடைக்கவில்லை!")
        return redirect(url_for('history'))


# ---------------------------------------------------------
# 6. MASTER DEVELOPER CONTROL ROUTE
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
                truss_labor_rate = float(request.form.get('truss_labor_rate') or 25)
                truss_contract_rate = float(request.form.get('truss_contract_rate') or 180)
                roof_labor_rate = float(request.form.get('roof_labor_rate') or 20)
                roof_contract_rate = float(request.form.get('roof_contract_rate') or 150)
                new_password = request.form.get('new_password')

                app.config['DEFAULT_RATES'] = {
                    'truss_labor': truss_labor_rate,
                    'truss_contract': truss_contract_rate,
                    'roof_labor': roof_labor_rate,
                    'roof_contract': roof_contract_rate
                }

                if new_password:
                    app.config['ADMIN_PASSWORD'] = new_password
                    msg = "பாஸ்வேர்ட் மற்றும் விகிதங்கள் வெற்றிகரமாக சேமிக்கப்பட்டன!"
                else:
                    msg = "இயல்புநிலை விகிதங்கள் சேமிக்கப்பட்டன!"

            elif action == 'clear_history':
                HISTORY_DATA.clear()
                msg = "அனைத்து மதிப்பீட்டு வரலாறுகளும் அழிக்கப்பட்டன!"

            elif action == 'clear_workers':
                WORKER_DATA.clear()
                msg = "அனைத்து பணிப் பதிவுகளும் அழிக்கப்பட்டன!"

            elif action == 'clear_all':
                HISTORY_DATA.clear()
                WORKER_DATA.clear()
                msg = "VMK Roofing ஆப்பின் அனைத்து தரவுகளும் வெற்றிகரமாக ரீசெட் செய்யப்பட்டன!"

    # உண்மையாக பதிவு செய்த பயனர்கள் (USERS_DB) + Dummy Admin பயனர்களை ஒன்றாகக் காட்டுதல்
    all_users = list(USERS_DB.values()) if 'USERS_DB' in globals() else []

    total_pending = sum(item.get('customer_balance', 0) for item in WORKER_DATA)
    stats = {
        'total_estimates': len(HISTORY_DATA),
        'total_worker_entries': len(WORKER_DATA),
        'total_pending_balance': f"{total_pending:,}"
    }

    return render_template(
        'developer_control.html',
        authenticated=authenticated,
        msg=msg,
        users=all_users,
        logs=WORKER_DATA,
        stats=stats
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)