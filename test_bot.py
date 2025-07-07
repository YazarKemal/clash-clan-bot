import requests
import time
import json
import os
import asyncio
import threading
from datetime import datetime, timedelta

# IP adresini öğren ve yazdır
try:
    ip = requests.get('https://httpbin.org/ip', timeout=5).json()['origin']
    print(f"🌐 Bot IP adresi: {ip}")
except:
    print("IP bulunamadı")

# Bot ayarları
BOT_TOKEN = "7341092014:AAFegDvTd2ozU7fWMoyxriJuCn5wqkypvaY"
ADMIN_USERS = ["8114999904"]
COC_API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDatYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjZiYTE1MTdmLTE4YWItNDFhMS1iZTA3LTUxMzMyN2Q0ZTk3YyIsImlhdCI6MTc1MTg1NDIzOSwic3ViIjoiZGV2ZWxvcGVyLzRiYTU2MTc5LWE5NDgt MTBkYy0yNmI1LThkZjc5NjcyYjRmNCIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjIwOC43Ny4yNDQuODMiXSwidHlwZSI6ImNsaWVudCJ9XX0.vsBXveIRmpkw_PFbMWCwOLs4sPUQEeRanIMVL3Ozpg94x7YJSv2YxB_MCbmppVZWhoUBlPR0L8hC9zhTa69m5A"
CLAN_TAG = "#2RGC8UPYV"
COC_API_BASE = "https://api.clashofclans.com/v1"

# Rütbe sistemı
ROLE_HIERARCHY = {
    'member': 1,
    'admin': 2, 
    'coLeader': 3,
    'leader': 4
}

ROLE_NAMES = {
    'member': 'Üye',
    'admin': 'Başkan', 
    'coLeader': 'Yardımcı Lider',
    'leader': 'Lider'
}

# Küfür listesi
BAD_WORDS = ['aptal', 'salak', 'mal', 'ahmak', 'gerizekalı']

