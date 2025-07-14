import requests
import time
import json
import os
import asyncio
import threading
from datetime import datetime, timedelta

# Environment variables'dan güvenli token alma
BOT_TOKEN = os.getenv('BOT_TOKEN', '7708393145:AAFHHNBUNNMhx8mTCZ4iWy83ZdgiNB-SoNc')
COC_API_TOKEN = os.getenv('COC_API_TOKEN', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjI5Y2QzZGJhLTEzMjktNDBmMy05MmFkLTg0NmJkZmQwNjI4YyIsImlhdCI6MTc1MTkxMjAxNywic3ViIjoiZGV2ZWxvcGVyLzRiYTU2MTc5LWE5NDgtMTBkYy0yNmI1LThkZjc5NjcyYjRmNCIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjUyLjU3LjMzLjE3NyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.K6meIBPNtbmzBeefJ3Naa2pF7fRgoCB6UYXCRitdg6LKyBwj02pL0wEYe4fhTlrwO9eHtDgAuqHiYz36M6RLhQ')

# Diğer ayarlar
ADMIN_USERS = os.getenv('ADMIN_USERS', '8114999904').split(',')
CLAN_TAG = os.getenv('CLAN_TAG', '#2RGC8UPYV')
COC_API_BASE = "https://api.clashofclans.com/v1"

# AWS Lambda uyumluluğu için
RUNNING_ON_AWS = os.getenv('AWS_EXECUTION_ENV') is not None
DATA_PATH = '/tmp/' if RUNNING_ON_AWS else './'

# Token'dan IP çıkar (JWT decode)
def get_token_ip():
    """Token'dan kayıtlı IP'yi çıkar"""
    try:
        import base64
        # JWT'nin payload kısmını al
        token_parts = COC_API_TOKEN.split('.')
        if len(token_parts) >= 2:
            payload = token_parts[1]
            # Base64 padding ekle
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(payload)
            payload_data = json.loads(decoded.decode('utf-8'))
            
            # limits içinden IP'yi bul
            limits = payload_data.get('limits', [])
            for limit in limits:
                if limit.get('type') == 'client':
                    cidrs = limit.get('cidrs', [])
                    if cidrs:
                        return cidrs[0]  # İlk IP'yi dön
        return "Bulunamadı"
    except Exception as e:
        print(f"Token IP çıkarma hatası: {e}")
        return "52.57.33.177"  # Yeni token IP'si

# IP adresini öğren ve yazdır
def get_current_ip():
    try:
        ip = requests.get('https://httpbin.org/ip', timeout=5).json()['origin']
        print(f"🌐 Bot IP adresi: {ip}")
        return ip
    except Exception as e:
        print(f"IP bulunamadı: {e}")
        return None

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
        self.data_file = os.path.join(DATA_PATH, "clan_data.json")
        self.load_data()
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.last_clan_check = None
        self.current_ip = get_current_ip()
        self.token_ip = get_token_ip()
        
        print(f"✅ Bot başlatıldı - Tarih: {self.today}")
        print(f"🔧 AWS Mode: {'✓' if RUNNING_ON_AWS else '✗'}")
        print(f"📁 Data Path: {DATA_PATH}")
        print(f"🌐 Current IP: {self.current_ip}")
        print(f"🔑 Token IP: {self.token_ip}")
        
        # IP uyumsuzluğu kontrolü
        if self.current_ip and self.current_ip != self.token_ip:
            print("⚠️ IP UYUMSUZLUĞU TESPİT EDİLDİ!")
            print(f"   Mevcut IP: {self.current_ip}")
            print(f"   Token IP: {self.token_ip}")
        else:
            print("✅ IP Durumu: Eşleşiyor")
        
        # İlk klan analizi
        self.analyze_clan()

        # ==================== SAVAS ANALİZ FONKSİYONLARI ====================
    
    def get_war_analysis(self):
        """Detaylı savaş analizi ve eşleştirme değerlendirmesi"""
        war_data = self.get_clan_war_data()
        
        if not war_data or war_data.get('state') == 'notInWar':
            return None
        
        our_clan = war_data.get('clan', {})
        enemy_clan = war_data.get('opponent', {})
        
        analysis = {
            'war_state': war_data.get('state'),
            'preparation_start': war_data.get('preparationStartTime'),
            'start_time': war_data.get('startTime'),
            'end_time': war_data.get('endTime'),
            'team_size': war_data.get('teamSize'),
            'our_clan': {
                'name': our_clan.get('name'),
                'tag': our_clan.get('tag'),
                'level': our_clan.get('clanLevel'),
                'stars': our_clan.get('stars', 0),
                'destruction': our_clan.get('destructionPercentage', 0),
                'attacks_used': our_clan.get('attacksUsed', 0),
                'attacks_remaining': (war_data.get('teamSize', 0) * 2) - our_clan.get('attacksUsed', 0)
            },
            'enemy_clan': {
                'name': enemy_clan.get('name'),
                'tag': enemy_clan.get('tag'),
                'level': enemy_clan.get('clanLevel'),
                'stars': enemy_clan.get('stars', 0),
                'destruction': enemy_clan.get('destructionPercentage', 0),
                'attacks_used': enemy_clan.get('attacksUsed', 0)
            },
            'matchup_analysis': self.analyze_war_matchup(our_clan, enemy_clan),
            'member_status': self.analyze_war_members(our_clan, enemy_clan),
            'recommended_strategy': None
        }
        
        # Strateji önerisi
        analysis['recommended_strategy'] = self.generate_war_strategy(analysis)
        
        return analysis

    def analyze_war_matchup(self, our_clan, enemy_clan):
        """Savaş eşleştirmesi analizi - rakip klan güçlü mü?"""
        our_members = our_clan.get('members', [])
        enemy_members = enemy_clan.get('members', [])
        
        if not our_members or not enemy_members:
            return {'status': 'unknown', 'details': 'Üye bilgileri bulunamadı'}
        
        # Güç karşılaştırması
        our_total_th = sum(member.get('townhallLevel', 0) for member in our_members)
        enemy_total_th = sum(member.get('townhallLevel', 0) for member in enemy_members)
        
        our_avg_th = our_total_th / len(our_members)
        enemy_avg_th = enemy_total_th / len(enemy_members)
        
        # TH dağılımı analizi
        our_th_distribution = {}
        enemy_th_distribution = {}
        
        for member in our_members:
            th_level = member.get('townhallLevel', 0)
            our_th_distribution[th_level] = our_th_distribution.get(th_level, 0) + 1
        
        for member in enemy_members:
            th_level = member.get('townhallLevel', 0)
            enemy_th_distribution[th_level] = enemy_th_distribution.get(th_level, 0) + 1
        
        # Güç değerlendirmesi
        th_difference = enemy_avg_th - our_avg_th
        
        if th_difference > 0.5:
            strength_status = 'enemy_stronger'
            strength_emoji = '🔴'
            strength_text = 'Rakip daha güçlü'
        elif th_difference < -0.5:
            strength_status = 'we_stronger'
            strength_emoji = '🟢'
            strength_text = 'Bizim avantajımız var'
        else:
            strength_status = 'balanced'
            strength_emoji = '🟡'
            strength_text = 'Dengeli eşleşme'
        
        # En güçlü üyeler karşılaştırması
        our_top3 = sorted(our_members, key=lambda x: x.get('townhallLevel', 0), reverse=True)[:3]
        enemy_top3 = sorted(enemy_members, key=lambda x: x.get('townhallLevel', 0), reverse=True)[:3]
        
        return {
            'status': strength_status,
            'emoji': strength_emoji,
            'description': strength_text,
            'our_avg_th': round(our_avg_th, 1),
            'enemy_avg_th': round(enemy_avg_th, 1),
            'th_difference': round(th_difference, 1),
            'our_th_distribution': our_th_distribution,
            'enemy_th_distribution': enemy_th_distribution,
            'our_top3': [{'name': m.get('name'), 'th': m.get('townhallLevel')} for m in our_top3],
            'enemy_top3': [{'name': m.get('name'), 'th': m.get('townhallLevel')} for m in enemy_top3]
        }

    def analyze_war_members(self, our_clan, enemy_clan):
        """Savaş üye durumu ve atama analizi"""
        our_members = our_clan.get('members', [])
        enemy_members = enemy_clan.get('members', [])
        
        member_analysis = []
        
        for i, member in enumerate(our_members, 1):
            attacks = member.get('attacks', [])
            best_attack = member.get('bestOpponentAttack')
            
            # Karşı üye analizi
            if i <= len(enemy_members):
                opponent = enemy_members[i-1]
                opponent_attacks = opponent.get('attacks', [])
                
                # Saldırı durumu
                attack_status = 'not_attacked'
                total_stars = 0
                total_destruction = 0
                
                if attacks:
                    attack_status = 'attacked'
                    total_stars = sum(attack.get('stars', 0) for attack in attacks)
                    total_destruction = sum(attack.get('destructionPercentage', 0) for attack in attacks)
                
                # Savunma durumu
                defense_status = 'not_defended'
                defended_stars = 0
                defended_destruction = 0
                
                if best_attack:
                    defense_status = 'defended'
                    defended_stars = best_attack.get('stars', 0)
                    defended_destruction = best_attack.get('destructionPercentage', 0)
                
                # Hedef önerisi
                recommended_targets = self.suggest_targets_for_member(member, enemy_members, our_members)
                
                member_analysis.append({
                    'position': i,
                    'name': member.get('name'),
                    'tag': member.get('tag'),
                    'th_level': member.get('townhallLevel'),
                    'attack_status': attack_status,
                    'attacks_made': len(attacks),
                    'total_stars': total_stars,
                    'total_destruction': round(total_destruction, 1),
                    'defense_status': defense_status,
                    'defended_stars': defended_stars,
                    'defended_destruction': round(defended_destruction, 1),
                    'opponent': {
                        'name': opponent.get('name'),
                        'th_level': opponent.get('townhallLevel'),
                        'attacks_made': len(opponent_attacks)
                    },
                    'recommended_targets': recommended_targets,
                    'priority': self.calculate_member_priority(member, attacks, best_attack)
                })
        
        return member_analysis

    def suggest_targets_for_member(self, member, enemy_members, our_members):
        """Üye için hedef önerisi algoritması"""
        member_th = member.get('townhallLevel', 0)
        member_position = None
        
        # Üyenin pozisyonunu bul
        for i, our_member in enumerate(our_members, 1):
            if our_member.get('tag') == member.get('tag'):
                member_position = i
                break
        
        suggestions = []
        
        for i, enemy in enumerate(enemy_members, 1):
            enemy_th = enemy.get('townhallLevel', 0)
            enemy_attacks = enemy.get('attacks', [])
            
            # Hedef analizi
            th_difference = member_th - enemy_th
            
            # Skor hesaplama
            score = 50  # Base score
            
            # TH seviyesi bonus/malus
            if th_difference >= 0:
                score += min(th_difference * 20, 40)  # Aynı veya düşük TH bonus
            else:
                score -= abs(th_difference) * 15  # Yüksek TH cezası
            
            # Pozisyon uygunluğu
            position_diff = abs(member_position - i) if member_position else 0
            if position_diff <= 2:
                score += 20  # Kendi seviyesi civarı bonus
            elif position_diff <= 5:
                score += 10
            
            # Zaten saldırılmış mı kontrolü
            attacked_by_us = False
            for our_member in our_members:
                for attack in our_member.get('attacks', []):
                    if attack.get('defenderTag') == enemy.get('tag'):
                        attacked_by_us = True
                        break
            
            if attacked_by_us:
                score -= 30  # Zaten saldırılmış ceza
            
            # Düşman saldırı sayısı (savunmasız hedefler tercih)
            if len(enemy_attacks) == 0:
                score += 15  # Henüz saldırmamış bonus
            
            # Öncelik belirleme
            if score >= 80:
                priority = 'high'
                priority_emoji = '🎯'
            elif score >= 60:
                priority = 'medium'
                priority_emoji = '⚡'
            elif score >= 40:
                priority = 'low'
                priority_emoji = '💫'
            else:
                priority = 'avoid'
                priority_emoji = '❌'
            
            suggestions.append({
                'position': i,
                'name': enemy.get('name'),
                'th_level': enemy_th,
                'score': round(score),
                'priority': priority,
                'emoji': priority_emoji,
                'th_difference': th_difference,
                'already_attacked': attacked_by_us,
                'reason': self.get_target_reason(th_difference, position_diff, attacked_by_us, score)
            })
        
        # En iyi 3 hedefi döndür
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:3]

    def get_target_reason(self, th_diff, pos_diff, attacked, score):
        """Hedef önerisi sebebi"""
        if attacked:
            return "Zaten saldırılmış"
        elif th_diff >= 1:
            return "Kolay hedef"
        elif th_diff == 0:
            return "Eşit seviye"
        elif th_diff == -1:
            return "Zorlayıcı ama yapılabilir"
        elif pos_diff <= 2:
            return "Pozisyon uygun"
        elif score >= 70:
            return "Güvenli seçim"
        else:
            return "Risk'li hedef"

    def calculate_member_priority(self, member, attacks, best_defense):
        """Üye öncelik hesaplama"""
        priority_score = 0
        
        # Saldırı durumu
        if len(attacks) == 0:
            priority_score += 50  # Henüz saldırmamış - yüksek öncelik
        elif len(attacks) == 1:
            attack = attacks[0]
            if attack.get('stars', 0) < 2:
                priority_score += 30  # Kötü ilk saldırı - tekrar denemeli
            else:
                priority_score += 10  # İyi saldırı - ikinci saldırı için orta öncelik
        
        # TH seviyesi
        th_level = member.get('townhallLevel', 0)
        if th_level >= 12:
            priority_score += 20  # Yüksek TH - stratejik önemli
        
        # Savunma durumu
        if best_defense:
            defended_stars = best_defense.get('stars', 0)
            if defended_stars >= 2:
                priority_score -= 20  # İyi savunmuş - düşük öncelik
        
        return 'high' if priority_score >= 60 else 'medium' if priority_score >= 30 else 'low'

    def generate_war_strategy(self, war_analysis):
        """Savaş stratejisi önerisi"""
        matchup = war_analysis['matchup_analysis']
        our_clan = war_analysis['our_clan']
        enemy_clan = war_analysis['enemy_clan']
        
        strategy = {
            'main_approach': '',
            'priority_actions': [],
            'warnings': [],
            'timeline': []
        }
        
        # Ana strateji belirleme
        if matchup['status'] == 'enemy_stronger':
            strategy['main_approach'] = 'defensive'
            strategy['priority_actions'] = [
                '🛡️ Savunmaya odaklan - güvenli hedefleri seç',
                '⭐ 2 yıldız stratejisi uygula',
                '🎯 Alt sıralarda güvenli puanları topla',
                '⚡ En güçlü üyeler üst sıraları temizlesin'
            ]
        elif matchup['status'] == 'we_stronger':
            strategy['main_approach'] = 'aggressive'
            strategy['priority_actions'] = [
                '🚀 Saldırgan git - 3 yıldız hedefle',
                '👑 Üst sıralar maksimum yıldız alsın',
                '🔥 Hızlı temizlik stratejisi',
                '💯 %100 hakim olma hedefi'
            ]
        else:
            strategy['main_approach'] = 'balanced'
            strategy['priority_actions'] = [
                '⚖️ Dengeli strateji - güvenli puanlar önce',
                '🎯 Kendi seviyende saldır',
                '⭐ 2 yıldız garantile, 3 yıldız dene',
                '🔄 Esnek takım çalışması'
            ]
        
        # Uyarılar
        remaining_attacks = our_clan['attacks_remaining']
        if remaining_attacks <= 5:
            strategy['warnings'].append('⚠️ Az saldırı hakkı kaldı - dikkatli ol!')
        
        if our_clan['stars'] < enemy_clan['stars']:
            strategy['warnings'].append('🔴 Gerideyiz - agresif strateji gerekli!')
        
        # Zaman çizelgesi
        war_state = war_analysis['war_state']
        if war_state == 'preparation':
            strategy['timeline'] = [
                '📋 Strateji toplantısı yap',
                '🎯 Hedef atamaları belirle',
                '💪 Ordu hazırlığı kontrol et',
                '⏰ Savaş başlangıcında hazır ol'
            ]
        elif war_state == 'inWar':
            strategy['timeline'] = [
                '🚀 İlk saldırıları başlat',
                '📊 İlk sonuçları değerlendir',
                '🔄 Gerekirse strateji güncelle',
                '⚡ Cleanup saldırıları organize et'
            ]
        
        return strategy

    def monitor_war_status(self):
        """Savaş durumunu izle ve otomatik bildirimler gönder"""
        try:
            war_data = self.get_clan_war_data()
            
            if not war_data:
                return
            
            war_state = war_data.get('state')
            current_time = datetime.now()
            
            # Savaş başlangıcı bildirimi
            if war_state == 'inWar':
                start_time_str = war_data.get('startTime', '')
                if start_time_str:
                    try:
                        start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                        if (current_time - start_time).total_seconds() < 3600:  # İlk 1 saat
                            print(f"🚨 Savaş başladı: {war_data.get('opponent', {}).get('name', 'Bilinmiyor')}")
                    except:
                        pass
            
            # Savaş sonu bildirimi
            elif war_state == 'warEnded':
                # Otomatik performans raporu oluştur ve kaydet
                timestamp = datetime.now().isoformat()
                if 'war_reports' not in self.clan_history:
                    self.clan_history['war_reports'] = {}
                
                self.clan_history['war_reports'][timestamp] = {
                    'end_time': timestamp,
                    'opponent': war_data.get('opponent', {}).get('name', 'Bilinmiyor'),
                    'our_stars': war_data.get('clan', {}).get('stars', 0),
                    'enemy_stars': war_data.get('opponent', {}).get('stars', 0)
                }
                self.save_data()
                
        except Exception as e:
            print(f"⚠️ Savaş izleme hatası: {e}")
    def handle_savas_command(self, message):
        """SAVAS komutu - Güncel savaş durumu"""
        chat_id = message['chat']['id']
        
        war_analysis = self.get_war_analysis()
        
        if not war_analysis:
            text = "🏰 **Şu anda savaşta değiliz**\n\n⏳ Savaş arama veya hazırlık aşamasında olabilirsiniz."
            self.send_message(chat_id, text)
            return
        
        war_state = war_analysis['war_state']
        our_clan = war_analysis['our_clan']
        enemy_clan = war_analysis['enemy_clan']
        matchup = war_analysis['matchup_analysis']
        
        if war_state == 'preparation':
            status_emoji = '⏳'
            status_text = 'Hazırlık Aşaması'
        elif war_state == 'inWar':
            status_emoji = '⚔️'
            status_text = 'Savaş Devam Ediyor'
        else:
            status_emoji = '✅'
            status_text = 'Savaş Bitti'
        
        text = f"""⚔️ **SAVAS DURUMU**

{status_emoji} **{status_text}**
🆚 **{our_clan['name']}** vs **{enemy_clan['name']}**

🏰 **Klan Karşılaştırması:**
- Bizim takım: Seviye {our_clan['level']} | {war_analysis['team_size']} kişi
- Rakip takım: Seviye {enemy_clan['level']} | {war_analysis['team_size']} kişi

{matchup['emoji']} **Güç Analizi: {matchup['description']}**
- Bizim ortalama TH: {matchup['our_avg_th']}
- Rakip ortalama TH: {matchup['enemy_avg_th']}
- Fark: {matchup['th_difference']:+.1f}

⭐ **Skor Durumu:**
- Bizim yıldız: {our_clan['stars']}
- Rakip yıldız: {enemy_clan['stars']}
- Bizim hasar: %{our_clan['destruction']}
- Rakip hasar: %{enemy_clan['destruction']}

🎯 **Saldırı Durumu:**
- Kullanılan: {our_clan['attacks_used']}
- Kalan: {our_clan['attacks_remaining']}

**Detaylı analiz:** HEDEFIM komutunu kullanın"""
        
        self.send_message(chat_id, text)

    def handle_hedefim_command(self, message):
        """HEDEFIM komutu - Kişisel hedef önerileri"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        war_analysis = self.get_war_analysis()
        
        if not war_analysis:
            text = "❌ Şu anda savaşta değiliz."
            self.send_message(chat_id, text)
            return
        
        user_data = self.users.get(user_id, {})
        user_coc_tag = user_data.get('coc_tag')
        
        if not user_coc_tag:
            text = "❌ COC tag'iniz kayıtlı değil. **COC** yazarak kayıt olun."
            self.send_message(chat_id, text)
            return
        
        user_war_status = None
        for member in war_analysis['member_status']:
            if member['tag'] == user_coc_tag:
                user_war_status = member
                break
        
        if not user_war_status:
            text = "❌ Bu savaşta yer almıyorsunuz."
            self.send_message(chat_id, text)
            return
        
        remaining_attacks = 2 - user_war_status['attacks_made']
        
        text = f"""🎯 **KİŞİSEL HEDEF ÖNERİLERİ**

