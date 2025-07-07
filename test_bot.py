import requests
import time
import json
import os
from datetime import datetime, timedelta

BOT_TOKEN = "7341092014:AAFegDvTd2ozU7fWMoyxriJuCn5wqkypvaY"
ADMIN_USERS = ["8114999904"]  # Buraya kendi Telegram ID'nizi yazın

class DailyActiveClanBot:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        self.offset = 0
        self.data_file = "clan_data.json"
        self.load_data()
        self.today = datetime.now().strftime('%Y-%m-%d')
        print(f"✅ Bot başlatıldı - Tarih: {self.today}")
        
        # Günlük analiz yap
        self.daily_analysis()
        
    def load_data(self):
        """Kalıcı verileri dosyadan yükle"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.daily_stats = data.get('daily_stats', {})
                    self.warnings_data = data.get('warnings_data', {})
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
        print("🔄 Yeni veri yapısı oluşturuldu")
    
    def save_data(self):
        """Verileri dosyaya kaydet"""
        data = {
            'users': self.users,
            'daily_stats': self.daily_stats,
            'warnings_data': self.warnings_data,
            'last_save': datetime.now().isoformat()
        }
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("💾 Veriler kaydedildi")
        except Exception as e:
            print(f"❌ Kaydetme hatası: {e}")
    
    def daily_analysis(self):
        """Günlük analiz ve rapor"""
        today = self.today
        
        if today not in self.daily_stats:
            self.daily_stats[today] = {
                'active_users': [],
                'new_registrations': [],
                'warnings_given': 0,
                'total_messages': 0,
                'start_time': datetime.now().isoformat()
            }
        
        # Son 7 günün analizi
        self.weekly_analysis()
        
        print(f"📊 Günlük analiz tamamlandı: {today}")
    
    def weekly_analysis(self):
        """Haftalık trend analizi"""
        last_7_days = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            last_7_days.append(date)
        
        weekly_data = {
            'dates': last_7_days,
            'active_users': 0,
            'total_warnings': 0,
            'new_members': 0
        }
        
        for date in last_7_days:
            if date in self.daily_stats:
                day_data = self.daily_stats[date]
                weekly_data['active_users'] += len(day_data.get('active_users', []))
                weekly_data['total_warnings'] += day_data.get('warnings_given', 0)
                weekly_data['new_members'] += len(day_data.get('new_registrations', []))
        
        self.weekly_data = weekly_data
        return weekly_data
    
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
            # Yeni kayıt
            self.daily_stats[self.today]['new_registrations'].append(user_id)
        else:
            # Mevcut kullanıcı
            self.users[user_id]['last_active'] = self.today
        
        # Günlük aktiflik
        if user_id not in self.daily_stats[self.today]['active_users']:
            self.daily_stats[self.today]['active_users'].append(user_id)
        
        # Günlük özet
        daily_summary = self.get_daily_summary()
        
        text = f"""🏰 **Kemal'in Değneği - Günlük Aktif Bot**

Hoş geldin {first_name}! ⚔️

📊 **Bugünün Özeti:**
{daily_summary}

🎯 **Komutlar:**
• **COC** - Clash of Clans kayıt
• **STATS** - Kişisel istatistikler
• **GUNLUK** - Günlük rapor
• **HAFTALIK** - Haftalık analiz
• **KLAN** - Klan durumu

💬 **Kullanım:** Sadece komut yazın"""
        
        self.send_message(chat_id, text)
        self.save_data()
    
    def get_daily_summary(self):
        """Günlük özet hazırla"""
        today_data = self.daily_stats[self.today]
        
        active_count = len(today_data['active_users'])
        new_count = len(today_data['new_registrations'])
        warnings_count = today_data['warnings_given']
        
        # Performans analizi
        total_registered = len([u for u in self.users.values() if u['coc_tag']])
        avg_performance = 0
        if total_registered > 0:
            total_avg = sum([u['stars']/(u['wars']*2) if u['wars'] > 0 else 0 for u in self.users.values() if u['coc_tag']])
            avg_performance = total_avg / total_registered
        
        summary = f"""👥 Bugün aktif: {active_count}
🆕 Yeni kayıt: {new_count}
⚠️ Verilen uyarı: {warnings_count}
📈 Klan ortalaması: {avg_performance:.1f}⭐"""
        
        return summary
    
    def handle_gunluk_command(self, message):
        """Günlük rapor komutu"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
        else:
            # Detaylı günlük rapor
            today_data = self.daily_stats[self.today]
            
            text = f"""📊 **Günlük Detaylı Rapor - {self.today}**

👥 **Kullanıcı Aktivitesi:**
• Toplam aktif: {len(today_data['active_users'])}
• Yeni kayıt: {len(today_data['new_registrations'])}
• Toplam mesaj: {today_data['total_messages']}

⚠️ **Uyarı İstatistikleri:**
• Bugün verilen: {today_data['warnings_given']}
• Toplam uyarılı üye: {len([u for u in self.users.values() if u['warnings'] > 0])}

🏆 **Performans:**
• Kayıtlı üye: {len([u for u in self.users.values() if u['coc_tag']])}
• En aktif: {self.get_most_active()}

🕐 **Başlatma:** {today_data['start_time'][:16]}"""
        
        self.send_message(chat_id, text)
    
    def handle_haftalik_command(self, message):
        """Haftalık analiz komutu"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
        else:
            weekly = self.weekly_data
            
            text = f"""📈 **Haftalık Analiz Raporu**

