"""Admin dashboard routes — content, images, tracking, settings."""
import os
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from models import db, SiteSetting, MediaFile, User
from .helpers import allowed_file, save_image, delete_image
from . import admin_bp

# ────────────────────────────────────────────────────────────────────
# Dashboard home
# ────────────────────────────────────────────────────────────────────
@admin_bp.route('/')
@login_required
def dashboard():
    import requests as req
    from bs4 import BeautifulSoup
    stats = {'total': 84, 'available': '—', 'booked': '—', 'pct': '—'}
    try:
        r = req.get('https://nexusluxurytower.nddlbd.com/public', timeout=8)
        soup = BeautifulSoup(r.text, 'html.parser')
        cards = soup.find_all('div', class_='apt-card')
        avail = sum(1 for c in cards if 'apt-available' in c.get('class', []))
        booked = sum(1 for c in cards if 'apt-booked' in c.get('class', []))
        stats = {'total': avail + booked, 'available': avail, 'booked': booked,
                 'pct': round(booked / (avail + booked) * 100) if (avail + booked) else 0}
    except Exception:
        pass
    media_count = MediaFile.query.count()
    return render_template('admin/dashboard.html', stats=stats, media_count=media_count)


# ────────────────────────────────────────────────────────────────────
# Content editor
# ────────────────────────────────────────────────────────────────────
SECTIONS = [
    ('seo',      'SEO সেটিং'),
    ('hero',     'হিরো সেকশন'),
    ('trust',    'ট্রাস্ট স্ট্রিপ'),
    ('gallery',  'মিডিয়া গ্যালারি'),
    ('features', 'রেসিডেন্স ফিচার'),
    ('payment',  'পেমেন্ট প্ল্যান'),
    ('booking',  'বুকিং ফর্ম'),
    ('footer',   'ফুটার ও পার্টনার'),
    ('contact',  'যোগাযোগ / WhatsApp'),
]

@admin_bp.route('/content')
@login_required
def content():
    active = request.args.get('section', 'hero')
    settings = SiteSetting.query.filter_by(section=active).order_by(SiteSetting.id).all()
    return render_template('admin/content.html', sections=SECTIONS, active=active, settings=settings)


@admin_bp.route('/content/save', methods=['POST'])
@login_required
def content_save():
    for key, value in request.form.items():
        if key.startswith('_'):
            continue
        SiteSetting.set(key, value)
    flash('সেভ হয়েছে! ✓', 'success')
    section = request.form.get('_section', 'hero')
    return redirect(url_for('admin.content', section=section))


# ────────────────────────────────────────────────────────────────────
# Image manager
# ────────────────────────────────────────────────────────────────────
@admin_bp.route('/images')
@login_required
def images():
    files = MediaFile.query.order_by(MediaFile.uploaded_at.desc()).all()
    return render_template('admin/images.html', files=files)


@admin_bp.route('/images/upload', methods=['POST'])
@login_required
def images_upload():
    uploaded_files = request.files.getlist('files')
    count = 0
    for f in uploaded_files:
        if f and allowed_file(f.filename):
            filename, url, size = save_image(f)
            mf = MediaFile(filename=filename, original_name=f.filename, url=url, size_bytes=size)
            db.session.add(mf)
            count += 1
    db.session.commit()
    flash(f'{count}টি ছবি আপলোড হয়েছে। ✓', 'success')
    return redirect(url_for('admin.images'))


@admin_bp.route('/images/delete/<int:file_id>', methods=['POST'])
@login_required
def images_delete(file_id):
    mf = MediaFile.query.get_or_404(file_id)
    delete_image(mf.filename)
    db.session.delete(mf)
    db.session.commit()
    return jsonify({'ok': True})


# ────────────────────────────────────────────────────────────────────
# Tracking codes
# ────────────────────────────────────────────────────────────────────
@admin_bp.route('/tracking', methods=['GET', 'POST'])
@login_required
def tracking():
    tracking_keys = [k for k in [
        'tracking_fb_pixel_id', 'tracking_fb_pixel_enabled',
        'tracking_fb_capi_token', 'tracking_fb_capi_enabled',
        'tracking_ga4_id', 'tracking_ga4_enabled',
        'tracking_gtm_id', 'tracking_gtm_enabled',
        'tracking_tiktok_pixel_id', 'tracking_tiktok_enabled',
        'tracking_custom_head', 'tracking_custom_body',
    ]]
    if request.method == 'POST':
        for key in tracking_keys:
            value = request.form.get(key, '')
            SiteSetting.set(key, value)
        flash('ট্র্যাকিং কোড সেভ হয়েছে! ✓', 'success')
        return redirect(url_for('admin.tracking'))

    settings = {k: SiteSetting.get(k) for k in tracking_keys}
    return render_template('admin/tracking.html', settings=settings)


# ────────────────────────────────────────────────────────────────────
# Site settings (SEO, WhatsApp, password)
# ────────────────────────────────────────────────────────────────────
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'seo':
            SiteSetting.set('site_title', request.form.get('site_title', ''))
            SiteSetting.set('site_description', request.form.get('site_description', ''))
            SiteSetting.set('contact_whatsapp', request.form.get('contact_whatsapp', ''))
            SiteSetting.set('contact_phone', request.form.get('contact_phone', ''))
            flash('সেটিং সেভ হয়েছে! ✓', 'success')
        elif action == 'password':
            from flask_login import current_user
            new_pw = request.form.get('new_password', '')
            confirm = request.form.get('confirm_password', '')
            if len(new_pw) < 6:
                flash('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে।', 'error')
            elif new_pw != confirm:
                flash('পাসওয়ার্ড মিলছে না।', 'error')
            else:
                current_user.set_password(new_pw)
                db.session.commit()
                flash('পাসওয়ার্ড পরিবর্তন হয়েছে! ✓', 'success')
        return redirect(url_for('admin.settings'))

    data = {
        'site_title': SiteSetting.get('site_title'),
        'site_description': SiteSetting.get('site_description'),
        'contact_whatsapp': SiteSetting.get('contact_whatsapp'),
        'contact_phone': SiteSetting.get('contact_phone'),
    }
    return render_template('admin/settings.html', data=data)

# ────────────────────────────────────────────────────────────────────
# Visitors list
# ────────────────────────────────────────────────────────────────────
from models import Visitor

@admin_bp.route('/visitors')
@login_required
def visitors():
    items = Visitor.query.order_by(Visitor.created_at.desc()).all()
    return render_template('admin/visitors.html', visitors=items)

