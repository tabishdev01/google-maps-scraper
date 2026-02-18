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
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:4px}
::-webkit-scrollbar-thumb:hover{background:#D1D5DB}
@media(max-width:768px){.options-grid{grid-template-columns:1fr}.stats-grid{grid-template-columns:1fr}}
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
<div><strong>Cloud Version:</strong> This runs on Railway's free tier. Scraping uses Playwright with Chromium browser. For large batches (50+ places), the free tier may hit memory limits.</div>
</div>
<div class="card" id="input-card">
<div class="section-title"><span>📝 Step 1: Add Google Maps URLs</span></div>
<div class="file-upload" id="file-upload-zone">
<input type="file" id="csv-file" accept=".csv,.txt">
<div class="file-upload-icon">📄</div>
<div class="file-upload-text">Drop CSV file here or click to browse</div>
<div class="file-upload-hint">One Google Maps URL per line</div>
</div>
<div class="file-chosen" id="file-chosen">✓ File selected: <span id="file-name"></span></div>
<div style="text-align:center;margin:20px 0;color:var(--muted);font-weight:600;">OR</div>
<textarea id="urls-textarea" placeholder="Paste Google Maps URLs here (one per line)

Example:
https://www.google.com/maps/place/USA+FOOD/@24.8677839,67.0524912,17z/..."></textarea>
<div class="help-text">Each URL should be a complete Google Maps place link from your browser's address bar</div>
<div class="section-title" style="margin-top:32px"><span>⚙️ Step 2: Configure Options</span></div>
<div class="options-grid">
<div class="option-group">
<label for="max-reviews">Max reviews per place</label>
<input type="number" id="max-reviews" value="200" min="10" max="500" step="10">
</div>
<div class="option-group">
<label for="sort-by">Sort reviews by</label>
<select id="sort-by">
<option value="relevant" selected>Most relevant</option>
<option value="newest">Newest first</option>
<option value="highest">Highest rating</option>
<option value="lowest">Lowest rating</option>
</select>
</div>
</div>
<button class="btn btn-primary" id="start-btn" onclick="startScraping()"><span>▶️</span><span>Start Scraping</span></button>
<button class="btn btn-secondary" onclick="downloadSample()"><span>📥</span><span>Download Sample CSV Template</span></button>
</div>
<div class="card" id="progress-section">
<div class="section-title"><span>🔄 Scraping Progress</span><span class="badge">Live</span></div>
<div class="progress-header">
<span class="progress-label" id="progress-label">Initializing...</span>
<span class="progress-percent" id="progress-percent">0%</span>
</div>
<div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
<div class="log-container" id="log-container"></div>
<div class="results-section" id="results-section">
<div class="stats-grid">
<div class="stat-card"><div class="stat-value" id="stat-places">0</div><div class="stat-label">Places Scraped</div></div>
<div class="stat-card"><div class="stat-value" id="stat-reviews">0</div><div class="stat-label">Total Reviews</div></div>
<div class="stat-card"><div class="stat-value" id="stat-errors">0</div><div class="stat-label">Errors</div></div>
</div>
<button class="btn btn-success" id="download-btn" onclick="downloadResults()"><span>⬇️</span><span>Download Results CSV</span></button>
<button class="btn btn-secondary" onclick="location.reload()"><span>🔄</span><span>Scrape Another Batch</span></button>
</div>
</div>
</div>
<script>
let currentJobId=null,pollInterval=null,lastLogCount=0;
const fileUpload=document.getElementById('file-upload-zone'),fileInput=document.getElementById('csv-file');
fileUpload.addEventListener('dragover',e=>{e.preventDefault();fileUpload.style.borderColor='var(--primary)';fileUpload.style.background='#F0F9FF'});
fileUpload.addEventListener('dragleave',()=>{fileUpload.style.borderColor='var(--border)';fileUpload.style.background=''});
fileUpload.addEventListener('drop',e=>{e.preventDefault();fileUpload.style.borderColor='var(--border)';fileUpload.style.background='';if(e.dataTransfer.files[0]){fileInput.files=e.dataTransfer.files;showFileName(e.dataTransfer.files[0].name)}});
fileInput.addEventListener('change',()=>{if(fileInput.files[0])showFileName(fileInput.files[0].name)});
function showFileName(name){document.getElementById('file-name').textContent=name;document.getElementById('file-chosen').style.display='block'}
function downloadSample(){const csv='url\\nhttps://www.google.com/maps/place/USA+FOOD/@24.8677839,67.0524912,17z/...';const blob=new Blob([csv],{type:'text/csv'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='sample_urls.csv';a.click();URL.revokeObjectURL(url)}
async function startScraping(){const file=fileInput.files[0],urlsText=document.getElementById('urls-textarea').value.trim();if(!file&&!urlsText){alert('Please upload a CSV file or paste URLs in the text area');return}const maxReviews=document.getElementById('max-reviews').value,sortBy=document.getElementById('sort-by').value;const formData=new FormData();if(file)formData.append('file',file);else formData.append('urls_text',urlsText);formData.append('max_reviews',maxReviews);formData.append('sort_by',sortBy);document.getElementById('start-btn').disabled=true;document.getElementById('start-btn').innerHTML='<span>⏳</span><span>Starting...</span>';try{const res=await fetch('/start',{method:'POST',body:formData});const data=await res.json();if(data.error){alert('Error: '+data.error);document.getElementById('start-btn').disabled=false;document.getElementById('start-btn').innerHTML='<span>▶️</span><span>Start Scraping</span>';return}currentJobId=data.job_id;showProgressSection();pollInterval=setInterval(pollStatus,1500)}catch(error){alert('Failed to start scraping: '+error.message);document.getElementById('start-btn').disabled=false;document.getElementById('start-btn').innerHTML='<span>▶️</span><span>Start Scraping</span>'}}
function showProgressSection(){document.getElementById('input-card').style.display='none';document.getElementById('progress-section').style.display='block'}
function addLog(message,type=''){const container=document.getElementById('log-container');const line=document.createElement('div');line.className='log-line '+type;const time=new Date().toLocaleTimeString();line.innerHTML=`<span class="log-time">${time}</span>${message}`;container.appendChild(line);container.scrollTop=container.scrollHeight}
async function pollStatus(){if(!currentJobId)return;try{const res=await fetch(`/status/${currentJobId}`);const data=await res.json();const percent=data.total>0?Math.round((data.done/data.total)*100):0;document.getElementById('progress-fill').style.width=percent+'%';document.getElementById('progress-percent').textContent=percent+'%';document.getElementById('progress-label').textContent=`Processing ${data.done} of ${data.total} places`;if(data.logs&&data.logs.length>lastLogCount){for(let i=lastLogCount;i<data.logs.length;i++)addLog(data.logs[i].msg,data.logs[i].cls||'');lastLogCount=data.logs.length}document.getElementById('stat-places').textContent=data.places_done||0;document.getElementById('stat-reviews').textContent=data.total_reviews||0;document.getElementById('stat-errors').textContent=data.errors||0;if(data.status==='done'||data.status==='error'){clearInterval(pollInterval);document.getElementById('results-section').style.display='block';if(data.status==='done'){document.getElementById('progress-fill').style.width='100%';document.getElementById('progress-percent').textContent='100%';addLog('✓ Scraping completed successfully!','success')}}}catch(error){console.error('Poll error:',error)}}
function downloadResults(){window.location.href=`/download/${currentJobId}`}
</script>
</body>
</html>
"""

# Scraping function
def scrape_place_reviews(url, max_reviews, sort_by, job_id):
    """Scrape reviews using Playwright"""
    from playwright.sync_api import sync_playwright
    import re
    
    job = jobs[job_id]
    def log(msg, cls=''):
        job['logs'].append({'msg': msg, 'cls': cls})
    
    SORT_MAP = {
        'newest': 'Newest',
        'relevant': 'Most relevant',
        'highest': 'Highest rating',
        'lowest': 'Lowest rating',
    }
    
    reviews = []
    place_name = 'Unknown'
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()
        
        try:
            log(f'→ Loading page...', 'info')
            page.goto(url, wait_until='networkidle', timeout=60000)
            time.sleep(3)
            
            try:
                place_name = page.locator('h1').first.inner_text(timeout=5000).strip()
                log(f'📍 Place: {place_name}')
            except:
                if '/place/' in url:
                    place_name = url.split('/place/')[1].split('/')[0].replace('+', ' ')
                log(f'📍 Using name from URL: {place_name}')
            
            try:
                page.get_by_role('tab', name=re.compile('Reviews', re.I)).click(timeout=5000)
                log('✓ Opened Reviews tab')
                time.sleep(2)
            except:
                log('⚠ Could not find Reviews tab', 'error')
            
            if sort_by != 'relevant':
                try:
                    sort_label = SORT_MAP.get(sort_by, 'Most relevant')
                    page.locator('button[aria-label*="Sort"]').first.click(timeout=5000)
                    time.sleep(1)
                    page.get_by_role('menuitemradio', name=re.compile(sort_label, re.I)).click(timeout=4000)
                    log(f'✓ Sorted by: {sort_label}')
                    time.sleep(2)
                except:
                    pass
            
            review_panel = page.locator('[role="main"]').first
            prev_count = 0
            stall_rounds = 0
            
            log(f'🔍 Collecting reviews (max {max_reviews})...')
            
            while len(reviews) < max_reviews:
                more_buttons = page.locator('button[aria-label*="See more"]').all()
                for btn in more_buttons:
                    try:
                        btn.click(timeout=500)
                        time.sleep(0.05)
                    except:
                        pass
                
                review_elements = page.locator('[data-review-id]').all()
                
                for element in review_elements:
                    try:
                        review_id = element.get_attribute('data-review-id') or ''
                        if any(r.get('review_id') == review_id for r in reviews):
                            continue
                        
                        try:
                            reviewer = element.locator('.d4r55').first.inner_text(timeout=1000).strip()
                        except:
                            reviewer = ''
                        
                        try:
                            rating_aria = element.locator('[aria-label*="stars"]').first.get_attribute('aria-label')
                            rating_match = re.search(r'(\d)', rating_aria or '')
                            rating = rating_match.group(1) if rating_match else ''
                        except:
                            rating = ''
                        
                        try:
                            date = element.locator('.rsqaWe').first.inner_text(timeout=1000).strip()
                        except:
                            date = ''
                        
                        try:
                            text = element.locator('.wiI7pd').first.inner_text(timeout=1000).strip()
                        except:
                            text = ''
                        
                        try:
                            reply = element.locator('.CDe7pd').first.inner_text(timeout=1000).strip()
                        except:
                            reply = ''
                        
                        if reviewer or text:
                            reviews.append({
                                'review_id': review_id,
                                'place_name': place_name,
                                'url': url,
                                'reviewer': reviewer,
                                'rating': rating,
                                'date': date,
                                'review_text': text,
                                'owner_reply': reply,
                            })
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