📊 **Son 7 Gün Özeti:**
• Toplam aktiflik: {weekly['active_users']} 
• Yeni üyeler: {weekly['new_members']}
• Toplam uyarılar: {weekly['total_warnings']}

📅 **Trend Analizi:**
{self.get_weekly_trends()}

🎯 **Öneriler:**
{self.get_recommendations()}"""
        
        self.send_message(chat_id, text)
    
    def get_most_active(self):
        """En aktif kullanıcıyı bul"""
        today_actives = self.daily_stats[self.today]['active_users']
        if today_actives:
            most_active_id = today_actives[0]
            return self.users[most_active_id]['name']
        return "Henüz yok"
    
    def get_weekly_trends(self):
        """Haftalık trendleri analiz et"""
        # Basit trend analizi
        if self.weekly_data['active_users'] > 10:
            return "📈 Aktivite yüksek seviyede"
        elif self.weekly_data['active_users'] > 5:
            return "📊 Aktivite orta seviyede"
        else:
            return "📉 Aktivite düşük, teşvik gerekli"
    
    def get_recommendations(self):
        """Haftalık önerileri hazırla"""
        recommendations = []
        
        if self.weekly_data['total_warnings'] > 5:
            recommendations.append("⚠️ Uyarı sayısı yüksek, kural hatırlatması yapın")
        
        if self.weekly_data['new_members'] < 2:
            recommendations.append("👥 Yeni üye sayısı düşük, tanıtım yapın")
        
        if self.weekly_data['active_users'] < 10:
            recommendations.append("🎯 Aktivite düşük, etkinlik düzenleyin")
        
        if not recommendations:
            recommendations.append("🎉 Her şey yolunda gidiyor!")
        
        return "\n".join([f"• {rec}" for rec in recommendations])
    
    def handle_text_message(self, message):
        """Metin mesajlarını işle"""
        user_id = str(message['from']['id'])
        chat_id = message['chat']['id']
        text = message['text'].upper()
        
        # Günlük mesaj sayısını artır
        self.daily_stats[self.today]['total_messages'] += 1
        
        if text == '/START' or text == 'START':
            self.handle_start(message)
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
        elif text == 'KLAN':
            self.handle_klan_command(message)
        else:
            # Küfür kontrolü
            self.check_profanity(message)
    
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
            
            text = f"""⚔️ **Kişisel İstatistikler**

👤 **Oyuncu:** {user_data['name']}
🏷️ **COC Tag:** `{user_data['coc_tag']}`
📅 **Katılım:** {user_data['join_date']} ({days_active} gün)
⚠️ **Uyarılar:** {user_data['warnings']}/3
🏆 **Savaşlar:** {user_data['wars']}
⭐ **Yıldızlar:** {user_data['stars']}"""
        
        self.send_message(chat_id, text)
    
    def handle_klan_command(self, message):
        """Klan durumu komutu"""
        chat_id = message['chat']['id']
        
        total_users = len(self.users)
        registered_users = len([u for u in self.users.values() if u['coc_tag']])
        today_active = len(self.daily_stats[self.today]['active_users'])
        
        text = f"""🏰 **Klan Durumu**

👥 **Üye İstatistikleri:**
• Toplam üye: {total_users}
• COC kayıtlı: {registered_users}
• Bugün aktif: {today_active}

📊 **Günlük Veriler:**
{self.get_daily_summary()}

🕐 **Son güncelleme:** {datetime.now().strftime('%H:%M')}"""
        
        self.send_message(chat_id, text)
    
    def check_profanity(self, message):
        """Küfür kontrolü"""
        bad_words = ['aptal', 'salak', 'mal', 'ahmak']
        user_id = str(message['from']['id'])
        chat_id = message['chat']['id']
        text_lower = message['text'].lower()
        
        for bad_word in bad_words:
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
        print("🏰 Kemal'in Değneği - Günlük Aktif Bot")
        print("📊 Günlük analiz ve veri saklama aktif")
        print("📱 Telegram'da /start gönderin")
        print("🛑 Ctrl+C ile durdurun")
        print("-" * 50)
        
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
            print(f"❌ Hata: {e}")
            self.save_data()

if __name__ == '__main__':
    bot = DailyActiveClanBot()
    bot.run()