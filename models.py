from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False)
    value = db.Column(db.Text, default='')
    value_type = db.Column(db.String(20), default='text')  # text, html, image, code, bool
    label = db.Column(db.String(200), default='')
    section = db.Column(db.String(80), default='general')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @staticmethod
    def get(key, default=''):
        s = SiteSetting.query.filter_by(key=key).first()
        return s.value if s else default

    @staticmethod
    def set(key, value):
        s = SiteSetting.query.filter_by(key=key).first()
        if s:
            s.value = value
            s.updated_at = datetime.utcnow()
        else:
            s = SiteSetting(key=key, value=value)
            db.session.add(s)
        db.session.commit()


class MediaFile(db.Model):
    __tablename__ = 'media_files'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(256), nullable=False)
    original_name = db.Column(db.String(256))
    url = db.Column(db.String(512))
    size_bytes = db.Column(db.Integer)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


# Default settings seed data
DEFAULT_SETTINGS = [
    # ── Site / SEO ──────────────────────────────────────────────────
    {'key': 'site_title', 'value': 'NextGen Luxury Tower | Bosoti Point — বুড়িগঙ্গার পাড়ে নিজের ঠিকানা', 'value_type': 'text', 'label': 'Site Title', 'section': 'seo'},
    {'key': 'site_description', 'value': 'বুড়িগঙ্গার পাড়ে মোহাম্মদপুরে ৮৪টি ল্যান্ড-শেয়ার ফ্ল্যাট। ১,৮০০ বর্গফুট, ৪ বেডরুম — মাত্র ৳৫২ লাখ থেকে।', 'value_type': 'text', 'label': 'Meta Description', 'section': 'seo'},

    # ── Tracking ────────────────────────────────────────────────────
    {'key': 'tracking_fb_pixel_id', 'value': '', 'value_type': 'text', 'label': 'Facebook Pixel ID', 'section': 'tracking'},
    {'key': 'tracking_fb_pixel_enabled', 'value': '0', 'value_type': 'bool', 'label': 'Enable FB Pixel', 'section': 'tracking'},
    {'key': 'tracking_fb_capi_token', 'value': '', 'value_type': 'text', 'label': 'Facebook CAPI Token', 'section': 'tracking'},
    {'key': 'tracking_fb_capi_enabled', 'value': '0', 'value_type': 'bool', 'label': 'Enable FB CAPI', 'section': 'tracking'},
    {'key': 'tracking_ga4_id', 'value': '', 'value_type': 'text', 'label': 'Google Analytics Measurement ID (G-XXXXXXX)', 'section': 'tracking'},
    {'key': 'tracking_ga4_enabled', 'value': '0', 'value_type': 'bool', 'label': 'Enable GA4', 'section': 'tracking'},
    {'key': 'tracking_gtm_id', 'value': '', 'value_type': 'text', 'label': 'Google Tag Manager ID (GTM-XXXXX)', 'section': 'tracking'},
    {'key': 'tracking_gtm_enabled', 'value': '0', 'value_type': 'bool', 'label': 'Enable GTM', 'section': 'tracking'},
    {'key': 'tracking_tiktok_pixel_id', 'value': '', 'value_type': 'text', 'label': 'TikTok Pixel ID', 'section': 'tracking'},
    {'key': 'tracking_tiktok_enabled', 'value': '0', 'value_type': 'bool', 'label': 'Enable TikTok Pixel', 'section': 'tracking'},
    {'key': 'tracking_custom_head', 'value': '', 'value_type': 'code', 'label': 'Custom Head Scripts', 'section': 'tracking'},
    {'key': 'tracking_custom_body', 'value': '', 'value_type': 'code', 'label': 'Custom Body Scripts', 'section': 'tracking'},

    # ── Hero Section ─────────────────────────────────────────────────
    {'key': 'hero_title_line1', 'value': 'নিজের একটি বাড়ি,', 'value_type': 'text', 'label': 'Hero Title Line 1', 'section': 'hero'},
    {'key': 'hero_title_line2', 'value': 'গড়া হবে একসাথে।', 'value_type': 'text', 'label': 'Hero Title Line 2', 'section': 'hero'},
    {'key': 'hero_subtitle', 'value': 'NextGen Luxury Tower শুধু একটি ফ্ল্যাট নয় — এটি আপনার সন্তানের শৈশবের ঠিকানা, বাবা-মায়ের নিরাপদ আশ্রয়, আর নিজের হাতে গড়া স্বপ্নের বাস্তব রূপ।', 'value_type': 'text', 'label': 'Hero Subtitle', 'section': 'hero'},
    {'key': 'hero_location_tag', 'value': 'চন্দ্রিমা মডেল টাউন · মোহাম্মদপুর, ঢাকা', 'value_type': 'text', 'label': 'Location Tag', 'section': 'hero'},
    {'key': 'hero_cta1_label', 'value': 'প্রাইভেট সাইট ভিজিট বুক করুন', 'value_type': 'text', 'label': 'CTA Button 1 Label', 'section': 'hero'},
    {'key': 'hero_cta1_url', 'value': '#book', 'value_type': 'text', 'label': 'CTA Button 1 URL', 'section': 'hero'},
    {'key': 'hero_stat1_num', 'value': 'B+G+18', 'value_type': 'text', 'label': 'Stat 1 Number', 'section': 'hero'},
    {'key': 'hero_stat1_lbl', 'value': 'তলা টাওয়ার', 'value_type': 'text', 'label': 'Stat 1 Label', 'section': 'hero'},
    {'key': 'hero_stat2_num', 'value': '1,800 sqft', 'value_type': 'text', 'label': 'Stat 2 Number', 'section': 'hero'},
    {'key': 'hero_stat2_lbl', 'value': '৪ বেড · ৩ বাথ', 'value_type': 'text', 'label': 'Stat 2 Label', 'section': 'hero'},
    {'key': 'hero_stat3_num', 'value': '84', 'value_type': 'text', 'label': 'Stat 3 Number', 'section': 'hero'},
    {'key': 'hero_stat3_lbl', 'value': 'মোট রেসিডেন্স', 'value_type': 'text', 'label': 'Stat 3 Label', 'section': 'hero'},
    {'key': 'hero_stat4_num', 'value': '৳52L', 'value_type': 'text', 'label': 'Stat 4 Number', 'section': 'hero'},
    {'key': 'hero_stat4_lbl', 'value': 'শুরু যেখান থেকে', 'value_type': 'text', 'label': 'Stat 4 Label', 'section': 'hero'},

    # ── Trust Strip ───────────────────────────────────────────────────
    {'key': 'trust_1', 'value': 'ডিজাইন ও তত্ত্বাবধানে <b>NDDL</b>', 'value_type': 'html', 'label': 'Trust Item 1', 'section': 'trust'},
    {'key': 'trust_2', 'value': 'নির্মাণে <b>Luxury Construction</b>', 'value_type': 'html', 'label': 'Trust Item 2', 'section': 'trust'},
    {'key': 'trust_3', 'value': 'মার্কেটিং পার্টনার <b>Creatrex</b>', 'value_type': 'html', 'label': 'Trust Item 3', 'section': 'trust'},
    {'key': 'trust_4', 'value': 'নির্মাণ শুরু <b>জুন–জুলাই ২০২৭</b>', 'value_type': 'html', 'label': 'Trust Item 4', 'section': 'trust'},

    # ── Gallery ───────────────────────────────────────────────────────
    {'key': 'gallery_youtube_url', 'value': 'https://www.youtube.com/embed/5WfsBSk5zSg', 'value_type': 'text', 'label': 'YouTube Embed URL', 'section': 'gallery'},

    # ── Features ──────────────────────────────────────────────────────
    {'key': 'feature_1_num', 'value': '15 Kotha', 'value_type': 'text', 'label': 'Feature 1 Number', 'section': 'features'},
    {'key': 'feature_1_lbl', 'value': 'জমির পরিমাণ', 'value_type': 'text', 'label': 'Feature 1 Label', 'section': 'features'},
    {'key': 'feature_2_num', 'value': 'B+G+18', 'value_type': 'text', 'label': 'Feature 2 Number', 'section': 'features'},
    {'key': 'feature_2_lbl', 'value': 'তলা কাঠামো', 'value_type': 'text', 'label': 'Feature 2 Label', 'section': 'features'},
    {'key': 'feature_3_num', 'value': '84', 'value_type': 'text', 'label': 'Feature 3 Number', 'section': 'features'},
    {'key': 'feature_3_lbl', 'value': 'মোট রেসিডেন্স', 'value_type': 'text', 'label': 'Feature 3 Label', 'section': 'features'},
    {'key': 'feature_4_num', 'value': '6 / Floor', 'value_type': 'text', 'label': 'Feature 4 Number', 'section': 'features'},
    {'key': 'feature_4_lbl', 'value': 'প্রতি তলায় ফ্ল্যাট', 'value_type': 'text', 'label': 'Feature 4 Label', 'section': 'features'},
    {'key': 'feature_5_num', 'value': '1,800 sqft', 'value_type': 'text', 'label': 'Feature 5 Number', 'section': 'features'},
    {'key': 'feature_5_lbl', 'value': 'প্রতি ফ্ল্যাটে', 'value_type': 'text', 'label': 'Feature 5 Label', 'section': 'features'},
    {'key': 'feature_6_num', 'value': '4 Bed · 3 Bath', 'value_type': 'text', 'label': 'Feature 6 Number', 'section': 'features'},
    {'key': 'feature_6_lbl', 'value': '৩টি বারান্দা', 'value_type': 'text', 'label': 'Feature 6 Label', 'section': 'features'},
    {'key': 'feature_7_num', 'value': '1 Drawing · 1 Dining', 'value_type': 'text', 'label': 'Feature 7 Number', 'section': 'features'},
    {'key': 'feature_7_lbl', 'value': 'সাথে কিচেন', 'value_type': 'text', 'label': 'Feature 7 Label', 'section': 'features'},
    {'key': 'feature_8_num', 'value': 'Basement + Ground', 'value_type': 'text', 'label': 'Feature 8 Number', 'section': 'features'},
    {'key': 'feature_8_lbl', 'value': 'নির্ধারিত পার্কিং', 'value_type': 'text', 'label': 'Feature 8 Label', 'section': 'features'},

    # ── Payment ───────────────────────────────────────────────────────
    {'key': 'payment_desc', 'value': 'টাওয়ার যেমন উঠবে, তেমনই দেবেন কিস্তি। এককালীন কোনো চাপ নেই। প্রতিটি কিস্তি বাঁধা থাকে যাচাইকৃত নির্মাণ ধাপের সাথে, প্রতি ধাপে হিসাব খোলা থাকে সব সদস্যের জন্য।', 'value_type': 'textarea', 'label': 'Payment Description', 'section': 'payment'},
    {'key': 'payment_step1_name', 'value': 'ধাপ ০১ / শেয়ার সংরক্ষণ করুন', 'value_type': 'text', 'label': 'Step 1 Name', 'section': 'payment'},
    {'key': 'payment_step1_desc', 'value': 'শেয়ার চুক্তিতে সই করে NextGen Luxury Tower-এর ৮৪ জন মালিকের একজন হয়ে যান।', 'value_type': 'textarea', 'label': 'Step 1 Description', 'section': 'payment'},
    {'key': 'payment_step2_name', 'value': 'ধাপ ০২ / পাইলিং', 'value_type': 'text', 'label': 'Step 2 Name', 'section': 'payment'},
    {'key': 'payment_step2_desc', 'value': 'সাইটে ফাউন্ডেশন পাইলিং শুরু হলে প্রতি সদস্যকে দিতে হবে।', 'value_type': 'textarea', 'label': 'Step 2 Description', 'section': 'payment'},
    {'key': 'payment_step2_amt', 'value': '৳3,00,000', 'value_type': 'text', 'label': 'Step 2 Amount', 'section': 'payment'},
    {'key': 'payment_step3_name', 'value': 'ধাপ ০৩ / বেজমেন্ট ও গ্রেড বিম', 'value_type': 'text', 'label': 'Step 3 Name', 'section': 'payment'},
    {'key': 'payment_step3_desc', 'value': 'বেজমেন্ট ও গ্রেড বিমের কাজ সম্পন্ন হলে প্রতি সদস্যকে দিতে হবে।', 'value_type': 'textarea', 'label': 'Step 3 Description', 'section': 'payment'},
    {'key': 'payment_step3_amt', 'value': '৳3,00,000', 'value_type': 'text', 'label': 'Step 3 Amount', 'section': 'payment'},
    {'key': 'payment_step4_name', 'value': 'ধাপ ০৪ → প্রতি তলার কিস্তি', 'value_type': 'text', 'label': 'Step 4 Name', 'section': 'payment'},
    {'key': 'payment_step4_desc', 'value': 'প্রতিটি তলার ঢালাই হওয়ার সাথে সাথে প্রতি সদস্য তার অংশ পরিশোধ করবেন।', 'value_type': 'textarea', 'label': 'Step 4 Description', 'section': 'payment'},
    {'key': 'payment_step4_amt', 'value': '৳1,20,000 / তলা', 'value_type': 'text', 'label': 'Step 4 Amount', 'section': 'payment'},
    {'key': 'payment_step5_name', 'value': 'হস্তান্তর / ৪৮–৫৪ মাসের মধ্যে চাবি হাতে', 'value_type': 'text', 'label': 'Step 5 Name', 'section': 'payment'},
    {'key': 'payment_step5_desc', 'value': 'সম্পূর্ণ শেয়ার পরিশোধের পর ৪৮–৫৪ মাসের মধ্যে নির্মাণকাজ সম্পন্ন হবে ইনশাআল্লাহ্ — পুরো সময় তত্ত্বাবধানে থাকবে NDDL ও Luxury Construction।', 'value_type': 'textarea', 'label': 'Step 5 Description', 'section': 'payment'},
    {'key': 'payment_note', 'value': 'আনুমানিক নির্মাণ খরচের সর্বোচ্চ সীমা ৳৩০,০০,০০০ প্রতি শেয়ার। প্রকৃত খরচ কম হলে সদস্যরা কমই দেবেন। টপ ফ্লোরের ছয়টি ফ্ল্যাটে প্রতিটিতে ৳১,০০,০০০ ছাড় থাকবে। NDDL ও Luxury Construction-এর ১০% সার্ভিস চার্জ এই নির্মাণ বাজেটের মধ্যেই অন্তর্ভুক্ত — আলাদাভাবে কখনো ধার্য করা হবে না।', 'value_type': 'textarea', 'label': 'Payment Note', 'section': 'payment'},

    # ── Footer / Partners ─────────────────────────────────────────────
    {'key': 'footer_nddl_addr', 'value': 'House #13 (Flat-5), Road #28, Khan Apartment, Dhanmondi, Dhaka-1209', 'value_type': 'text', 'label': 'NDDL Address', 'section': 'footer'},
    {'key': 'footer_nddl_phone', 'value': '01617-929270 · 01677-463737', 'value_type': 'text', 'label': 'NDDL Phone', 'section': 'footer'},
    {'key': 'footer_nddl_web', 'value': 'www.nddbd.com', 'value_type': 'text', 'label': 'NDDL Web', 'section': 'footer'},
    {'key': 'footer_nddl_email', 'value': 'nddlbd25@gmail.com', 'value_type': 'text', 'label': 'NDDL Email', 'section': 'footer'},
    {'key': 'footer_luxury_addr', 'value': 'House #1 (2nd Floor), Road #04, Block B, Dhaka Uddan, Dhaka-1207', 'value_type': 'text', 'label': 'Luxury Const. Address', 'section': 'footer'},
    {'key': 'footer_luxury_phone', 'value': '01718-084135', 'value_type': 'text', 'label': 'Luxury Const. Phone', 'section': 'footer'},
    {'key': 'footer_luxury_web', 'value': 'luxuryconstructionltd.com', 'value_type': 'text', 'label': 'Luxury Const. Web', 'section': 'footer'},
    {'key': 'footer_luxury_email', 'value': 'luxuryconstruction2001@gmail.com', 'value_type': 'text', 'label': 'Luxury Const. Email', 'section': 'footer'},

    # ── Booking ───────────────────────────────────────────────────────
    {'key': 'booking_whatsapp_text', 'value': 'আসসালামু আলাইকুম, আমি বসতি পয়েন্টের NextGen Luxury Tower সম্পর্কে আগ্রহী। বিস্তারিত জানতে চাই।', 'value_type': 'textarea', 'label': 'WhatsApp Default Text', 'section': 'booking'},
    {'key': 'booking_fb_link', 'value': 'https://www.facebook.com/bosotipoint', 'value_type': 'text', 'label': 'Facebook Page Link', 'section': 'booking'},

    # ── Contact / WhatsApp ────────────────────────────────────────────
    {'key': 'contact_whatsapp', 'value': '8801617929270', 'value_type': 'text', 'label': 'WhatsApp Number (with country code, no +)', 'section': 'contact'},
    {'key': 'contact_phone', 'value': '+8801617929270', 'value_type': 'text', 'label': 'Phone Number (display)', 'section': 'contact'},
]

class Visitor(db.Model):
    __tablename__ = 'visitors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    time_pref = db.Column(db.String(50))
    budget = db.Column(db.String(50))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
