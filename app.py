"""
Google Maps Review Scraper - Railway Cloud Version
Deploy to Railway.app for free cloud hosting
"""

import os
import csv
import io
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify, Response
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import re

app = Flask(__name__)

# Job storage
jobs = {}

# HTML Template
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Google Maps Review Scraper</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--primary:#2563EB;--success:#10B981;--error:#EF4444;--bg:#F9FAFB;--surface:#FFF;--border:#E5E7EB;--text:#111827;--muted:#6B7280}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6;padding:20px}
.container{max-width:900px;margin:0 auto}
.header{text-align:center;padding:40px 0}
h1{font-size:36px;font-weight:700;margin-bottom:8px;background:linear-gradient(135deg,var(--primary) 0%,#7C3AED 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.subtitle{color:var(--muted);font-size:16px}
.card{background:var(--surface);border-radius:16px;padding:32px;box-shadow:0 1px 3px rgba(0,0,0,0.1);margin-bottom:24px}
.section-title{font-size:18px;font-weight:600;margin-bottom:20px;display:flex;align-items:center;gap:8px}
.badge{background:#DBEAFE;color:#1E40AF;font-size:11px;font-weight:600;padding:4px 8px;border-radius:4px;text-transform:uppercase;letter-spacing:0.5px}
textarea{width:100%;min-height:180px;padding:16px;border:2px solid var(--border);border-radius:12px;font-family:'Courier New',monospace;font-size:14px;resize:vertical;transition:border-color 0.2s}
textarea:focus{outline:none;border-color:var(--primary)}
.help-text{font-size:14px;color:var(--muted);margin:12px 0 24px 0;display:flex;align-items:start;gap:8px}
.help-text::before{content:'💡';font-size:16px}
.file-upload{border:2px dashed var(--border);border-radius:12px;padding:32px;text-align:center;cursor:pointer;transition:all 0.3s;position:relative;margin-bottom:24px}
.file-upload:hover{border-color:var(--primary);background:#F0F9FF}
.file-upload input{position:absolute;inset:0;opacity:0;cursor:pointer}
.file-upload-icon{font-size:48px;margin-bottom:12px}
.file-upload-text{font-size:15px;color:var(--text);font-weight:500}
.file-upload-hint{font-size:13px;color:var(--muted);margin-top:8px}
.file-chosen{display:none;background:#D1FAE5;color:#065F46;padding:12px 16px;border-radius:8px;margin-top:12px;font-size:14px;font-weight:500}
.options-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:24px}
.option-group{display:flex;flex-direction:column;gap:8px}
label{font-size:14px;font-weight:500;color:var(--text)}
input[type="number"],select{padding:12px;border:2px solid var(--border);border-radius:8px;font-size:14px;font-family:inherit;transition:border-color 0.2s}
input[type="number"]:focus,select:focus{outline:none;border-color:var(--primary)}
.btn{width:100%;padding:16px 24px;border:none;border-radius:12px;font-size:16px;font-weight:600;cursor:pointer;transition:all 0.2s;display:flex;align-items:center;justify-content:center;gap:8px}
.btn-primary{background:var(--primary);color:white;box-shadow:0 4px 12px rgba(37,99,235,0.3)}
.btn-primary:hover{background:#1D4ED8;transform:translateY(-2px);box-shadow:0 6px 16px rgba(37,99,235,0.4)}
.btn-primary:disabled{opacity:0.5;cursor:not-allowed;transform:none}
.btn-secondary{background:white;color:var(--text);border:2px solid var(--border);margin-top:12px}
.btn-secondary:hover{background:var(--bg)}
.alert{padding:16px 20px;border-radius:12px;margin-bottom:24px;font-size:14px;display:flex;align-items:start;gap:12px;line-height:1.6}
.alert-info{background:#DBEAFE;color:#1E40AF;border:1px solid #BFDBFE}
.alert-warning{background:#FEF3C7;color:#92400E;border:1px solid #FDE68A}
.alert-icon{font-size:20px;flex-shrink:0}
#progress-section{display:none}
.progress-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.progress-label{font-size:15px;font-weight:500;color:var(--text)}
.progress-percent{font-size:24px;font-weight:700;color:var(--primary)}
.progress-bar{height:12px;background:var(--border);border-radius:6px;overflow:hidden;margin-bottom:24px}
.progress-fill{height:100%;background:linear-gradient(90deg,var(--primary),#7C3AED);border-radius:6px;transition:width 0.5s ease;width:0%}
.log-container{background:#F9FAFB;border:2px solid var(--border);border-radius:12px;padding:16px;max-height:300px;overflow-y:auto;font-family:'Courier New',monospace;font-size:13px;margin-bottom:24px}
.log-line{padding:4px 0;color:var(--muted)}
.log-line.success{color:var(--success);font-weight:500}
.log-line.error{color:var(--error);font-weight:500}
.log-line.info{color:var(--primary)}
.log-time{color:#9CA3AF;margin-right:8px}
.results-section{display:none;margin-top:24px}
.stats-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:24px}
.stat-card{background:linear-gradient(135deg,#F0F9FF 0%,#E0F2FE 100%);border-radius:12px;padding:24px;text-align:center}
.stat-value{font-size:36px;font-weight:700;color:var(--primary);margin-bottom:4px}
.stat-label{font-size:12px;text-transform:uppercase;letter-spacing:0.5px;color:var(--muted);font-weight:600}
.btn-success{background:var(--success);color:white}
.btn-success:hover{background:#059669}
</style>
</head>
<body>
<div class="container">
<div class="header">
<h1>🗺️ Google Maps Review Scraper</h1>
<p class="subtitle">Cloud-Hosted on Railway.app</p>
</div>

<div class="alert alert-info">
<span class="alert-icon">☁️</span>
Cloud Version: This runs on Railway's free tier. Scraping uses Playwright with Chromium browser. For large batches (50+ places), the free tier may hit memory limits.
</div>

<div class="card">
<div class="section-title">
<span>Input URLs</span>
<span class="badge">Required</span>
</div>

<textarea id="urls-text" placeholder="Paste Google Maps URLs here, one per line&#10;e.g.&#10;https://www.google.com/maps/place/...&#10;https://www.google.com/maps/place/..."></textarea>

<div class="help-text">
Paste full Google Maps place URLs (must include /place/ and data=)
</div>

<div class="file-upload">
<input type="file" id="file-input" accept=".csv,.txt">
<span class="file-upload-icon">📂</span>
<p class="file-upload-text">Or upload CSV file</p>
<p class="file-upload-hint">CSV should have URLs in first column (with or without 'url' header)</p>
</div>

<p id="file-chosen"></p>

<div class="options-grid">
<div class="option-group">
<label for="max-reviews">Max Reviews per Place</label>
<input type="number" id="max-reviews" value="200" min="1" max="1000">
</div>
<div class="option-group">
<label for="sort-by">Sort Reviews By</label>
<select id="sort-by">
<option value="relevant">Most Relevant</option>
<option value="newest">Newest</option>
<option value="highest">Highest Rating</option>
<option value="lowest">Lowest Rating</option>
</select>
</div>
</div>

<button id="start-btn" class="btn btn-primary" disabled>
<span>🚀 Start Scraping</span>
</button>
<button id="reset-btn" class="btn btn-secondary" style="display:none">🔄 Scrape Another Batch</button>
</div>

<div id="progress-section" class="card">
<div class="section-title">🔄 Scraping Progress <span class="badge">Live</span></div>

<div class="progress-header">
<span class="progress-label">Processing <span id="current-done">0</span> of <span id="total-places">0</span> places</span>
<span class="progress-percent">0%</span>
</div>

<div class="progress-bar">
<div class="progress-fill" id="progress-fill"></div>
</div>

<div class="log-container" id="logs"></div>
</div>

<div id="results-section" class="results-section">
<div class="stats-grid">
<div class="stat-card">
<div class="stat-value" id="places-scraped">0</div>
<div class="stat-label">Places Scraped</div>
</div>
<div class="stat-card">
<div class="stat-value" id="total-reviews">0</div>
<div class="stat-label">Total Reviews</div>
</div>
<div class="stat-card">
<div class="stat-value" id="errors-count">0</div>
<div class="stat-label">Errors</div>
</div>
</div>

<button id="download-btn" class="btn btn-success">
<span>⬇️ Download Results CSV</span>
</button>
</div>
</div>

<script>
const urlsText = document.getElementById('urls-text');
const fileInput = document.getElementById('file-input');
const fileChosen = document.getElementById('file-chosen');
const startBtn = document.getElementById('start-btn');
const resetBtn = document.getElementById('reset-btn');
const progressSection = document.getElementById('progress-section');
const resultsSection = document.getElementById('results-section');
const logsContainer = document.getElementById('logs');
const progressFill = document.getElementById('progress-fill');
const currentDone = document.getElementById('current-done');
const totalPlaces = document.getElementById('total-places');
const placesScraped = document.getElementById('places-scraped');
const totalReviews = document.getElementById('total-reviews');
const errorsCount = document.getElementById('errors-count');
const downloadBtn = document.getElementById('download-btn');
const maxReviews = document.getElementById('max-reviews');
const sortBy = document.getElementById('sort-by');

let jobId = null;
let pollInterval = null;

function toggleInputs(disabled) {
  urlsText.disabled = disabled;
  fileInput.disabled = disabled;
  maxReviews.disabled = disabled;
  sortBy.disabled = disabled;
  startBtn.disabled = disabled;
  startBtn.textContent = disabled ? 'Scraping...' : '🚀 Start Scraping';
}

function validateInput() {
  const hasText = urlsText.value.trim().length > 0;
  startBtn.disabled = !hasText;
}

urlsText.addEventListener('input', validateInput);

fileInput.addEventListener('change', (e) => {
  const file = e.target.files[0];
  if (file) {
    fileChosen.textContent = `Chosen file: ${file.name}`;
    fileChosen.style.display = 'block';
  }
  validateInput();
});

startBtn.addEventListener('click', async () => {
  toggleInputs(true);
  progressSection.style.display = 'block';
  logsContainer.innerHTML = '';
  const formData = new FormData();
  if (fileInput.files[0]) {
    formData.append('file', fileInput.files[0]);
  } else {
    formData.append('urls_text', urlsText.value);
  }
  formData.append('max_reviews', maxReviews.value);
  formData.append('sort_by', sortBy.value);

  try {
    const res = await fetch('/start', {
      method: 'POST',
      body: formData
    });
    if (!res.ok) throw new Error(await res.text());
    const { job_id } = await res.json();
    jobId = job_id;
    pollStatus();
  } catch (err) {
    alert('Error starting job: ' + err.message);
    toggleInputs(false);
    progressSection.style.display = 'none';
  }
});

function pollStatus() {
  pollInterval = setInterval(async () => {
    if (!jobId) return;
    try {
      const res = await fetch(`/status/${jobId}`);
      if (!res.ok) throw new Error('Job not found');
      const data = await res.json();
      updateProgress(data);
      if (data.status === 'done') {
        clearInterval(pollInterval);
        showResults(data);
        resetBtn.style.display = 'block';
      }
    } catch (err) {
      clearInterval(pollInterval);
      alert('Error: ' + err.message);
      toggleInputs(false);
    }
  }, 2000);
}

function updateProgress(data) {
  currentDone.textContent = data.done;
  totalPlaces.textContent = data.total;
  const percent = Math.round((data.done / data.total) * 100) || 0;
  progressFill.style.width = `${percent}%`;
  document.querySelector('.progress-percent').textContent = `${percent}%`;

  logsContainer.innerHTML = data.logs.map(log => `
    <div class="log-line ${log.cls}">
      <span class="log-time">${new Date().toLocaleTimeString()}</span>
      ${log.msg}
    </div>
  `).join('');
  logsContainer.scrollTop = logsContainer.scrollHeight;
}

function showResults(data) {
  placesScraped.textContent = data.places_done;
  totalReviews.textContent = data.total_reviews;
  errorsCount.textContent = data.errors;
  resultsSection.style.display = 'block';
  downloadBtn.onclick = () => window.location.href = `/download/${jobId}`;
  logsContainer.innerHTML += '<div class="log-line success">✓ Scraping completed successfully!</div>';
}

resetBtn.addEventListener('click', () => {
  urlsText.value = '';
  fileInput.value = '';
  fileChosen.style.display = 'none';
  progressSection.style.display = 'none';
  resultsSection.style.display = 'none';
  resetBtn.style.display = 'none';
  toggleInputs(false);
  validateInput();
  jobId = null;
});
</script>
</body>
</html>"""

def scrape_place_reviews(url, max_reviews, sort_by, job_id):
    job = jobs[job_id]
    def log(msg, cls=''):
        job['logs'].append({'msg': msg, 'cls': cls})

    reviews = []
    place_name = 'Unknown'

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
            context = browser.new_context(viewport={'width': 1920, 'height': 1080}, locale='en-US', timezone_id='UTC')
            page = context.new_page()
            page.goto(url, timeout=90000)  # Increased timeout
            log('→ Loading page...')

            # Extra wait for full load
            time.sleep(5)  # or page.wait_for_load_state('networkidle')

            # Scroll to trigger UI elements
            page.evaluate("window.scrollBy(0, 500)")
            time.sleep(1)

            # Get place name (assuming h1 is the selector)
            try:
                place_name = page.locator('h1').text_content(timeout=10000).strip()
                log(f'📍 Place: {place_name}')
            except PlaywrightTimeoutError:
                log('⚠ Could not find place name')

            # Try to find and click Reviews tab with multiple selectors
            reviews_tab = None
            selectors = [
                'button:has-text("Reviews")',
                '[role="tab"][aria-label*="Reviews"]',
                'button[data-value="Reviews"]',
                'button[jsaction="pane.rating.moreReviews"]',
                'div[role="tab"][data-index="1"]',  # Sometimes index-based
                'button[aria-label*="reviews"]'
            ]

            for sel in selectors:
                try:
                    tab = page.locator(sel).first
                    if tab.is_visible(timeout=5000):
                        reviews_tab = tab
                        log(f'Found Reviews tab using {sel}')
                        break
                except PlaywrightTimeoutError:
                    pass

            if reviews_tab:
                reviews_tab.click()
                time.sleep(5)  # Wait longer for reviews to load
            else:
                log('⚠ Could not find Reviews tab after multiple attempts')

            # Check for no reviews message
            no_reviews_selectors = [
                'text="No reviews"',
                'text="no reviews yet"',
                'text="Be the first to review"',
                'text="This place has no reviews"'
            ]
            has_no_reviews = False
            for sel in no_reviews_selectors:
                if page.locator(sel).count() > 0:
                    has_no_reviews = True
                    break

            if has_no_reviews:
                log('ℹ️ This place has no reviews yet')
                return [], place_name

            # Sort reviews if not most relevant
            if sort_by != 'relevant':
                try:
                    sort_button = page.locator('button[aria-label="Sort reviews"]').first
                    sort_button.click()
                    time.sleep(1)
                    sort_options = {
                        'newest': page.locator('text="Newest"').first,
                        'highest': page.locator('text="Highest rating"').first,
                        'lowest': page.locator('text="Lowest rating"').first
                    }
                    if sort_by in sort_options:
                        sort_options[sort_by].click()
                        time.sleep(3)
                except:
                    log('⚠ Could not sort reviews')

            # Collect reviews
            log(f'🔍 Collecting reviews (max {max_reviews})...')

            review_panel = page.locator('.section-layout.section-scrollbox')  # Adjust if needed
            stall_rounds = 0
            prev_count = 0

            while len(reviews) < max_reviews:
                # Extract reviews (adjust selectors based on current UI)
                review_elements = page.locator('[data-review-id]').all()  # Common selector for reviews

                for elem in review_elements:
                    if len(reviews) >= max_reviews:
                        break
                    try:
                        review = {
                            'place_name': place_name,
                            'url': url,
                            'reviewer': elem.locator('.d4r55').text_content().strip(),  # Adjust
                            'rating': elem.locator('.kvMYJc').get_attribute('aria-label'),  # Adjust
                            'date': elem.locator('.rsqaWe').text_content().strip(),  # Adjust
                            'review_text': elem.locator('.wiI7pd').text_content().strip(),  # Adjust
                            'owner_reply': elem.locator('.jVeX0b .wiI7pd').text_content().strip() if elem.locator('.jVeX0b').count() > 0 else '',
                            'review_id': elem.get_attribute('data-review-id')
                        }
                        if review not in reviews:  # Avoid duplicates
                            reviews.append(review)
                    except:
                        pass

                current_count = len(reviews)
                log(f'  📊 Found {current_count} reviews...')

                if current_count >= max_reviews:
                    break

                try:
                    review_panel.evaluate('el => el.scrollTop += 3000')
                except:
                    page.mouse.wheel(0, 3000)

                time.sleep(1.5)

                if current_count == prev_count:
                    stall_rounds += 1
                    if stall_rounds >= 5:
                        break
                else:
                    stall_rounds = 0
                prev_count = current_count

            log(f'✓ Scraped {len(reviews)} reviews', 'success')

    except Exception as e:
        log(f'✗ Error: {str(e)[:200]}', 'error')
    finally:
        if 'browser' in locals():
            browser.close()

    return reviews, place_name


def run_scraping_job(job_id, urls, max_reviews, sort_by):
    """Background scraping job"""
    job = jobs[job_id]
    job['status'] = 'running'
    job['total'] = len(urls)
    job['done'] = 0
    job['results'] = []
    job['errors'] = 0
    job['places_done'] = 0
    job['total_reviews'] = 0
    
    def log(msg, cls=''):
        job['logs'].append({'msg': msg, 'cls': cls})
    
    log(f'🚀 Starting scrape of {len(urls)} place(s)...', 'info')
    
    for i, url in enumerate(urls):
        log(f'[{i+1}/{len(urls)}] Processing: {url[:70]}...', 'info')
        
        try:
            reviews, place_name = scrape_place_reviews(url.strip(), max_reviews, sort_by, job_id)
            job['results'].extend(reviews)
            job['places_done'] += 1
            job['total_reviews'] = len(job['results'])
            
            if not reviews:
                job['errors'] += 1
        except Exception as e:
            log(f'✗ Failed: {str(e)[:150]}', 'error')
            job['errors'] += 1
        
        job['done'] = i + 1
        time.sleep(2)
    
    job['status'] = 'done'
    log(f'🎉 Complete! Total: {len(job["results"])} reviews', 'success')


# Routes
@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/start', methods=['POST'])
def start():
    urls = []
    
    if 'file' in request.files:
        file = request.files['file']
        if file:
            content = file.read().decode('utf-8', errors='ignore')
            reader = csv.reader(io.StringIO(content))
            headers = None
            
            for row in reader:
                if not row:
                    continue
                if headers is None:
                    headers = [h.strip().lower() for h in row]
                    if 'url' in headers:
                        continue
                    elif row[0].strip().startswith('http'):
                        urls.append(row[0].strip())
                        continue
                else:
                    url_col = headers.index('url') if 'url' in headers else 0
                    if url_col < len(row):
                        url = row[url_col].strip()
                        if url.startswith('http'):
                            urls.append(url)
    
    elif 'urls_text' in request.form:
        text = request.form['urls_text']
        for line in text.splitlines():
            line = line.strip()
            if line.startswith('http'):
                urls.append(line)
    
    if not urls:
        return jsonify({'error': 'No valid URLs found'}), 400
    
    max_reviews = int(request.form.get('max_reviews', 200))
    sort_by = request.form.get('sort_by', 'relevant')
    
    import uuid
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        'status': 'queued',
        'total': len(urls),
        'done': 0,
        'results': [],
        'errors': 0,
        'logs': [],
        'places_done': 0,
        'total_reviews': 0
    }
    
    thread = threading.Thread(
        target=run_scraping_job,
        args=(job_id, urls, max_reviews, sort_by),
        daemon=True
    )
    thread.start()
    
    return jsonify({'job_id': job_id})


@app.route('/status/<job_id>')
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'status': job['status'],
        'total': job['total'],
        'done': job['done'],
        'errors': job['errors'],
        'logs': job['logs'],
        'places_done': job.get('places_done', 0),
        'total_reviews': job.get('total_reviews', 0),
    })


@app.route('/download/<job_id>')
def download(job_id):
    job = jobs.get(job_id)
    if not job or not job['results']:
        return 'No results', 404
    
    output = io.StringIO()
    fields = ['place_name', 'url', 'reviewer', 'rating', 'date', 'review_text', 'owner_reply', 'review_id']
    writer = csv.DictWriter(output, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(job['results'])
    output.seek(0)
    
    filename = f'google_reviews_{job_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)