👤 **{user_war_status['name']}** (#{user_war_status['position']})
🏰 **TH{user_war_status['th_level']}** | Kalan saldırı: **{remaining_attacks}**

📊 **Mevcut Performansın:**
⚔️ Saldırı: {user_war_status['attacks_made']}/2
⭐ Toplam yıldız: {user_war_status['total_stars']}
💥 Toplam hasar: %{user_war_status['total_destruction']}
🛡️ Savunma: {user_war_status['defended_stars']} yıldız verildi

🎯 **ÖNERİLEN HEDEFLER:**"""
        
        for i, target in enumerate(user_war_status['recommended_targets'], 1):
            text += f"\n\n**{i}. {target['emoji']} HEDEF:**"
            text += f"\n• #{target['position']} {target['name']} (TH{target['th_level']})"
            text += f"\n• TH Farkı: {target['th_difference']:+d}"
            text += f"\n• Önem: {target['priority'].title()}"
            text += f"\n• Sebep: {target['reason']}"
            if target['already_attacked']:
                text += f"\n• ⚠️ Zaten saldırılmış"
        
        if remaining_attacks > 0:
            priority_target = user_war_status['recommended_targets'][0] if user_war_status['recommended_targets'] else None
            
            text += f"\n\n💡 **STRATEJİ ÖNERİSİ:**"
            
            if user_war_status['attacks_made'] == 0:
                text += f"\n🥇 **İLK SALDIRI:** Güvenli hedefle başla"
                if priority_target:
                    text += f"\n   → #{priority_target['position']} {priority_target['name']} ideal"
            elif user_war_status['attacks_made'] == 1:
                if user_war_status['total_stars'] >= 2:
                    text += f"\n🥈 **İKİNCİ SALDIRI:** Risk alabilirsin"
                    text += f"\n   → Daha yüksek hedef dene"
                else:
                    text += f"\n🔄 **İKİNCİ SALDIRI:** Güvenli git"
                    text += f"\n   → Yıldız garantile"
            
            text += f"\n\n⏰ **Mevcut Öncelik:** {user_war_status['priority'].title()}"
        else:
            text += f"\n\n✅ **Tüm saldırılarını tamamladın!**"
            if user_war_status['total_stars'] >= 4:
                text += f"\n🏆 Mükemmel performans!"
            elif user_war_status['total_stars'] >= 3:
                text += f"\n👍 İyi iş çıkardın!"
            else:
                text += f"\n💪 Bir sonrakinde daha iyi olacak!"
        
        self.send_message(chat_id, text)

    def handle_savastakla_command(self, message):
        """SAVASTAKLA komutu - Savaş stratejisi ve takım analizi"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
            self.send_message(chat_id, text)
            return
        
        war_analysis = self.get_war_analysis()
        
        if not war_analysis:
            text = "❌ Şu anda savaşta değiliz."
            self.send_message(chat_id, text)
            return
        
        strategy = war_analysis['recommended_strategy']
        member_status = war_analysis['member_status']
        
        not_attacked = [m for m in member_status if m['attacks_made'] == 0]
        partial_attacks = [m for m in member_status if m['attacks_made'] == 1]
        
        text = f"""🎯 **SAVAS STRATEJİSİ VE TAKTİK**

🛡️ **Ana Yaklaşım:** {strategy['main_approach'].title()}

📋 **Öncelikli Aksiyonlar:**"""
        
        for action in strategy['priority_actions']:
            text += f"\n• {action}"
        
        if strategy['warnings']:
            text += f"\n\n⚠️ **Uyarılar:**"
            for warning in strategy['warnings']:
                text += f"\n• {warning}"
        
        text += f"\n\n🎯 **SALDIRI DURUMU:**"
        text += f"\n• Hiç saldırmadı: {len(not_attacked)} üye"
        text += f"\n• 1 saldırı yaptı: {len(partial_attacks)} üye"
        
        if not_attacked:
            text += f"\n\n❌ **SALDIRI YAPMAYAN ÜYELER:**"
            for member in not_attacked[:5]:
                text += f"\n• {member['name']} (#{member['position']}) - TH{member['th_level']}"
        
        high_priority = [m for m in member_status if m['priority'] == 'high' and m['attacks_made'] < 2]
        if high_priority:
            text += f"\n\n🔥 **ÖNCELİKLİ SALDIRMASI GEREKENLER:**"
            for member in high_priority[:5]:
                remaining = 2 - member['attacks_made']
                text += f"\n• {member['name']} (#{member['position']}) - {remaining} saldırı kaldı"
        
        self.send_message(chat_id, text)

       
        # AWS Lambda'da otomatik monitoring'i başlatma (event-driven)
        if not RUNNING_ON_AWS:
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
            except Exception as e:
                print(f"⚠️ Veri yükleme hatası: {e}")
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
            'last_save': datetime.now().isoformat(),
            'bot_info': {
                'ip': self.current_ip,
                'token_ip': self.token_ip,
                'aws_mode': RUNNING_ON_AWS,
                'version': '2.1'
            }
        
        try:
            # AWS'de /tmp dizini kullan
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
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
            elif response.status_code == 403:
                print(f"❌ COC API Yetki Hatası: IP uyumsuzluğu ({self.current_ip} ≠ {self.token_ip})")
                # IP değişikliğini sadece gerçekten değişmişse bildir
                if self.current_ip != self.token_ip:
                    self.notify_ip_change()
                return None
            else:
                print(f"❌ COC API Hatası: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ COC API Bağlantı hatası: {e}")
            return None
    
    def notify_ip_change(self):
        """IP değişikliğini adminlere bildir"""
        if not hasattr(self, '_ip_notified'):
            for admin_id in ADMIN_USERS:
                try:
                    text = f"""🚨 **IP UYUMSUZLUĞU TESPİT EDİLDİ!**
                    
🌐 **Mevcut IP:** {self.current_ip}
🔑 **Token IP'si:** {self.token_ip}

🛠️ **ÇÖZÜM:**
1. developer.clashofclans.com'a gidin
2. Yeni API key oluşturun  
3. IP olarak `{self.current_ip}` girin
4. Yeni token'ı environment variable olarak güncelleyin

⚡ **Lightsail'de:**
```bash
export COC_API_TOKEN="yeni_token_buraya"
```

💡 **Not:** Bu uyumsuzluk AWS IP değişikliğinden kaynaklanabilir."""
                    
                    self.send_message(admin_id, text)
                except:
                    pass
            self._ip_notified = True
    
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
            return None
        
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
        """Otomatik klan izleme başlat (sadece EC2/local için)"""
        def monitor_loop():
            while True:
                try:
                    print("🔄 Otomatik klan kontrolü...")
                    self.analyze_clan()
                    self.monitor_war_status()
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
        
        aws_info = f"\n🌐 **Deploy:** {'☁️ AWS' if RUNNING_ON_AWS else '🖥️ Local'}" if user_id in ADMIN_USERS else ""
        ip_status = f"\n🔍 **IP Status:** {'✅ Eşleşiyor' if self.current_ip == self.token_ip else '⚠️ Uyumsuz'}" if user_id in ADMIN_USERS else ""
        
        text = f"""🏰 **Kemal'in Değneği - Otomatik Klan Yöneticisi**

Hoş geldin {first_name}! ⚔️

🤖 **Otomatik Özellikler:**
• 🔄 Saatlik klan analizi
• 👑 Otomatik rütbe önerileri  
• ⚠️ Pasif üye tespiti
• 📊 Gerçek zamanlı istatistikler{aws_info}{ip_status}

{clan_summary}

🎯 **Komutlar:**
• **KLAN** - Canlı klan durumu
• **ANALIZ** - Son analiz raporu
• **RUTBE** - Rütbe önerileri
• **PASIF** - Pasif üyeler
• **STATS** - Kişisel istatistik
• **IPCHECK** - IP kontrol (admin)"""
"""🎯 **Savaş Komutları:**
- **SAVAS** - Güncel savaş durumu ve analiz
- **HEDEFIM** - Kişisel hedef önerileri  
- **SAVASTAKLA** - Detaylı strateji (Admin)
        
        self.send_message(chat_id, text)
        self.save_data()
    
  def get_clan_summary(self):
    """Klan özeti hazırla"""
    analysis = self.get_latest_clan_analysis()
    
    if not analysis:
        return "**Klan Durumu:** İlk analiz yapılıyor..."
    
    clan_info = analysis['clan_info']
    inactive_count = len(analysis['inactive_members'])
    top_count = len(analysis['top_performers'])
    role_changes = len(analysis['role_recommendations'])
    
    last_update = datetime.fromisoformat(analysis['timestamp'])
    time_ago = datetime.now() - last_update
    hours_ago = int(time_ago.total_seconds() / 3600)
    
    summary_text = **Klan Durumu:**
🏰 {clan_info['name']} (Seviye {clan_info['level']})
👥 Üye: {clan_info['members']}/50
🏆 Klan Puanı: {clan_info['total_points']:,}
⚔️ Savaş: {clan_info['war_wins']}W-{clan_info['war_losses']}L

🎯 **Analiz Sonuçları:**
👑 En iyi performans: {top_count} üye
⚠️ Pasif üye: {inactive_count} üye  
🔄 Rütbe önerisi: {role_changes} üye

🕐 Son analiz: {hours_ago} saat önce"""
    
    return summary_text
    
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
    
    def handle_ipcheck_command(self, message):
        """IP kontrol komutu"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
            self.send_message(chat_id, text)
            return
        
        try:
            # Şu anki IP'yi al
            current_ip = get_current_ip() or "Bulunamadı"
            
            # Token'dan kayıtlı IP'yi çıkar  
            registered_ip = self.token_ip
            
            text = f"""🌐 **IP Durum Kontrolü**

📍 **Şu anki IP:** `{current_ip}`
🔑 **Token'da kayıtlı:** `{registered_ip}`

"""
            
            if current_ip == registered_ip:
                text += """✅ **IP EŞLEŞİYOR!**
🎯 API çalışması normal

🧪 Test için: **KLAN** komutunu deneyin"""
            else:
                text += f"""❌ **IP UYUMSUZLUĞU!**
🔄 Mevcut IP: {current_ip}
🔒 Token IP: {registered_ip}

🛠️ **ÇÖZÜM ADIMLAR:**

**1️⃣ Yeni Token Oluşturun:**
• developer.clashofclans.com'a gidin
• Create New Key tıklayın
• IP: `{current_ip}` yazın
• Yeni token'ı kopyalayın

**2️⃣ Lightsail'de Token Güncelleyin:**
```bash
nano clash_bot.py
# 11. satırda COC_API_TOKEN'ı güncelleyin
# Ctrl+X, Y, Enter ile kaydedin
```

**3️⃣ Bot'u Yeniden Başlatın:**
```bash
python3 clash_bot.py
```

💡 **Not:** Bu uyumsuzluk AWS IP değişikliğinden kaynaklanıyor."""
            
        except Exception as e:
            text = f"❌ **IP kontrol hatası:** {str(e)}"
        
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
        elif text == 'STATS':
            self.handle_stats_command(message)
        elif text == 'IPCHECK':
            self.handle_ipcheck_command(message)
        elif text == 'SAVAS':
            self.handle_savas_command(message)
        elif text == 'HEDEFIM':
            self.handle_hedefim_command(message)
        elif text == 'SAVASTAKLA':
            self.handle_savastakla_command(message)
        elif text == 'COC':
            self.send_message(chat_id, "🏰 **COC Tag'inizi yazın:**\n📋 Örnek: #ABC123XYZ")
        elif text.startswith('#') and len(text) >= 4:
            # COC tag kaydet
            if user_id in self.users:
                self.users[user_id]['coc_tag'] = text
                self.send_message(chat_id, f"✅ **COC tag kaydedildi!**\n🏷️ **Tag:** `{text}`")
                self.save_data()
        else:
            # Küfür kontrolü
            self.check_profanity(message)
    
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
        print(f"🔧 AWS Mode: {'✓' if RUNNING_ON_AWS else '✗'}")
        print(f"🌐 Current IP: {self.current_ip}")
        print(f"🔑 Token IP: {self.token_ip}")
        
        if self.current_ip != self.token_ip:
            print(f"⚠️ IP UYUMSUZLUĞU: {self.current_ip} ≠ {self.token_ip}")
        else:
            print("✅ IP Durumu: Eşleşiyor")
        
        if not RUNNING_ON_AWS:
            print("🔄 Otomatik saatlik klan analizi çalışıyor")
        else:
            print("☁️ AWS Lambda - Event-driven mode")
            
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

# AWS Lambda handler fonksiyonu
def lambda_handler(event, context):
    """AWS Lambda için handler"""
    try:
        bot = AutoClanManager()
        
        # Webhook'tan gelen mesajı işle
        if 'body' in event:
            import json
            update = json.loads(event['body'])
            
            if 'message' in update and 'text' in update['message']:
                bot.handle_text_message(update['message'])
        
        # CloudWatch Events ile tetiklenen otomatik analiz
        elif event.get('source') == 'aws.events':
            print("🔄 Zamanlanmış analiz tetiklendi")
            analysis = bot.analyze_clan()
            
            # Admins'e özet gönder
            if analysis:
                summary = f"""🤖 **Otomatik Analiz Raporu**
                
🏰 {analysis['clan_info']['name']}
👑 En iyi: {len(analysis['top_performers'])}
⚠️ Pasif: {len(analysis['inactive_members'])}
🔄 Rütbe: {len(analysis['role_recommendations'])}

🕐 {datetime.now().strftime('%H:%M')}"""
                
                for admin_id in ADMIN_USERS:
                    bot.send_message(admin_id, summary)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'success'})
        }
        
    except Exception as e:
        print(f"❌ Lambda error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

if __name__ == '__main__':
    if RUNNING_ON_AWS:
        print("☁️ AWS Lambda modunda çalışıyor")
    else:
        bot = AutoClanManager()
        bot.run()
