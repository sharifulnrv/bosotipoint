import os
import re
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager
from models import db, User, SiteSetting, DEFAULT_SETTINGS, Visitor

# ─── App factory ────────────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'bosotipoint-secret-2026')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bosoti.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB upload limit

# ─── Extensions ─────────────────────────────────────────────────────
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'admin.login'
login_manager.login_message = 'অনুগ্রহ করে লগইন করুন।'
login_manager.login_message_category = 'error'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Admin blueprint ────────────────────────────────────────────────
from admin import admin_bp  # noqa: E402
app.register_blueprint(admin_bp)


# ─── DB init & seed ─────────────────────────────────────────────────
def init_db():
    with app.app_context():
        db.create_all()
        # Seed default admin user
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin')
            admin_user.set_password('bosoti2026')
            db.session.add(admin_user)
        # Seed default settings
        for row in DEFAULT_SETTINGS:
            if not SiteSetting.query.filter_by(key=row['key']).first():
                db.session.add(SiteSetting(**row))
        db.session.commit()


# ─── Apartment data fetcher ─────────────────────────────────────────
CACHE_TIMEOUT = 300 # 5 minutes
apartment_cache = {'data': [], 'timestamp': 0}

def fetch_apartments():
    global apartment_cache
    if time.time() - apartment_cache['timestamp'] < CACHE_TIMEOUT and apartment_cache['data']:
        return apartment_cache['data']

    url = "https://nexusluxurytower.nddlbd.com/public"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching apartments: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    apartments = []
    for card in soup.find_all('div', class_='apt-card'):
        id_el = card.find('div', class_='apt-id')
        if not id_el:
            continue
        apt_id = id_el.text.strip()
        classes = card.get('class', [])
        status = 'unknown'
        name = ''
        if 'apt-available' in classes or card.find(string=lambda t: t and 'Open' in t):
            status = 'available'
        elif 'apt-booked' in classes or card.find(string=lambda t: t and 'Booked' in t):
            status = 'booked'
            tenant_div = card.find('div', class_='tenant-name')
            if tenant_div:
                name = tenant_div.text.strip()
        if status != 'unknown':
            apartments.append({'id': apt_id, 'status': status, 'name': name})

    def sort_key(apt):
        match = re.match(r'([A-Z]+)(\d+)', apt['id'])
        return (int(match.group(2)), match.group(1)) if match else (0, apt['id'])

    apartments.sort(key=sort_key)
    apartment_cache['data'] = apartments[:84]
    apartment_cache['timestamp'] = time.time()
    return apartment_cache['data']


