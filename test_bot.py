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
BOT_TOKEN = "7708393145:AAFHHNBUNNMhx8mTCZ4iWy83ZdgiNB-SoNc"
ADMIN_USERS = ["8114999904"]
COC_API_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImJkYzliMTQ1LTZkY2QtNDU0Mi1hNmNmLTgwMzViNDJiZWFjNyIsImlhdCI6MTc1MjAyNzAxMiwic3ViIjoiZGV2ZWxvcGVyLzRiYTU2MTc5LWE5NDgtMTBkYy0yNmI1LThkZjc5NjcyYjRmNCIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjEzLjYxLjU2LjE5NyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.xkmTiuBnozS8NSK8F1D8ST939QxlKj5qZ7EkRI45ZhDqCS406RFr0Jzh4hTJkEB3oWgNBDZh7aVs0xFqxBRWvw"
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

    def reset_data(self):
        """Veri sıfırlama"""
        self.users = {}
        self.daily_stats = {}
        self.warnings_data = {}
        self.clan_history = {}
        print("🔄 Yeni veri yapısı oluşturuldu")
    
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
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        self.offset = 0
        self.data_file = "clan_data.json"
        self.load_data()
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.last_clan_check = None
        print(f"✅ Bot başlatıldı - Tarih: {self.today}")
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

    def run(self):
        """Botu çalıştır"""
        print("🏰 Kemal'in Değneği - Tam Otomatik Klan Yöneticisi")
        print("🤖 Clash of Clans API entegrasyonu aktif")
        print("🔄 Otomatik saatlik klan analizi çalışıyor")
        print("📱 Telegram komutu: /start")
        print("🛑 Durdurmak için Ctrl+C")
        print("-" * 60)

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

     def save_data(self):
        """Verileri dosyaya kaydet"""
        data = {
            'users': self.users,
            'daily_stats': self.daily_stats,
            'warnings_data': self.warnings_data,
            'clan_history': self.clan_history,
            'last_save': datetime.now().isoformat()

        # Akıllı Savaş Planlama Özellikleri
# Ana AutoClanManager sınıfına eklenecek methodlar

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
        position_diff = abs(member_position - i)
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

def generate_war_performance_report(self, war_data):
    """Savaş sonrası detaylı performans raporu"""
    if not war_data or war_data.get('state') != 'warEnded':
        return None
    
    our_clan = war_data.get('clan', {})
    enemy_clan = war_data.get('opponent', {})
    our_members = our_clan.get('members', [])
    
    # Genel sonuç
    our_stars = our_clan.get('stars', 0)
    enemy_stars = enemy_clan.get('stars', 0)
    our_destruction = our_clan.get('destructionPercentage', 0)
    enemy_destruction = enemy_clan.get('destructionPercentage', 0)
    
    result = 'victory' if our_stars > enemy_stars else 'defeat' if our_stars < enemy_stars else 'draw'
    
    # Üye performans analizi
    member_performances = []
    total_possible_stars = len(our_members) * 2
    
    for member in our_members:
        attacks = member.get('attacks', [])
        best_defense = member.get('bestOpponentAttack')
        
        # Saldırı performansı
        attack_stars = sum(attack.get('stars', 0) for attack in attacks)
        attack_destruction = sum(attack.get('destructionPercentage', 0) for attack in attacks)
        attacks_made = len(attacks)
        
        # Performans skoru hesaplama
        performance_score = 0
        
        # Saldırı skoru (0-60 puan)
        if attacks_made == 2:
            performance_score += 20  # Her iki saldırı kullanıldı
            if attack_stars >= 4:
                performance_score += 40  # Mükemmel saldırı
            elif attack_stars >= 3:
                performance_score += 30  # İyi saldırı
            elif attack_stars >= 2:
                performance_score += 20  # Orta saldırı
            else:
                performance_score += 10  # Zayıf saldırı
        elif attacks_made == 1:
            performance_score += 10
            if attack_stars >= 2:
                performance_score += 20
            else:
                performance_score += 10
        
        # Savunma skoru (0-20 puan)
        if best_defense:
            defended_stars = best_defense.get('stars', 0)
            if defended_stars == 0:
                performance_score += 20  # Mükemmel savunma
            elif defended_stars == 1:
                performance_score += 15  # İyi savunma
            elif defended_stars == 2:
                performance_score += 10  # Orta savunma
            else:
                performance_score += 5   # Zayıf savunma
        else:
            performance_score += 20  # Saldırılmamış
        
        # Yıldız verimliliği (0-20 puan)
        if attacks_made > 0:
            star_efficiency = attack_stars / attacks_made
            if star_efficiency >= 2.0:
                performance_score += 20
            elif star_efficiency >= 1.5:
                performance_score += 15
            elif star_efficiency >= 1.0:
                performance_score += 10
            else:
                performance_score += 5
        
        # Performans değerlendirmesi
        if performance_score >= 80:
            performance_grade = 'A+'
            performance_emoji = '🏆'
            performance_text = 'Mükemmel'
        elif performance_score >= 70:
            performance_grade = 'A'
            performance_emoji = '🥇'
            performance_text = 'Çok İyi'
        elif performance_score >= 60:
            performance_grade = 'B'
            performance_emoji = '🥈'
            performance_text = 'İyi'
        elif performance_score >= 50:
            performance_grade = 'C'
            performance_emoji = '🥉'
            performance_text = 'Orta'
        elif performance_score >= 40:
            performance_grade = 'D'
            performance_emoji = '⚠️'
            performance_text = 'Zayıf'
        else:
            performance_grade = 'F'
            performance_emoji = '❌'
            performance_text = 'Çok Zayıf'
        
        member_performances.append({
            'name': member.get('name'),
            'position': member.get('mapPosition'),
            'th_level': member.get('townhallLevel'),
            'attacks_made': attacks_made,
            'attack_stars': attack_stars,
            'attack_destruction': round(attack_destruction, 1),
            'defended_stars': best_defense.get('stars', 0) if best_defense else 0,
            'defended_destruction': best_defense.get('destructionPercentage', 0) if best_defense else 0,
            'performance_score': performance_score,
            'performance_grade': performance_grade,
            'performance_emoji': performance_emoji,
            'performance_text': performance_text
        })
    
    # En iyi ve en kötü performanslar
    sorted_performances = sorted(member_performances, key=lambda x: x['performance_score'], reverse=True)
    top_performers = sorted_performances[:3]
    worst_performers = sorted_performances[-3:] if len(sorted_performances) >= 3 else []
    
    # Takım istatistikleri
    total_attacks_made = sum(p['attacks_made'] for p in member_performances)
    total_stars_earned = sum(p['attack_stars'] for p in member_performances)
    average_score = sum(p['performance_score'] for p in member_performances) / len(member_performances)
    
    # Missed attacks (kaçırılan saldırılar)
    missed_attacks = total_possible_stars - total_attacks_made
    
    return {
        'result': result,
        'our_stars': our_stars,
        'enemy_stars': enemy_stars,
        'our_destruction': our_destruction,
        'enemy_destruction': enemy_destruction,
        'total_attacks_made': total_attacks_made,
        'total_possible_attacks': total_possible_stars,
        'missed_attacks': missed_attacks,
        'total_stars_earned': total_stars_earned,
        'average_performance': round(average_score, 1),
        'member_performances': member_performances,
        'top_performers': top_performers,
        'worst_performers': worst_performers,
        'team_grade': self.calculate_team_grade(average_score, missed_attacks, result)
    }

def calculate_team_grade(self, avg_score, missed_attacks, result):
    """Takım notu hesaplama"""
    team_score = avg_score
    
    # Sonuç bonusu/cezası
    if result == 'victory':
        team_score += 10
    elif result == 'defeat':
        team_score -= 10
    
    # Kaçırılan saldırı cezası
    team_score -= missed_attacks * 5
    
    if team_score >= 85:
        return 'A+', '🏆', 'Mükemmel Takım Performansı'
    elif team_score >= 75:
        return 'A', '🥇', 'Harika Takım Çalışması'
    elif team_score >= 65:
        return 'B', '🥈', 'İyi Koordinasyon'
    elif team_score >= 55:
        return 'C', '🥉', 'Orta Seviye Performans'
    elif team_score >= 45:
        return 'D', '⚠️', 'Gelişim Gerekli'
    else:
        return 'F', '❌', 'Ciddi Sorunlar Var'

# Telegram komut handler'ları

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
• Bizim takım: Seviye {our_clan['level']} | {war_analysis['team_size']} kişi
• Rakip takım: Seviye {enemy_clan['level']} | {war_analysis['team_size']} kişi

{matchup['emoji']} **Güç Analizi: {matchup['description']}**
• Bizim ortalama TH: {matchup['our_avg_th']}
• Rakip ortalama TH: {matchup['enemy_avg_th']}
• Fark: {matchup['th_difference']:+.1f}

⭐ **Skor Durumu:**
• Bizim yıldız: {our_clan['stars']}
• Rakip yıldız: {enemy_clan['stars']}
• Bizim hasar: %{our_clan['destruction']}
• Rakip hasar: %{enemy_clan['destruction']}

🎯 **Saldırı Durumu:**
• Kullanılan: {our_clan['attacks_used']}
• Kalan: {our_clan['attacks_remaining']}

**Detaylı analiz:** SAVASTAKLA komutunu kullanın"""
    
    self.send_message(chat_id, text)

def handle_savastakla_command(self, message):
    """SAVASTAKLA komutu - Savaş stratejisi ve hedef önerileri"""
    chat_id = message['chat']['id']
    user_id = str(message['from']['id'])
    
    war_analysis = self.get_war_analysis()
    
    if not war_analysis:
        text = "❌ Şu anda savaşta değiliz."
        self.send_message(chat_id, text)
        return
    
    strategy = war_analysis['recommended_strategy']
    member_status = war_analysis['member_status']
    
    # Kullanıcının kendi durumunu bul
    user_data = self.users.get(user_id, {})
    user_coc_tag = user_data.get('coc_tag')
    user_war_status = None
    
    if user_coc_tag:
        for member in member_status:
            if member['tag'] == user_coc_tag:
                user_war_status = member
                break
    
    text = f"""🎯 **SAVAS STRATEJİSİ**

🛡️ **Ana Yaklaşım:** {strategy['main_approach'].title()}

📋 **Öncelikli Aksiyonlar:**"""
    
    for action in strategy['priority_actions']:
        text += f"\n• {action}"
    
    if strategy['warnings']:
        text += f"\n\n⚠️ **Uyarılar:**"
        for warning in strategy['warnings']:
            text += f"\n• {warning}"
    
    if user_war_status:
        text += f"\n\n👤 **Senin Durumun:**"
        text += f"\n• Pozisyon: #{user_war_status['position']}"
        text += f"\n• Saldırı: {user_war_status['attacks_made']}/2"
        text += f"\n• Toplam yıldız: {user_war_status['total_stars']}"
        
        if user_war_status['recommended_targets']:
            text += f"\n\n🎯 **Önerilen Hedefler:**"
            for target in user_war_status['recommended_targets']:
                text += f"\n{target['emoji']} #{target['position']} {target['name']} (TH{target['th_level']}) - {target['reason']}"
    
    text += f"\n\n**Tam rapor:** SAVASRAPOR"
    
    self.send_message(chat_id, text)

def handle_savasrapor_command(self, message):
    """SAVASRAPOR komutu - Detaylı savaş raporu"""
    chat_id = message['chat']['id']
    user_id = str(message['from']['id'])
    
    if user_id not in ADMIN_USERS:
        text = "❌ Bu komut sadece adminler için!"
        self.send_message(chat_id, text)
        return
    
    war_data = self.get_clan_war_data()
    
    if not war_data:
        text = "❌ Savaş verisi bulunamadı."
        self.send_message(chat_id, text)
        return
    
    if war_data.get('state') == 'warEnded':
        # Savaş bitti - performans raporu
        performance_report = self.generate_war_performance_report(war_data)
        
        if performance_report:
            result_emoji = '🏆' if performance_report['result'] == 'victory' else '💔' if performance_report['result'] == 'defeat' else '🤝'
            result_text = 'GALİBİYET' if performance_report['result'] == 'victory' else 'MAĞLUBİYET' if performance_report['result'] == 'defeat' else 'BERABERE'
            
            team_grade, team_emoji, team_description = performance_report['team_grade']
            
            text = f"""📊 **SAVAS PERFORMANS RAPORU**

{result_emoji} **SONUÇ: {result_text}**
⭐ **{performance_report['our_stars']} - {performance_report['enemy_stars']}** (Yıldız)
💥 **%{performance_report['our_destruction']:.1f} - %{performance_report['enemy_destruction']:.1f}** (Hasar)

{team_emoji} **TAKIM NOTU: {team_grade}**
📈 **{team_description}**
📊 Ortalama performans: {performance_report['average_performance']}/100

🎯 **SALDIRI İSTATİSTİKLERİ:**
• Yapılan saldırı: {performance_report['total_attacks_made']}/{performance_report['total_possible_attacks']}
• Kaçırılan saldırı: {performance_report['missed_attacks']}
• Toplam yıldız: {performance_report['total_stars_earned']}

🏆 **EN İYİ PERFORMANSLAR:**"""
            
            for i, performer in enumerate(performance_report['top_performers'], 1):
                text += f"\n{i}. {performer['performance_emoji']} {performer['name']} - {performer['performance_grade']} ({performer['performance_score']}/100)"
                text += f"\n   ⚔️ {performer['attack_stars']} yıldız ({performer['attacks_made']} saldırı)"
            
            if performance_report['worst_performers']:
                text += f"\n\n⚠️ **GELİŞİM GEREKLİ:**"
                for performer in performance_report['worst_performers']:
                    text += f"\n• {performer['performance_emoji']} {performer['name']} - {performer['performance_grade']} ({performer['performance_score']}/100)"
            
            text += f"\n\n💡 **ÖNERİLER:**"
            if performance_report['missed_attacks'] > 3:
                text += f"\n• {performance_report['missed_attacks']} saldırı kaçırıldı - katılım artırılmalı"
            if performance_report['average_performance'] < 60:
                text += f"\n• Ortalama performans düşük - antrenman gerekli"
            if performance_report['result'] == 'defeat':
                text += f"\n• Mağlubiyet analizi yapılmalı - strateji gözden geçir"
            else:
                text += f"\n• Güzel performans - bu seviyeyi koruyun!"
        
        else:
            text = "❌ Performans raporu oluşturulamadı."
    
    else:
        # Savaş devam ediyor - anlık durum raporu
        war_analysis = self.get_war_analysis()
        member_status = war_analysis['member_status']
        
        # Saldırı yapmayan üyeler
        not_attacked = [m for m in member_status if m['attacks_made'] == 0]
        partial_attacks = [m for m in member_status if m['attacks_made'] == 1]
        completed_attacks = [m for m in member_status if m['attacks_made'] == 2]
        
        # Performans sıralaması
        active_members = [m for m in member_status if m['attacks_made'] > 0]
        active_members.sort(key=lambda x: (x['total_stars'], x['total_destruction']), reverse=True)
        
        text = f"""📊 **CANLI SAVAS RAPORU**

⚔️ **SALDIRI DURUMU:**
• Hiç saldırmadı: {len(not_attacked)} üye
• 1 saldırı yaptı: {len(partial_attacks)} üye  
• 2 saldırı tamamladı: {len(completed_attacks)} üye

🎯 **ÖNCELİKLİ SALDIRMASI GEREKENLER:**"""
        
        # En yüksek öncelikli üyeler
        high_priority = [m for m in member_status if m['priority'] == 'high' and m['attacks_made'] < 2]
        for member in high_priority[:5]:
            remaining = 2 - member['attacks_made']
            text += f"\n🔥 {member['name']} (#{member['position']}) - {remaining} saldırı kaldı"
        
        if not_attacked:
            text += f"\n\n❌ **SALDIRI YAPMAYAN ÜYELER:**"
            for member in not_attacked[:5]:
                text += f"\n• {member['name']} (#{member['position']}) - TH{member['th_level']}"
        
        if active_members:
            text += f"\n\n🏆 **EN İYİ PERFORMANSLAR:**"
            for i, member in enumerate(active_members[:3], 1):
                text += f"\n{i}. {member['name']} - {member['total_stars']} ⭐ (%{member['total_destruction']:.1f})"
        
        text += f"\n\n🎯 **STRATEJİK ÖNERİLER:**"
        our_clan = war_analysis['our_clan']
        enemy_clan = war_analysis['enemy_clan']
        
        if our_clan['stars'] > enemy_clan['stars']:
            text += f"\n✅ Önde gidiyoruz - güvenli oyun"
        elif our_clan['stars'] < enemy_clan['stars']:
            text += f"\n🔴 Geride kaldık - agresif strateji"
        else:
            text += f"\n🟡 Baş başa - dikkatli ilerle"
        
        if our_clan['attacks_remaining'] <= 10:
            text += f"\n⏰ Az saldırı kaldı - hızlı hareket edin"
    
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
    
    # Kullanıcının savaş durumunu bul
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
    
    # Strateji önerisi
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

def handle_savasonucu_command(self, message):
    """SAVASONUCU komutu - Savaş sonucu ve istatistikler"""
    chat_id = message['chat']['id']
    
    war_data = self.get_clan_war_data()
    
    if not war_data:
        text = "❌ Savaş verisi bulunamadı."
        self.send_message(chat_id, text)
        return
    
    if war_data.get('state') != 'warEnded':
        text = "⏳ Savaş henüz bitmedi. SAVAS komutunu kullanın."
        self.send_message(chat_id, text)
        return
    
    performance_report = self.generate_war_performance_report(war_data)
    
    if not performance_report:
        text = "❌ Savaş raporu oluşturulamadı."
        self.send_message(chat_id, text)
        return
    
    # Özet rapor (herkese açık)
    result_emoji = '🏆' if performance_report['result'] == 'victory' else '💔' if performance_report['result'] == 'defeat' else '🤝'
    result_text = 'GALİBİYET! 🎉' if performance_report['result'] == 'victory' else 'Mağlubiyet 😞' if performance_report['result'] == 'defeat' else 'Berabere 🤝'
    
    team_grade, team_emoji, team_description = performance_report['team_grade']
    
    text = f"""🏁 **SAVAS SONUCU**

{result_emoji} **{result_text}**

📊 **SKOR:**
⭐ **{performance_report['our_stars']} - {performance_report['enemy_stars']}**
💥 **%{performance_report['our_destruction']:.1f} - %{performance_report['enemy_destruction']:.1f}**

{team_emoji} **TAKIM PERFORMANSI: {team_grade}**
📈 {team_description}

🎯 **İSTATİSTİKLER:**
• Saldırı kullanımı: {performance_report['total_attacks_made']}/{performance_report['total_possible_attacks']}
• Kaçırılan saldırı: {performance_report['missed_attacks']}
• Ortalama performans: {performance_report['average_performance']}/100

🏆 **GÜNÜN YILDIZLARI:**"""
    
    for i, performer in enumerate(performance_report['top_performers'], 1):
        text += f"\n{i}. {performer['performance_emoji']} **{performer['name']}** - {performer['performance_grade']}"
        text += f"\n   ⚔️ {performer['attack_stars']} yıldız | 🛡️ {performer['defended_stars']} yıldız verildi"
    
    # Genel değerlendirme
    text += f"\n\n💭 **DEĞERLENDİRME:**"
    
    if performance_report['result'] == 'victory':
        if team_grade in ['A+', 'A']:
            text += f"\n🌟 Harika bir galibiyet! Takım çok uyumlu."
        else:
            text += f"\n✅ Galip geldik ama daha iyisini yapabiliriz."
    elif performance_report['result'] == 'defeat':
        if performance_report['missed_attacks'] > 3:
            text += f"\n💔 Kaçırılan {performance_report['missed_attacks']} saldırı mağlubiyetin sebebi."
        else:
            text += f"\n💪 İyi savaştık ama rakip daha güçlüydü."
    
    if performance_report['average_performance'] >= 70:
        text += f"\n👏 Takım ortalaması çok iyi!"
    elif performance_report['average_performance'] < 50:
        text += f"\n📚 Antrenman ve koordinasyon gerekli."
    
    text += f"\n\n**Detaylı rapor için adminlere danışın**"
    
    self.send_message(chat_id, text)

def handle_savasgecmis_command(self, message):
    """SAVASGECMIS komutu - Savaş geçmişi analizi"""
    chat_id = message['chat']['id']
    user_id = str(message['from']['id'])
    
    if user_id not in ADMIN_USERS:
        text = "❌ Bu komut sadece adminler için!"
        self.send_message(chat_id, text)
        return
    
    # Son 5 savaş analizini getir
    war_history = []
    
    # Clan data'dan savaş istatistiklerini al
    clan_data = self.get_clan_data()
    
    if clan_data:
        total_wars = clan_data.get('warWins', 0) + clan_data.get('warLosses', 0)
        win_rate = (clan_data.get('warWins', 0) / total_wars * 100) if total_wars > 0 else 0
        
        text = f"""📜 **SAVAS GEÇMİŞİ ANALİZİ**

🏆 **GENEL İSTATİSTİKLER:**
• Toplam savaş: {total_wars}
• Galibiyet: {clan_data.get('warWins', 0)}
• Mağlubiyet: {clan_data.get('warLosses', 0)}
• Galibiyet oranı: %{win_rate:.1f}

📊 **TREND ANALİZİ:**"""
        
        if win_rate >= 80:
            text += f"\n🌟 Mükemmel savaş performansı!"
            text += f"\n💪 Klan çok güçlü ve organize"
        elif win_rate >= 60:
            text += f"\n👍 İyi savaş performansı"
            text += f"\n🎯 Bazı iyileştirmeler yapılabilir"
        elif win_rate >= 40:
            text += f"\n⚠️ Orta seviye performans"
            text += f"\n📚 Strateji ve koordinasyon geliştirmeli"
        else:
            text += f"\n🔴 Düşük savaş performansı"
            text += f"\n🛠️ Ciddi iyileştirmeler gerekli"
        
        # Son analizlerden trend çıkarma
        recent_analyses = list(self.clan_history.values())[-5:]
        
        if recent_analyses:
            avg_inactive = sum(len(a.get('inactive_members', [])) for a in recent_analyses) / len(recent_analyses)
            avg_top_performers = sum(len(a.get('top_performers', [])) for a in recent_analyses) / len(recent_analyses)
            
            text += f"\n\n📈 **SON DÖNEM TRENDLERİ:**"
            text += f"\n• Ortalama pasif üye: {avg_inactive:.1f}"
            text += f"\n• Ortalama en iyi performans: {avg_top_performers:.1f}"
            
            text += f"\n\n💡 **ÖNERİLER:**"
            
            if win_rate < 60:
                text += f"\n🎯 Savaş stratejilerini gözden geçirin"
                text += f"\n👥 Üye eğitimi düzenleyin"
            
            if avg_inactive > 3:
                text += f"\n⚠️ Pasif üye sayısı yüksek"
                text += f"\n🧹 Klan temizliği yapın"
            
            if avg_top_performers < 5:
                text += f"\n⭐ Daha fazla üyeyi motive edin"
                text += f"\n🏆 Başarılı üyeleri ödüllendirin"
        
        text += f"\n\n🔄 **Otomatik takip aktif**"
        text += f"\n📊 Her savaş sonrası detaylı analiz"
    
    else:
        text = "❌ Klan verileri alınamadı."
    
    self.send_message(chat_id, text)

# Ana kod entegrasyonu için gerekli eklentiler

def add_war_commands_to_handler(self, text, message):
    """Savaş komutlarını ana handler'a eklemek için"""
    if text == 'SAVAS':
        self.handle_savas_command(message)
    elif text == 'SAVASTAKLA':
        self.handle_savastakla_command(message)
    elif text == 'SAVASRAPOR':
        self.handle_savasrapor_command(message)
    elif text == 'HEDEFIM':
        self.handle_hedefim_command(message)
    elif text == 'SAVASONUCU':
        self.handle_savasonucu_command(message)
    elif text == 'SAVASGECMIS':
        self.handle_savasgecmis_command(message)

def update_start_command_help_text(self):
    """Start komutundaki yardım metnini güncelle"""
    additional_commands = """
🎯 **Savaş Komutları:**
• **SAVAS** - Güncel savaş durumu
• **SAVASTAKLA** - Strateji ve hedefler
• **HEDEFIM** - Kişisel hedef önerileri
• **SAVASONUCU** - Savaş sonuç raporu
• **SAVASRAPOR** - Detaylı performans (Admin)
• **SAVASGECMIS** - Savaş geçmişi (Admin)"""
    
    return additional_commands

# Otomatik savaş izleme için ek fonksiyonlar

def monitor_war_status(self):
    """Savaş durumunu izle ve otomatik bildirimler gönder"""
    war_data = self.get_clan_war_data()
    
    if not war_data:
        return
    
    war_state = war_data.get('state')
    current_time = datetime.now()
    
    # Savaş başlangıcı bildirimi
    if war_state == 'inWar':
        start_time = datetime.fromisoformat(war_data.get('startTime', '').replace('Z', '+00:00'))
        if (current_time - start_time).total_seconds() < 3600:  # İlk 1 saat
            # Admin grubuna bildirim gönder
            notification = f"""🚨 **SAVAS BAŞLADI!**

⚔️ Rakip: {war_data.get('opponent', {}).get('name', 'Bilinmiyor')}
👥 Takım: {war_data.get('teamSize')} vs {war_data.get('teamSize')}

🎯 Strateji için: SAVASTAKLA
📊 Durum için: SAVAS"""
            
            # Burada admin grubuna bildirim gönderilir
            # self.send_message(ADMIN_CHAT_ID, notification)
    
    # Savaş sonu bildirimi
    elif war_state == 'warEnded':
        # Otomatik performans raporu oluştur ve kaydet
        performance_report = self.generate_war_performance_report(war_data)
        if performance_report:
            # Raporu geçmişe kaydet
            timestamp = datetime.now().isoformat()
            if 'war_reports' not in self.clan_history:
                self.clan_history['war_reports'] = {}
            
            self.clan_history['war_reports'][timestamp] = performance_report
            self.save_data()

def integrate_war_monitoring_to_auto_check(self):
    """Otomatik klan kontrolüne savaş izlemeyi entegre et"""
    
    # Otomatik klan kontrolü başlat (her saat)
    self.start_auto_clan_monitoring()
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
        additional_commands = self.update_start_command_help_text()
text += additional_commands


Hoş geldin {first_name}! ⚔️

🤖 **Otomatik Özellikler:**
• 🔄 Saatlik klan analizi
• 👑 Otomatik rütbe önerileri  
• ⚠️ Pasif üye tespiti
• 📊 Gerçek zamanlı istatistikler

{clan_summary}

🎯 **Savaş Komutları:**
- **SAVAS** - Güncel savaş durumu
- **HEDEFIM** - Kişisel hedef önerileri
- **SAVASONUCU** - Savaş sonuç raporu
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
        elif text == 'SAVAS':
            self.handle_savas_command(message)
        elif text == 'SAVASTAKLA':
            self.handle_savastakla_command(message)
        elif text == 'HEDEFIM':
            self.handle_hedefim_command(message)
        elif text == 'SAVASONUCU':
            self.handle_savasonucu_command(message)
        elif text == 'SAVASRAPOR':
            self.handle_savasrapor_command(message)
        elif text == 'SAVASGECMIS':
            self.handle_savasgecmis_command(message)
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
        elif text == 'IPCHECK':
            self.handle_ip_check_command(message)
        elif text == 'APITEST':
            self.handle_api_test_command(message)
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
    
    def handle_ip_check_command(self, message):
        """IP değişiklik kontrolü"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            text = "❌ Bu komut sadece adminler için!"
            self.send_message(chat_id, text)
            return
        
        try:
            # Şu anki IP'yi al
            current_ip = requests.get('https://httpbin.org/ip', timeout=5).json()['origin']
            
            # Token'dan kayıtlı IP'yi çıkar (JWT decode etmeden basit kontrol)
            token_info = COC_API_TOKEN.split('.')[1] + '=='  # Padding ekle
            import base64
            try:
                decoded = base64.b64decode(token_info)
                token_text = decoded.decode('utf-8')
                
                # IP bilgisini bul
                if '13.61.56.197' in token_text:
                    registered_ip = '13.61.56.197'
                elif '208.77.244.83' in token_text:
                    registered_ip = '208.77.244.83'
                elif '208.77.244.10' in token_text:
                    registered_ip = '208.77.244.10'
                else:
                    registered_ip = 'Bulunamadı'
            except:
                registered_ip = 'Parse edilemedi'
            
            text = f"""🌐 **IP Durum Kontrolü**

📍 **Şu anki IP:** `{current_ip}`
🔑 **API'de kayıtlı:** `{registered_ip}`

"""
            
            if current_ip == registered_ip:
                text += """✅ **IP EŞLEŞİYOR!**
🎯 API çalışması normal

🧪 Test: `APITEST` komutunu deneyin"""
            else:
                text += f"""❌ **IP DEĞİŞMİŞ!**
🔄 Yeni IP: {current_ip}
🔒 Eski IP: {registered_ip}

🛠️ **YAPMANIZ GEREKENLER:**
1. developer.clashofclans.com'a gidin
2. Yeni API key oluşturun
3. IP: `{current_ip}` yazın
4. Yeni token'ı bana gönderin

⚡ **Otomatik çözüm geliştirilecek!**"""
            
        except Exception as e:
            text = f"❌ **IP kontrol hatası:** {str(e)}"
        
        self.send_message(chat_id, text)
    
    def handle_api_test_command(self, message):
        """API test komutu"""
        chat_id = message['chat']['id']
        
        headers = {
            'Authorization': f'Bearer {COC_API_TOKEN}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        try:
            # Header'ları yazdır
            text = f"""🔧 **API Test - Debug Bilgisi**

🔑 **Token (ilk 50 karakter):** {COC_API_TOKEN[:50]}...
📡 **Headers:** {list(headers.keys())}
🎯 **Klan Tag:** {CLAN_TAG}

⏳ **API Testi yapılıyor...**

"""
            
            # Basit API testi
            clan_url = f"{COC_API_BASE}/clans/{CLAN_TAG.replace('#', '%23')}"
            print(f"🌐 API Request: {clan_url}")
            print(f"🔑 Headers: {headers}")
            
            response = requests.get(clan_url, headers=headers, timeout=15)
            
            text += f"""📡 **URL:** {clan_url}
📊 **Status Code:** {response.status_code}
🕐 **Response Time:** {datetime.now().strftime('%H:%M:%S')}

"""
            
            if response.status_code == 200:
                data = response.json()
                text += f"""✅ **BAŞARILI!**
🏰 Klan: {data.get('name', 'Bilinmiyor')}
👥 Üye: {data.get('members', 0)}
🌍 Ülke: {data.get('location', {}).get('name', 'Bilinmiyor')}
📈 Seviye: {data.get('clanLevel', 0)}
🏆 Puan: {data.get('clanPoints', 0)}"""
            
            elif response.status_code == 403:
                text += f"""❌ **403 FORBIDDEN**
🔒 Erişim reddedildi

**Debug Bilgisi:**
• Response: {response.text[:200]}
• Headers gönderildi: ✓
• Token uzunluğu: {len(COC_API_TOKEN)} karakter

💡 **Muhtemel sebepler:**
• API key süresi dolmuş
• IP adresi değişmiş
• Rate limit aşıldı"""
            
            elif response.status_code == 404:
                text += f"""❌ **404 NOT FOUND**
🔍 Klan bulunamadı: {CLAN_TAG}

**Klan tag'inizi kontrol edin:**
• Doğru yazıldı mı?
• # işareti var mı?
• Klan hala mevcut mu?"""
            
            else:
                text += f"""❌ **HATA: {response.status_code}**
📝 Response: {response.text[:300]}
🔍 Headers sent: {headers}"""
                
        except Exception as e:
            text = f"""❌ **Bağlantı Hatası:**
🚫 Error: {str(e)}
🌐 URL: {clan_url if 'clan_url' in locals() else 'N/A'}"""
        
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

if __name__ == '__main__':
    bot = AutoClanManager()
    bot.run()