class AutoClanManager:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        self.offset = 0
        self.data_file = "clan_data.json"
        self.load_data()
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.last_clan_check = None
        print(f"✅ Bot başlatıldı - Tarih: {self.today}")
        
        # İlk klan analizi
        self.analyze_clan()
        
        # Otomatik klan kontrolü başlat (her saat)
        self.start_auto_clan_monitoring()
        
    def load_data(self):
        """Kalıcı verileri dosyadan yükle"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.daily_stats = data.get('daily_stats', {})
                    self.warnings_data = data.get('warnings_data', {})
                    self.clan_history = data.get('clan_history', {})
                    print(f"✅ {len(self.users)} kullanıcı verisi yüklendi")
            except:
                self.reset_data()
        else:
            self.reset_data()
    
    def reset_data(self):
        """Veri sıfırlama"""
        self.users = {}
        self.daily_stats = {}
        self.warnings_data = {}
        self.clan_history = {}
        print("🔄 Yeni veri yapısı oluşturuldu")
    
    def save_data(self):
        """Verileri dosyaya kaydet"""
        data = {
            'users': self.users,
            'daily_stats': self.daily_stats,
            'warnings_data': self.warnings_data,
            'clan_history': self.clan_history,
            'last_save': datetime.now().isoformat()
        }
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("💾 Veriler kaydedildi")
        except Exception as e:
            print(f"❌ Kaydetme hatası: {e}")
    
    def get_clan_data(self):
        """Clash of Clans API'den klan verilerini çek"""
        headers = {
            'Authorization': f'Bearer {COC_API_TOKEN}',
            'Accept': 'application/json'
        }
        
        try:
            # Klan genel bilgileri
            clan_url = f"{COC_API_BASE}/clans/{CLAN_TAG.replace('#', '%23')}"
            response = requests.get(clan_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                clan_data = response.json()
                print(f"✅ Klan verisi alındı: {clan_data['name']}")
                return clan_data
            else:
                print(f"❌ COC API Hatası: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ COC API Bağlantı hatası: {e}")
            return None
    
    def get_clan_war_data(self):
        """Klan savaşı verilerini çek"""
        headers = {
            'Authorization': f'Bearer {COC_API_TOKEN}',
            'Accept': 'application/json'
        }
        
        try:
            war_url = f"{COC_API_BASE}/clans/{CLAN_TAG.replace('#', '%23')}/currentwar"
            response = requests.get(war_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                war_data = response.json()
                print(f"✅ Savaş verisi alındı")
                return war_data
            else:
                print(f"⚠️ Savaş verisi alınamadı: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Savaş API hatası: {e}")
            return None
    
    def analyze_clan_member_performance(self, member, war_data=None):
        """Üye performansını analiz et"""
        score = 0
        reasons = []
        
        # Bağış skoru (0-40 puan)
        donations = member.get('donations', 0)
        received = member.get('donationsReceived', 0)
        
        if donations >= 1000:
            score += 40
            reasons.append("🎁 Mükemmel bağış")
        elif donations >= 500:
            score += 30
            reasons.append("🎁 İyi bağış")
        elif donations >= 200:
            score += 20
            reasons.append("🎁 Orta bağış")
        elif donations >= 50:
            score += 10
            reasons.append("🎁 Az bağış")
        else:
            reasons.append("❌ Bağış yok")
        
        # Aktiflik skoru (trophies değişimi)
        trophies = member.get('trophies', 0)
        if trophies >= 3000:
            score += 20
            reasons.append("🏆 Yüksek kupa")
        elif trophies >= 2000:
            score += 15
            reasons.append("🏆 Orta kupa")
        elif trophies >= 1000:
            score += 10
            reasons.append("🏆 Düşük kupa")
        
        # Savaş performansı (varsa)
        if war_data and war_data.get('state') in ['inWar', 'warEnded']:
            # Savaş üyesi kontrolü
            for war_member in war_data.get('clan', {}).get('members', []):
                if war_member['tag'] == member['tag']:
                    attacks = war_member.get('attacks', [])
                    if attacks:
                        total_stars = sum(attack.get('stars', 0) for attack in attacks)
                        if total_stars >= 4:
                            score += 30
                            reasons.append("⚔️ Mükemmel savaş")
                        elif total_stars >= 2:
                            score += 20
                            reasons.append("⚔️ İyi savaş")
                        else:
                            score += 10
                            reasons.append("⚔️ Zayıf savaş")
                    else:
                        reasons.append("❌ Savaş yapmadı")
                    break
        
        return score, reasons
    
    def get_recommended_role(self, score, current_role):
        """Performansa göre önerilen rütbe"""
        if score >= 80:
            return 'admin'  # Başkan
        elif score >= 50:
            return 'member'  # Aktif üye kalır
        else:
            return 'member'  # Pasif üye
    
    def analyze_clan(self):
        """Tam klan analizi"""
        print("🔍 Klan analizi başlıyor...")
        
        clan_data = self.get_clan_data()
        war_data = self.get_clan_war_data()
        
        if not clan_data:
            print("❌ Klan verisi alınamadı")
            return
        
        analysis_time = datetime.now().isoformat()
        
        # Klan analiz sonuçları
        analysis = {
            'timestamp': analysis_time,
            'clan_info': {
                'name': clan_data['name'],
                'level': clan_data['clanLevel'],
                'members': clan_data['members'],
                'total_points': clan_data['clanPoints'],
                'war_wins': clan_data.get('warWins', 0),
                'war_losses': clan_data.get('warLosses', 0)
            },
            'member_analysis': [],
            'role_recommendations': [],
            'inactive_members': [],
            'top_performers': []
        }
        
        print(f"📊 Analiz ediliyor: {clan_data['name']} ({clan_data['members']} üye)")
        
        # Her üyeyi analiz et
        for member in clan_data['memberList']:
            score, reasons = self.analyze_clan_member_performance(member, war_data)
            current_role = member['role']
            recommended_role = self.get_recommended_role(score, current_role)
            
            member_analysis = {
                'name': member['name'],
                'tag': member['tag'],
                'role': current_role,
                'recommended_role': recommended_role,
                'score': score,
                'reasons': reasons,
                'donations': member.get('donations', 0),
                'trophies': member.get('trophies', 0)
            }
            
            analysis['member_analysis'].append(member_analysis)
            
            # Rütbe değişikliği önerisi
            if recommended_role != current_role and recommended_role != 'coLeader':
                role_change = {
                    'name': member['name'],
                    'current': ROLE_NAMES.get(current_role, current_role),
                    'recommended': ROLE_NAMES.get(recommended_role, recommended_role),
                    'score': score,
                    'reason': f"Performans: {score}/100"
                }
                analysis['role_recommendations'].append(role_change)
            
            # Pasif üyeler
            if score < 30:
                analysis['inactive_members'].append({
                    'name': member['name'],
                    'score': score,
                    'issues': [r for r in reasons if '❌' in r]
                })
            
            # En iyi performans
            if score >= 70:
                analysis['top_performers'].append({
                    'name': member['name'],
                    'score': score
                })
        
        # Sonuçları kaydet
        self.clan_history[analysis_time] = analysis
        self.save_data()
        
        print(f"✅ Klan analizi tamamlandı!")
        print(f"👑 En iyi performans: {len(analysis['top_performers'])} üye")
        print(f"⚠️ Pasif üye: {len(analysis['inactive_members'])} üye")
        print(f"🔄 Rütbe önerisi: {len(analysis['role_recommendations'])} üye")
        
        return analysis
    
    def start_auto_clan_monitoring(self):
        """Otomatik klan izleme başlat"""
        def monitor_loop():
            while True:
                try:
                    print("🔄 Otomatik klan kontrolü...")
                    self.analyze_clan()
                    print("💤 Bir sonraki kontrol 1 saat sonra...")
                    time.sleep(3600)  # 1 saat bekle
                except Exception as e:
                    print(f"❌ Otomatik kontrol hatası: {e}")
                    time.sleep(1800)  # Hata durumunda 30 dakika bekle
        
        # Arka planda çalıştır
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        print("🤖 Otomatik klan izleme başlatıldı (her saat)")
    
    def get_latest_clan_analysis(self):
        """En son klan analizini getir"""
        if self.clan_history:
            latest_key = max(self.clan_history.keys())
            return self.clan_history[latest_key]
        return None
    
    def send_message(self, chat_id, text, reply_markup=None):
        """Mesaj gönder"""
        url = f"{self.base_url}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        if reply_markup:
            data['reply_markup'] = reply_markup
        
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Mesaj gönderme hatası: {e}")
            return None
    
    def get_updates(self):
        """Telegram güncellemelerini al"""
        url = f"{self.base_url}/getUpdates"
        params = {'offset': self.offset, 'timeout': 5}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Güncelleme alma hatası: {e}")
            return None
    
    def handle_start(self, message):
        """Start komutu"""
        user_id = str(message['from']['id'])
        first_name = message['from'].get('first_name', 'Üye')
        chat_id = message['chat']['id']
        
        # Kullanıcıyı kaydet
        if user_id not in self.users:
            self.users[user_id] = {
                'name': first_name,
                'coc_tag': None,
                'warnings': 0,
                'wars': 0,
                'stars': 0,
                'join_date': self.today,
                'last_active': self.today
            }
        else:
            self.users[user_id]['last_active'] = self.today
        
        # Günlük aktiflik
        if self.today not in self.daily_stats:
            self.daily_stats[self.today] = {
                'active_users': [],
                'new_registrations': [],
                'warnings_given': 0,
                'total_messages': 0,
                'start_time': datetime.now().isoformat()
            }
        
        if user_id not in self.daily_stats[self.today]['active_users']:
            self.daily_stats[self.today]['active_users'].append(user_id)
        
        # Klan durumu özeti
        clan_summary = self.get_clan_summary()
        
        text = f"""🏰 **Kemal'in Değneği - Otomatik Klan Yöneticisi**

Hoş geldin {first_name}! ⚔️

🤖 **Otomatik Özellikler:**
• 🔄 Saatlik klan analizi
• 👑 Otomatik rütbe önerileri  
• ⚠️ Pasif üye tespiti
• 📊 Gerçek zamanlı istatistikler

{clan_summary}

🎯 **Komutlar:**
• **KLAN** - Canlı klan durumu
• **ANALIZ** - Son analiz raporu
• **RUTBE** - Rütbe önerileri
• **PASIF** - Pasif üyeler
• **GUNLUK** - Günlük rapor
• **HAFTALIK** - Haftalık analiz"""
        
        self.send_message(chat_id, text)
        self.save_data()
    
    def get_clan_summary(self):
        """Klan özeti hazırla"""
        analysis = self.get_latest_clan_analysis()
        
        if not analysis:
            return "📊 **Klan Durumu:** İlk analiz yapılıyor..."
        
        clan_info = analysis['clan_info']
        inactive_count = len(analysis['inactive_members'])
        top_count = len(analysis['top_performers'])
        role_changes = len(analysis['role_recommendations'])
        
        last_update = datetime.fromisoformat(analysis['timestamp'])
        time_ago = datetime.now() - last_update
        hours_ago = int(time_ago.total_seconds() / 3600)
        
        return f"""📊 **Klan Durumu:**
🏰 {clan_info['name']} (Seviye {clan_info['level']})
👥 Üye: {clan_info['members']}/50
🏆 Klan Puanı: {clan_info['total_points']:,}
⚔️ Savaş: {clan_info['war_wins']}W-{clan_info['war_losses']}L

🎯 **Analiz Sonuçları:**
👑 En iyi performans: {top_count} üye
⚠️ Pasif üye: {inactive_count} üye  
🔄 Rütbe önerisi: {role_changes} üye

🕐 Son analiz: {hours_ago} saat önce"""
    
    def handle_klan_command(self, message):
        """KLAN komutu - Canlı klan durumu"""
        chat_id = message['chat']['id']
        
        # Anlık klan verisi çek
        clan_data = self.get_clan_data()
        war_data = self.get_clan_war_data()
        
        if not clan_data:
            text = "❌ Klan verilerine erişilemiyor. Lütfen daha sonra deneyin."
            self.send_message(chat_id, text)
            return
        
        # Savaş durumu
        war_status = "🔄 Savaş yok"
        if war_data:
            if war_data.get('state') == 'preparation':
                war_status = "⏳ Savaş hazırlığı"
            elif war_data.get('state') == 'inWar':
                war_status = "⚔️ Savaş devam ediyor"
            elif war_data.get('state') == 'warEnded':
                war_status = "✅ Savaş bitti"
        
        text = f"""🏰 **{clan_data['name']} - Canlı Durum**

👥 **Üye Bilgileri:**
• Toplam üye: {clan_data['members']}/50
• Klan seviyesi: {clan_data['clanLevel']}
• Klan puanı: {clan_data['clanPoints']:,}

⚔️ **Savaş Bilgileri:**
• Durum: {war_status}
• Galibiyet: {clan_data.get('warWins', 0)}
• Mağlubiyet: {clan_data.get('warLosses', 0)}

📊 **En Aktif 5 Üye:**"""
        
        # En aktif üyeleri göster (bağış bazında)
        sorted_members = sorted(clan_data['memberList'], 
                              key=lambda x: x.get('donations', 0), reverse=True)
        
        for i, member in enumerate(sorted_members[:5], 1):
            role_emoji = {'leader': '👑', 'coLeader': '🔱', 'admin': '⭐', 'member': '👤'}.get(member['role'], '👤')
            text += f"\n{i}. {role_emoji} {member['name']} - {member.get('donations', 0)} bağış"
        
        text += f"\n\n🕐 Anlık veri - {datetime.now().strftime('%H:%M')}"
        
        self.send_message(chat_id, text)
    
    def handle_analiz_command(self, message):
        """ANALIZ komutu - Son analiz raporu"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
            self.send_message(chat_id, text)
            return
        
        analysis = self.get_latest_clan_analysis()
        
        if not analysis:
            text = "❌ Henüz analiz yapılmamış. Lütfen bekleyin..."
            self.send_message(chat_id, text)
            return
        
        clan_info = analysis['clan_info']
        last_update = datetime.fromisoformat(analysis['timestamp'])
        
        text = f"""📊 **Detaylı Klan Analizi**

🏰 **{clan_info['name']}**
📅 Analiz: {last_update.strftime('%d.%m.%Y %H:%M')}

👑 **En İyi Performans ({len(analysis['top_performers'])}):**"""
        
        for performer in analysis['top_performers'][:5]:
            text += f"\n• {performer['name']} - {performer['score']}/100"
        
        text += f"\n\n⚠️ **Pasif Üyeler ({len(analysis['inactive_members'])}):**"
        
        for inactive in analysis['inactive_members'][:5]:
            issues = ', '.join(inactive['issues'][:2])
            text += f"\n• {inactive['name']} - {inactive['score']}/100 ({issues})"
        
        text += f"\n\n🔄 **Rütbe Önerileri ({len(analysis['role_recommendations'])}):**"
        
        for role_rec in analysis['role_recommendations'][:5]:
            text += f"\n• {role_rec['name']}: {role_rec['current']} → {role_rec['recommended']}"
        
        if len(analysis['role_recommendations']) > 5:
            text += f"\n... ve {len(analysis['role_recommendations'])-5} üye daha"
        
        self.send_message(chat_id, text)
    
    def handle_rutbe_command(self, message):
        """RUTBE komutu - Rütbe önerileri"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
            self.send_message(chat_id, text)
            return
        
        analysis = self.get_latest_clan_analysis()
        
        if not analysis:
            text = "❌ Henüz analiz yapılmamış."
            self.send_message(chat_id, text)
            return
        
        role_recs = analysis['role_recommendations']
        
        if not role_recs:
            text = "✅ **Tüm üyelerin rütbeleri uygun!**\n\nHerkes performansına göre doğru rütbede."
        else:
            text = f"""👑 **Rütbe Değişiklik Önerileri**

🔄 **{len(role_recs)} üye için öneri:**

"""
            
            for rec in role_recs:
                direction = "⬆️" if rec['recommended'] == 'admin' else "⬇️"
                text += f"{direction} **{rec['name']}**\n"
                text += f"   {rec['current']} → {rec['recommended']}\n"
                text += f"   Performans: {rec['score']}/100\n\n"
            
            text += "⚠️ **Not:** Yardımcı Lider ataması güvenlik nedeniyle manuel yapılmalı."
        
        self.send_message(chat_id, text)
    
    def handle_pasif_command(self, message):
        """PASIF komutu - Pasif üyeler"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
            self.send_message(chat_id, text)
            return
        
        analysis = self.get_latest_clan_analysis()
        
        if not analysis:
            text = "❌ Henüz analiz yapılmamış."
            self.send_message(chat_id, text)
            return
        
        inactive_members = analysis['inactive_members']
        
        if not inactive_members:
            text = "🎉 **Harika! Pasif üye yok!**\n\nTüm klan üyeleri aktif gözüküyor."
        else:
            text = f"""⚠️ **Pasif Üye Raporu**

🔍 **{len(inactive_members)} pasif üye tespit edildi:**

"""
            
            for inactive in inactive_members:
                text += f"👤 **{inactive['name']}** - {inactive['score']}/100\n"
                text += f"   Sorunlar: {', '.join(inactive['issues'])}\n\n"
            
            text += """💡 **Öneriler:**
• Bu üyeleri uyarın
• Aktiflik artmazsa rütbe düşürün
• Çok pasifse klandan çıkarın"""
        
        self.send_message(chat_id, text)
    
    def handle_text_message(self, message):
        """Metin mesajlarını işle"""
        user_id = str(message['from']['id'])
        chat_id = message['chat']['id']
        text = message['text'].upper()
        
        # Günlük mesaj sayısını artır
        if self.today not in self.daily_stats:
            self.daily_stats[self.today] = {
                'active_users': [],
                'new_registrations': [],
                'warnings_given': 0,
                'total_messages': 0,
                'start_time': datetime.now().isoformat()
            }
        
        self.daily_stats[self.today]['total_messages'] += 1
        
        if text == '/START' or text == 'START':
            self.handle_start(message)
        elif text == 'KLAN':
            self.handle_klan_command(message)
        elif text == 'ANALIZ':
            self.handle_analiz_command(message)
        elif text == 'RUTBE':
            self.handle_rutbe_command(message)
        elif text == 'PASIF':
            self.handle_pasif_command(message)
        elif text == 'GUNLUK':
            self.handle_gunluk_command(message)
        elif text == 'HAFTALIK':
            self.handle_haftalik_command(message)
        elif text == 'COC':
            self.send_message(chat_id, "🏰 **COC Tag'inizi yazın:**\n📋 Örnek: #ABC123XYZ")
        elif text.startswith('#') and len(text) >= 4:
            # COC tag kaydet
            if user_id in self.users:
                self.users[user_id]['coc_tag'] = text
                self.send_message(chat_id, f"✅ **COC tag kaydedildi!**\n🏷️ **Tag:** `{text}`")
                self.save_data()
        elif text == 'STATS':
            self.handle_stats_command(message)
        else:
            # Küfür kontrolü
            self.check_profanity(message)
    
    def handle_gunluk_command(self, message):
        """Günlük rapor komutu"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
        else:
            today_data = self.daily_stats.get(self.today, {})
            analysis = self.get_latest_clan_analysis()
            
            text = f"""📊 **Günlük Detaylı Rapor - {self.today}**

🤖 **Otomatik Klan Analizi:**"""
            
            if analysis:
                clan_info = analysis['clan_info']
                text += f"""
🏰 {clan_info['name']} - {clan_info['members']} üye
👑 En iyi performans: {len(analysis['top_performers'])} üye
⚠️ Pasif üye: {len(analysis['inactive_members'])} üye
🔄 Rütbe önerisi: {len(analysis['role_recommendations'])} üye"""
            else:
                text += "\n⏳ İlk analiz bekleniyor..."
            
            text += f"""

👥 **Bot Kullanım İstatistikleri:**
• Toplam aktif: {len(today_data.get('active_users', []))}
• Yeni kayıt: {len(today_data.get('new_registrations', []))}
• Toplam mesaj: {today_data.get('total_messages', 0)}
• Verilen uyarı: {today_data.get('warnings_given', 0)}

🕐 **Başlatma:** {today_data.get('start_time', 'Bilinmiyor')[:16]}"""
        
        self.send_message(chat_id, text)
    
    def handle_haftalik_command(self, message):
        """Haftalık analiz komutu"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
        else:
            # Son 7 günün analizi
            last_7_days = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                last_7_days.append(date)
            
            total_active = 0
            total_warnings = 0
            total_messages = 0
            
            for date in last_7_days:
                if date in self.daily_stats:
                    day_data = self.daily_stats[date]
                    total_active += len(day_data.get('active_users', []))
                    total_warnings += day_data.get('warnings_given', 0)
                    total_messages += day_data.get('total_messages', 0)
            
            # Klan trend analizi
            analyses = list(self.clan_history.values())[-7:]  # Son 7 analiz
            
            text = f"""📈 **Haftalık Klan Analizi**

🤖 **Otomatik Takip Sonuçları:**"""
            
            if analyses:
                avg_inactive = sum(len(a.get('inactive_members', [])) for a in analyses) / len(analyses)
                avg_top = sum(len(a.get('top_performers', [])) for a in analyses) / len(analyses)
                
                text += f"""
📊 Ortalama pasif üye: {avg_inactive:.1f}
🏆 Ortalama en iyi: {avg_top:.1f}
🔄 Toplam analiz: {len(analyses)}"""
            
            text += f"""

👥 **Bot Aktivite (7 gün):**
• Toplam aktiflik: {total_active}
• Toplam uyarı: {total_warnings}
• Toplam mesaj: {total_messages}

🎯 **Öneriler:**"""
            
            if total_warnings > 10:
                text += "\n⚠️ Uyarı sayısı yüksek, kural hatırlatması yapın"
            
            if analyses and avg_inactive > 5:
                text += "\n👥 Pasif üye sayısı yüksek, temizlik gerekli"
            
            if total_active < 20:
                text += "\n📢 Bot kullanımı düşük, üyeleri teşvik edin"
            
            if not any([total_warnings > 10, analyses and avg_inactive > 5, total_active < 20]):
                text += "\n🎉 Her şey yolunda gidiyor!"
        
        self.send_message(chat_id, text)
    
    def handle_stats_command(self, message):
        """İstatistik komutu"""
        user_id = str(message['from']['id'])
        chat_id = message['chat']['id']
        
        if user_id not in self.users:
            text = "❌ Önce START yazın!"
        elif not self.users[user_id]['coc_tag']:
            text = "❌ COC kaydınız yok! **COC** yazarak kayıt olun."
        else:
            user_data = self.users[user_id]
            days_active = (datetime.now() - datetime.strptime(user_data['join_date'], '%Y-%m-%d')).days + 1
            
            # Klan analizinde kullanıcıyı bul
            analysis = self.get_latest_clan_analysis()
            user_analysis = None
            
            if analysis:
                for member in analysis['member_analysis']:
                    if member['tag'] == user_data['coc_tag']:
                        user_analysis = member
                        break
            
            text = f"""⚔️ **Kişisel İstatistikler**

👤 **Oyuncu:** {user_data['name']}
🏷️ **COC Tag:** `{user_data['coc_tag']}`
📅 **Katılım:** {user_data['join_date']} ({days_active} gün)
⚠️ **Uyarılar:** {user_data['warnings']}/3"""
            
            if user_analysis:
                text += f"""

🤖 **Otomatik Analiz:**
📊 Performans skoru: {user_analysis['score']}/100
👑 Mevcut rütbe: {ROLE_NAMES.get(user_analysis['role'], user_analysis['role'])}
🎯 Önerilen rütbe: {ROLE_NAMES.get(user_analysis['recommended_role'], user_analysis['recommended_role'])}
🎁 Bağış: {user_analysis['donations']}
🏆 Kupa: {user_analysis['trophies']}

💡 **Değerlendirme:**"""
                
                for reason in user_analysis['reasons'][:3]:
                    text += f"\n• {reason}"
                
                if user_analysis['score'] >= 70:
                    text += "\n\n🌟 **Harika performans! Klanın gururu!**"
                elif user_analysis['score'] >= 50:
                    text += "\n\n👍 **İyi gidiyorsun! Devam et!**"
                else:
                    text += "\n\n⚡ **Daha aktif olmalısın!**"
        
        self.send_message(chat_id, text)
    
    def check_profanity(self, message):
        """Küfür kontrolü"""
        user_id = str(message['from']['id'])
        chat_id = message['chat']['id']
        text_lower = message['text'].lower()
        
        for bad_word in BAD_WORDS:
            if bad_word in text_lower:
                if user_id in self.users:
                    self.users[user_id]['warnings'] += 1
                    self.daily_stats[self.today]['warnings_given'] += 1
                    
                    if user_id not in self.warnings_data:
                        self.warnings_data[user_id] = []
                    
                    self.warnings_data[user_id].append({
                        'reason': 'Küfür/Hakaret',
                        'date': self.today,
                        'time': datetime.now().strftime('%H:%M')
                    })
                    
                    warnings = self.users[user_id]['warnings']
                    name = self.users[user_id]['name']
                    
                    if warnings >= 3:
                        self.send_message(chat_id, f"🚫 **{name}** 3 uyarı aldığı için klandan atılmalı!")
                    else:
                        self.send_message(chat_id, f"⚠️ **{name}**, küfür yasak! Uyarı: {warnings}/3")
                    
                    self.save_data()
                return
    
    def run(self):
        """Botu çalıştır"""
        print("🏰 Kemal'in Değneği - Tam Otomatik Klan Yöneticisi")
        print("🤖 Clash of Clans API entegrasyonu aktif")
        print("🔄 Otomatik saatlik klan analizi çalışıyor")
        print("📱 Telegram komutu: /start")
        print("🛑 Durdurmak için Ctrl+C")
        print("-" * 60)
        
        try:
            while True:
                updates = self.get_updates()
                
                if updates and updates.get('ok'):
                    for update in updates['result']:
                        self.offset = update['update_id'] + 1
                        
                        if 'message' in update and 'text' in update['message']:
                            print(f"📨 Mesaj: {update['message']['text']}")
                            self.handle_text_message(update['message'])
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n💾 Veriler kaydediliyor...")
            self.save_data()
            print("🛑 Bot durduruldu!")
        except Exception as e:
            print(f"❌ Ana hata: {e}")
            self.save_data()

if __name__ == '__main__':
    bot = AutoClanManager()
    bot.run()