# ─── Public routes ───────────────────────────────────────────────────
@app.route('/')
def index():
    apartments = fetch_apartments()
    total = len(apartments)
    available_count = sum(1 for a in apartments if a['status'] == 'available')
    booked_count = sum(1 for a in apartments if a['status'] == 'booked')
    percentage = round((booked_count / total) * 100) if total > 0 else 0

    # Site settings from DB
    cfg = {
        'title': SiteSetting.get('site_title', 'NextGen Luxury Tower | Bosoti Point'),
        'description': SiteSetting.get('site_description', ''),
        'hero_title_line1': SiteSetting.get('hero_title_line1', 'নিজের একটি বাড়ি,'),
        'hero_title_line2': SiteSetting.get('hero_title_line2', 'গড়া হবে একসাথে।'),
        'hero_subtitle': SiteSetting.get('hero_subtitle', ''),
        'hero_location_tag': SiteSetting.get('hero_location_tag', ''),
        'hero_cta1_label': SiteSetting.get('hero_cta1_label', 'প্রাইভেট সাইট ভিজিট বুক করুন'),
        'hero_stat1_num': SiteSetting.get('hero_stat1_num', 'B+G+18'),
        'hero_stat1_lbl': SiteSetting.get('hero_stat1_lbl', 'তলা টাওয়ার'),
        'hero_stat2_num': SiteSetting.get('hero_stat2_num', '1,800 sqft'),
        'hero_stat2_lbl': SiteSetting.get('hero_stat2_lbl', '৪ বেড · ৩ বাথ'),
        'hero_stat3_num': SiteSetting.get('hero_stat3_num', '84'),
        'hero_stat3_lbl': SiteSetting.get('hero_stat3_lbl', 'মোট রেসিডেন্স'),
        'hero_stat4_num': SiteSetting.get('hero_stat4_num', '৳52L'),
        'hero_stat4_lbl': SiteSetting.get('hero_stat4_lbl', 'শুরু যেখান থেকে'),
        'trust_1': SiteSetting.get('trust_1', ''),
        'trust_2': SiteSetting.get('trust_2', ''),
        'trust_3': SiteSetting.get('trust_3', ''),
        'trust_4': SiteSetting.get('trust_4', ''),
        'gallery_youtube_url': SiteSetting.get('gallery_youtube_url', 'https://www.youtube.com/embed/5WfsBSk5zSg'),
        
        # Features
        'feature_1_num': SiteSetting.get('feature_1_num'),
        'feature_1_lbl': SiteSetting.get('feature_1_lbl'),
        'feature_2_num': SiteSetting.get('feature_2_num'),
        'feature_2_lbl': SiteSetting.get('feature_2_lbl'),
        'feature_3_num': SiteSetting.get('feature_3_num'),
        'feature_3_lbl': SiteSetting.get('feature_3_lbl'),
        'feature_4_num': SiteSetting.get('feature_4_num'),
        'feature_4_lbl': SiteSetting.get('feature_4_lbl'),
        'feature_5_num': SiteSetting.get('feature_5_num'),
        'feature_5_lbl': SiteSetting.get('feature_5_lbl'),
        'feature_6_num': SiteSetting.get('feature_6_num'),
        'feature_6_lbl': SiteSetting.get('feature_6_lbl'),
        'feature_7_num': SiteSetting.get('feature_7_num'),
        'feature_7_lbl': SiteSetting.get('feature_7_lbl'),
        'feature_8_num': SiteSetting.get('feature_8_num'),
        'feature_8_lbl': SiteSetting.get('feature_8_lbl'),

        # Payment
        'payment_desc': SiteSetting.get('payment_desc'),
        'payment_step1_name': SiteSetting.get('payment_step1_name'),
        'payment_step1_desc': SiteSetting.get('payment_step1_desc'),
        'payment_step2_name': SiteSetting.get('payment_step2_name'),
        'payment_step2_desc': SiteSetting.get('payment_step2_desc'),
        'payment_step2_amt': SiteSetting.get('payment_step2_amt'),
        'payment_step3_name': SiteSetting.get('payment_step3_name'),
        'payment_step3_desc': SiteSetting.get('payment_step3_desc'),
        'payment_step3_amt': SiteSetting.get('payment_step3_amt'),
        'payment_step4_name': SiteSetting.get('payment_step4_name'),
        'payment_step4_desc': SiteSetting.get('payment_step4_desc'),
        'payment_step4_amt': SiteSetting.get('payment_step4_amt'),
        'payment_step5_name': SiteSetting.get('payment_step5_name'),
        'payment_step5_desc': SiteSetting.get('payment_step5_desc'),
        'payment_note': SiteSetting.get('payment_note'),

        # Footer
        'footer_nddl_addr': SiteSetting.get('footer_nddl_addr'),
        'footer_nddl_phone': SiteSetting.get('footer_nddl_phone'),
        'footer_nddl_web': SiteSetting.get('footer_nddl_web'),
        'footer_nddl_email': SiteSetting.get('footer_nddl_email'),
        'footer_luxury_addr': SiteSetting.get('footer_luxury_addr'),
        'footer_luxury_phone': SiteSetting.get('footer_luxury_phone'),
        'footer_luxury_web': SiteSetting.get('footer_luxury_web'),
        'footer_luxury_email': SiteSetting.get('footer_luxury_email'),

        # Booking
        'booking_whatsapp_text': SiteSetting.get('booking_whatsapp_text'),
        'booking_fb_link': SiteSetting.get('booking_fb_link'),

        'contact_whatsapp': SiteSetting.get('contact_whatsapp', '8801617929270'),
        'contact_phone': SiteSetting.get('contact_phone', '+8801617929270'),
        # Tracking
        'fb_pixel_id': SiteSetting.get('tracking_fb_pixel_id') if SiteSetting.get('tracking_fb_pixel_enabled') == '1' else '',
        'ga4_id': SiteSetting.get('tracking_ga4_id') if SiteSetting.get('tracking_ga4_enabled') == '1' else '',
        'gtm_id': SiteSetting.get('tracking_gtm_id') if SiteSetting.get('tracking_gtm_enabled') == '1' else '',
        'tiktok_pixel_id': SiteSetting.get('tracking_tiktok_pixel_id') if SiteSetting.get('tracking_tiktok_enabled') == '1' else '',
        'custom_head': SiteSetting.get('tracking_custom_head'),
        'custom_body': SiteSetting.get('tracking_custom_body'),
    }

    return render_template('index.html',
                           apartments=apartments,
                           available=available_count,
                           booked=booked_count,
                           percentage=percentage,
                           cfg=cfg)

@app.route('/api/book', methods=['POST'])
def book_visit():
    data = request.json
    if not data or not data.get('fname') or not data.get('fphone'):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
    visitor = Visitor(
        name=data.get('fname'),
        phone=data.get('fphone'),
        time_pref=data.get('ftime'),
        budget=data.get('fbudget'),
        message=data.get('fmsg')
    )
    db.session.add(visitor)
    db.session.commit()
    return jsonify({'success': True})


# ─── Entry point ─────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8000)
