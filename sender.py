#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
WhatsApp Auto Sender - Split CSV Files Support
Files: SDB (1), SDB (2), SDB (3)...
"""

import os
import json
import time
import random
import string
import re
from datetime import datetime
import pandas as pd
import glob

print("🚀 Starting WhatsApp Auto Sender...")

# ============================================
# CONFIGURATION
# ============================================

with open('config.json', 'r') as f:
    CONFIG = json.load(f)

MESSAGE_TEMPLATE = """👋 Hello {name} 
तुमच्या फायद्यासाठीच हा मेसेज केला गेलेला आहे.

तुम्ही सोलापूरकर असाल तर आम्ही खास तुमच्यासाठी एक प्लॅटफॉर्म घेऊन आलोय. आता तुम्हाला सोलापुरातल्या घडामोडी, महत्वाच्या ऑफर्स, शाळकरी मुलांसाठी नोट्स, तरुणांसाठी नोकरीचे अपडेट्स सगळं काही व्हॉट्सॲप वर मिळेल. केवळ खाली दिलेल्या नंबर वर मेसेज करून तुम्हाला काय हवं आहे ते सांगा.

9988363680 📲

काळजी करू नका, हजारो सोलापूरकरांनी या सुविधेवर विश्वास ठेवला आहे. ✅❤️ 

तुम्ही समक्ष भेट देऊ शकता. 
आमचा पत्ता : 302, भाईजी अपार्टमेंट, चौपाड परिसर सोलापूर 

या कोड कडे दुर्लक्ष करा 👇
~{code}~"""

# ============================================
# LOAD ALL SPLIT CSV FILES
# ============================================

def load_all_csv_files():
    """
    सर्व SDB (1), SDB (2)... files एकत्र load करतो
    """
    
    print("\n📂 Loading all CSV files...")
    
    # सर्व CSV files शोधा
    # Pattern: SDB (1).csv, SDB (2).csv, etc.
    csv_files = []
    
    # Check different patterns
    patterns = [
        'SDB (*.csv',      # SDB (1).csv
        'SDB*.csv',        # SDB1.csv
        'contacts*.csv'    # contacts1.csv
    ]
    
    for pattern in patterns:
        found = glob.glob(pattern)
        if found:
            csv_files.extend(found)
            break
    
    if not csv_files:
        print("❌ No CSV files found!")
        print("   Expected files like: SDB (1).csv, SDB (2).csv")
        return None
    
    # Sort files (SDB (1), SDB (2), SDB (3)...)
    csv_files.sort()
    
    print(f"✅ Found {len(csv_files)} CSV files:")
    for f in csv_files:
        print(f"   - {f}")
    
    # सर्व files load करून combine करा
    all_dataframes = []
    total_contacts = 0
    
    for csv_file in csv_files:
        try:
            # No header, 2 columns: Phone, Name
            df = pd.read_csv(csv_file, header=None, names=['Phone', 'Name'])
            all_dataframes.append(df)
            total_contacts += len(df)
            print(f"   ✅ Loaded {csv_file}: {len(df)} contacts")
        except Exception as e:
            print(f"   ❌ Error loading {csv_file}: {str(e)}")
    
    if not all_dataframes:
        print("❌ No data loaded!")
        return None
    
    # Combine सर्व dataframes
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    print(f"\n✅ Total contacts loaded: {len(combined_df)}")
    
    return combined_df

# ============================================
# PROGRESS TRACKER
# ============================================

class Progress:
    def __init__(self):
        self.load()
    
    def load(self):
        if os.path.exists('progress.json'):
            with open('progress.json', 'r') as f:
                data = json.load(f)
                self.index = data.get('index', 0)
                self.total_sent = data.get('total_sent', 0)
                self.total_failed = data.get('total_failed', 0)
                self.last_date = data.get('last_date', '')
        else:
            self.index = 0
            self.total_sent = 0
            self.total_failed = 0
            self.last_date = ''
    
    def save(self):
        data = {
            'index': self.index,
            'total_sent': self.total_sent,
            'total_failed': self.total_failed,
            'last_date': datetime.now().strftime('%Y-%m-%d'),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        with open('progress.json', 'w') as f:
            json.dump(data, f, indent=4)
    
    def should_run_today(self):
        today = datetime.now().strftime('%Y-%m-%d')
        return self.last_date != today

# ============================================
# HELPER FUNCTIONS
# ============================================

def validate_phone(phone):
    """Phone number validate करतो"""
    phone_str = str(phone).strip()
    phone_clean = re.sub(r'[^0-9]', '', phone_str)
    return phone_clean if len(phone_clean) == 10 else None

def get_last_name(name):
    """नावातून शेवटचा शब्द (आडनाव) काढतो"""
    try:
        words = str(name).strip().split()
        return words[-1] if words else "मित्रा"
    except:
        return "मित्रा"

def gen_code():
    """4 digit random code generate करतो"""
    return ''.join(random.choices(string.digits, k=4))

def create_message(name):
    """Personalized message तयार करतो"""
    last = get_last_name(name)
    code = gen_code()
    msg = MESSAGE_TEMPLATE.format(name=last, code=code)
    return msg, code

# ============================================
# WHATSAPP SENDER
# ============================================

def send_whatsapp_message(phone, name, image_path):
    """
    WhatsApp message + image send करतो
    """
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        # Headless Chrome setup
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Session restore (login persist करण्यासाठी)
        profile_path = './chrome_profile'
        if os.path.exists(profile_path):
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        phone_full = f"91{phone}"
        msg, code = create_message(name)
        
        print(f"📤 Sending to: {get_last_name(name)} ({phone})")
        
        # WhatsApp Web उघडा
        driver.get(f"https://web.whatsapp.com/send?phone={phone_full}")
        time.sleep(10)
        
        try:
            # Check if chat loaded
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-testid="conversation-compose-box-input"]'))
            )
            
            # Attach button क्लिक करा
            attach_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@title="Attach"]'))
            )
            attach_btn.click()
            time.sleep(2)
            
            # Image upload करा
            img_input = driver.find_element(
                By.XPATH,
                '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
            )
            img_input.send_keys(os.path.abspath(image_path))
            time.sleep(4)
            
            # Caption box मध्ये message टाका
            caption_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@data-testid="media-caption-input-container"]//div[@contenteditable="true"]')
                )
            )
            
            # Message line by line टाका
            for line in msg.split('\n'):
                caption_box.send_keys(line)
                caption_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            time.sleep(2)
            
            # Send button क्लिक करा
            send_btn = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@data-testid="send-button"]'))
            )
            send_btn.click()
            
            print(f"   ✅ Sent! Code: {code}")
            time.sleep(3)
            
            driver.quit()
            return True, code
            
        except Exception as e:
            print(f"   ❌ Send error: {str(e)[:100]}")
            driver.quit()
            return False, code if 'code' in locals() else "0000"
        
    except Exception as e:
        print(f"   ❌ Driver error: {str(e)[:100]}")
        return False, "0000"

# ============================================
# SEND REPORT
# ============================================

def send_report(sent, failed, total_sent, total_failed):
    """
    Hourly/Daily report send करतो
    """
    
    report = f"""📊 *DAILY REPORT*
━━━━━━━━━━━━━━━━
⏰ {datetime.now().strftime('%d-%m-%Y %H:%M')}

*Today's Batch:*
✅ Sent: {sent}
❌ Failed: {failed}

*Overall Progress:*
📨 Total Sent: {total_sent}
❌ Total Failed: {total_failed}
📈 Success Rate: {(total_sent/(total_sent+total_failed)*100) if (total_sent+total_failed) > 0 else 0:.1f}%
━━━━━━━━━━━━━━━━"""
    
    print(f"\n📊 Sending report to {CONFIG['report_number']}...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        driver.get(f"https://web.whatsapp.com/send?phone=91{CONFIG['report_number']}")
        time.sleep(8)
        
        input_box = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-testid="conversation-compose-box-input"]'))
        )
        
        for line in report.split('\n'):
            input_box.send_keys(line)
            input_box.send_keys(Keys.SHIFT + Keys.ENTER)
        
        time.sleep(1)
        input_box.send_keys(Keys.ENTER)
        
        print("   ✅ Report sent!")
        time.sleep(3)
        
        driver.quit()
        
    except Exception as e:
        print(f"   ❌ Report failed: {str(e)[:50]}")

# ============================================
# MAIN FUNCTION
# ============================================

def main():
    print("\n" + "="*70)
    print("  🚀 WHATSAPP AUTO SENDER - SPLIT FILES VERSION")
    print("="*70)
    
    # Load progress
    progress = Progress()
    
    # Check if should run today
    if not progress.should_run_today():
        print(f"\n✅ Already ran today!")
        print(f"   Last run: {progress.last_date}")
        print(f"   Total sent: {progress.total_sent}")
        return
    
    # Load ALL CSV files
    df = load_all_csv_files()
    
    if df is None or len(df) == 0:
        print("❌ No contacts loaded!")
        return
    
    # Validate phone numbers
    print("\n🔍 Validating phone numbers...")
    valid = []
    invalid = 0
    
    for _, row in df.iterrows():
        ph = validate_phone(row['Phone'])
        if ph:
            valid.append({'Phone': ph, 'Name': row['Name']})
        else:
            invalid += 1
    
    clean_df = pd.DataFrame(valid)
    
    print(f"✅ Valid numbers: {len(clean_df)}")
    print(f"❌ Invalid/Skipped: {invalid}")
    
    # Get today's batch
    start = progress.index
    end = min(start + CONFIG['daily_limit'], len(clean_df))
    
    if start >= len(clean_df):
        print("\n🎉 All contacts completed!")
        return
    
    batch = clean_df.iloc[start:end]
    
    print(f"\n📊 Today's Batch:")
    print(f"   Starting from index: {start}")
    print(f"   Ending at index: {end}")
    print(f"   Messages to send: {len(batch)}")
    print(f"   Remaining after today: {len(clean_df) - end}")
    
    # Check if image exists
    image_files = glob.glob('*.jpg') + glob.glob('*.png') + glob.glob('*.jpeg')
    
    if not image_files:
        print("\n❌ No image file found!")
        print("   Please upload image.jpg")
        return
    
    image_path = image_files[0]
    print(f"\n✅ Using image: {image_path}")
    
    # Process batch
    print(f"\n🚀 Starting to send messages...")
    print(f"   Delay: {CONFIG['delay_minutes']} minute between messages")
    print("="*70)
    
    sent = 0
    failed = 0
    
    for idx, row in batch.iterrows():
        success, code = send_whatsapp_message(row['Phone'], row['Name'], image_path)
        
        if success:
            sent += 1
            progress.total_sent += 1
        else:
            failed += 1
            progress.total_failed += 1
        
        progress.index += 1
        
        # Save progress every 10 messages
        if (sent + failed) % 10 == 0:
            progress.save()
            print(f"\n📊 Progress Update: {sent + failed}/{len(batch)}")
            print(f"   ✅ Success: {sent} | ❌ Failed: {failed}")
        
        # Delay between messages
        if (sent + failed) < len(batch):  # Don't delay after last message
            print(f"   ⏳ Waiting {CONFIG['delay_minutes']} minute...")
            time.sleep(CONFIG['delay_minutes'] * 60)
    
    # Final save
    progress.save()
    
    # Send report
    send_report(sent, failed, progress.total_sent, progress.total_failed)
    
    # Final summary
    print("\n" + "="*70)
    print("✅ DAILY BATCH COMPLETED!")
    print("="*70)
    print(f"\n📊 Today's Statistics:")
    print(f"   ✅ Successfully sent: {sent}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📈 Success rate: {(sent/(sent+failed)*100) if (sent+failed) > 0 else 0:.1f}%")
    print(f"\n📈 Overall Progress:")
    print(f"   📨 Total sent: {progress.total_sent}")
    print(f"   ❌ Total failed: {progress.total_failed}")
    print(f"   ⏳ Remaining contacts: {len(clean_df) - progress.index}")
    print(f"   📅 Days remaining: ~{(len(clean_df) - progress.index) // CONFIG['daily_limit'] + 1}")
    print("="*70)
    
    print("\n💡 Next Run:")
    print("   Tomorrow at scheduled time, next 500 messages will be sent automatically!")

if __name__ == "__main__":
    main()
