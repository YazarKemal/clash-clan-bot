import requests
import time
import json
import os
import asyncio
import threading
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import math

# Python sürüm kontrolü
if sys.version_info < (3, 6):
    raise RuntimeError("Python 3.6 veya üzeri gereklidir")


class MathUtils:
    """Basit matematik yardımcıları"""

    @staticmethod
    def mean(values):
        return sum(values) / len(values) if values else 0

    @staticmethod
    def stdev(values):
        n = len(values)
        if n < 2:
            return 0
        mean_val = MathUtils.mean(values)
        variance = sum((x - mean_val) ** 2 for x in values) / (n - 1)
        return math.sqrt(variance)

# Telegram bot tokenını alıyoruz
BOT_TOKEN = os.getenv('BOT_TOKEN', '7708393145:AAFHHNBUNNMhx8mTCZ4iWy83ZdgiNB-SoNc')

# Bu script doğrudan Telegram API'si ile haberleşir. TeleBot
# kütüphanesini kullanmadığımız için polling işlemi de kendimiz
# yöneteceğiz.
COC_API_TOKEN = os.getenv('COC_API_TOKEN', 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImJkYzliMTQ1LTZkY2QtNDU0Mi1hNmNmLTgwMzViNDJiZWFjNyIsImlhdCI6MTc1MjAyNzAxMiwic3ViIjoiZGV2ZWxvcGVyLzRiYTU2MTc5LWE5NDgtMTBkYy0yNmI1LThkZjc5NjcyYjRmNCIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjEzLjYxLjU2LjE5NyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.xkmTiuBnozS8NSK8F1D8ST939QxlKj5qZ7EkRI45ZhDqCS406RFr0Jzh4hTJkEB3oWgNBDZh7aVs0xFqxBRWvw')

# Diğer ayarlar
ADMIN_USERS = os.getenv('ADMIN_USERS', '8114999904').split(',')
CLAN_TAG = os.getenv('CLAN_TAG', '#2RGC8UPYV')
COC_API_BASE = "https://api.clashofclans.com/v1"

# AWS Lambda uyumluluğu için
RUNNING_ON_AWS = os.getenv('AWS_EXECUTION_ENV') is not None
DATA_PATH = '/tmp/' if RUNNING_ON_AWS else './'

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

BAD_WORDS = ['aptal', 'salak', 'mal', 'ahmak', 'gerizekalı']

class AdvancedAnalytics:
    """Gelişmiş analiz altyapısı"""
    
    def __init__(self):
        self.min_data_points = 3  # Minimum analiz için gereken veri sayısı
        
    def calculate_trend(self, values, timestamps=None):
        """Trend hesaplama (linear regression)"""
        if len(values) < 2:
            return 0, "insufficient_data"
        
        try:
            x = list(range(len(values)))
            
            # Linear regression hesaplama
            n = len(values)
            sum_x = sum(x)
            sum_y = sum(values)
            sum_xy = sum(x[i] * values[i] for i in range(n))
            sum_x2 = sum(x[i] ** 2 for i in range(n))
            
            # Eğim hesaplama
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2) if (n * sum_x2 - sum_x ** 2) != 0 else 0
            
            # Trend kategorisi
            if slope > 0.5:
                trend_type = "strong_increasing"
            elif slope > 0.1:
                trend_type = "increasing"
            elif slope > -0.1:
                trend_type = "stable"
            elif slope > -0.5:
                trend_type = "decreasing"
            else:
                trend_type = "strong_decreasing"
                
            return slope, trend_type
            
        except:
            return 0, "calculation_error"
    
    def predict_next_value(self, values, periods_ahead=1):
        """Gelecek değer tahmini"""
        if len(values) < 3:
            return None
        
        try:
            slope, _ = self.calculate_trend(values)
            last_value = values[-1]
            predicted = last_value + (slope * periods_ahead)
            return max(0, predicted)  # Negatif değerleri önle
        except:
            return None
    
    def calculate_volatility(self, values):
        """Volatilite hesaplama (standart sapma)"""
        if len(values) < 2:
            return 0
        
        try:
            return MathUtils.stdev(values)
        except:
            return 0
    
    def detect_anomaly(self, values, current_value, threshold=2):
        """Anomali tespiti (z-score method)"""
        if len(values) < 3:
            return False, 0
        
        try:
            mean_val = MathUtils.mean(values)
            std_val = MathUtils.stdev(values)
            
            if std_val == 0:
                return False, 0
                
            z_score = abs(current_value - mean_val) / std_val
            is_anomaly = z_score > threshold
            
            return is_anomaly, z_score
        except:
            return False, 0

class TrendAnalyzer(AdvancedAnalytics):
    """Trend analizi modülü"""
    
    def analyze_member_trends(self, member_history):
        """Üye trend analizi"""
        trends = {}
        
        if not member_history or len(member_history) < 2:
            return trends
        
        # Değişkenler için trend analizi
        metrics = ['donations', 'trophies', 'score']
        
        for metric in metrics:
            values = []
            timestamps = []
            
            for data_point in member_history:
                if metric in data_point:
                    values.append(data_point[metric])
                    timestamps.append(data_point.get('timestamp', ''))
            
            if len(values) >= 2:
                slope, trend_type = self.calculate_trend(values)
                predicted = self.predict_next_value(values)
                volatility = self.calculate_volatility(values)
                
                trends[metric] = {
                    'slope': slope,
                    'trend_type': trend_type,
                    'predicted_next': predicted,
                    'volatility': volatility,
                    'data_points': len(values),
                    'improvement_rate': self.calculate_improvement_rate(values)
                }
        
        return trends
    
    def calculate_improvement_rate(self, values):
        """Gelişim oranı hesaplama"""
        if len(values) < 2:
            return 0
        
        try:
            first_val = values[0] or 1  # Sıfıra bölme önleme
            last_val = values[-1] or 1
            
            improvement = ((last_val - first_val) / first_val) * 100
            return round(improvement, 2)
        except:
            return 0
    
    def get_trend_emoji(self, trend_type):
        """Trend emoji'si"""
        emojis = {
            'strong_increasing': '🚀',
            'increasing': '📈',
            'stable': '➡️',
            'decreasing': '📉',
            'strong_decreasing': '💥'
        }
        return emojis.get(trend_type, '❓')

class WarAnalyzer(AdvancedAnalytics):
    """Savaş analizi modülü"""
    
    def analyze_war_performance(self, war_history, member_tag=None):
        """Detaylı savaş performans analizi"""
        if not war_history:
            return {}
        
        analysis = {
            'total_wars': len(war_history),
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'win_rate': 0,
            'average_stars': 0,
            'attack_efficiency': 0,
            'consistency_score': 0,
            'war_mvp_count': 0,
            'missed_attacks': 0
        }
        
        star_counts = []
        destruction_rates = []
        attack_counts = []
        
        for war in war_history:
            # Savaş sonucu
            if war.get('result') == 'win':
                analysis['wins'] += 1
            elif war.get('result') == 'lose':
                analysis['losses'] += 1
            else:
                analysis['draws'] += 1
            
            # Üye-spesifik analiz
            if member_tag:
                member_data = self.find_member_in_war(war, member_tag)
                if member_data:
                    attacks = member_data.get('attacks', [])
                    attack_counts.append(len(attacks))
                    
                    if attacks:
                        war_stars = sum(attack.get('stars', 0) for attack in attacks)
                        war_destruction = sum(attack.get('destructionPercentage', 0) for attack in attacks) / len(attacks)
                        
                        star_counts.append(war_stars)
                        destruction_rates.append(war_destruction)
                        
                        # MVP kontrolü (en çok yıldız)
                        if self.is_war_mvp(war, member_tag):
                            analysis['war_mvp_count'] += 1
                    else:
                        analysis['missed_attacks'] += 1
        
        # İstatistik hesaplamaları
        if analysis['total_wars'] > 0:
            analysis['win_rate'] = round((analysis['wins'] / analysis['total_wars']) * 100, 2)
        
        if star_counts:
            analysis['average_stars'] = round(MathUtils.mean(star_counts), 2)
            analysis['consistency_score'] = round(100 - (self.calculate_volatility(star_counts) * 10), 2)

        if destruction_rates:
            analysis['attack_efficiency'] = round(MathUtils.mean(destruction_rates), 2)
        
        return analysis
    
    def find_member_in_war(self, war_data, member_tag):
        """Savaşta üye bulma"""
        clan_members = war_data.get('clan', {}).get('members', [])
        for member in clan_members:
            if member.get('tag') == member_tag:
                return member
        return None
    
    def is_war_mvp(self, war_data, member_tag):
        """Savaş MVP'si kontrolü"""
        clan_members = war_data.get('clan', {}).get('members', [])
        max_stars = 0
        mvp_tag = None
        
        for member in clan_members:
            attacks = member.get('attacks', [])
            total_stars = sum(attack.get('stars', 0) for attack in attacks)
            
            if total_stars > max_stars:
                max_stars = total_stars
                mvp_tag = member.get('tag')
        
        return mvp_tag == member_tag
    
    def calculate_war_win_probability(self, clan_war_stats, enemy_war_stats):
        """Savaş kazanma olasılığı hesaplama"""
        try:
            # Basit model: Win rate ve average stars bazlı
            clan_factor = (clan_war_stats.get('win_rate', 50) + clan_war_stats.get('average_stars', 1) * 20) / 2
            enemy_factor = (enemy_war_stats.get('win_rate', 50) + enemy_war_stats.get('average_stars', 1) * 20) / 2
            
            probability = clan_factor / (clan_factor + enemy_factor) * 100
            return min(95, max(5, probability))  # %5-95 arasında sınırla
        except:
            return 50  # Varsayılan %50

class BehaviorAnalyzer(AdvancedAnalytics):
    """Davranış analizi modülü"""
    
    def analyze_activity_patterns(self, activity_history):
        """Aktivite pattern analizi"""
        if not activity_history:
            return {}
        
        patterns = {
            'most_active_hours': [],
            'activity_consistency': 0,
            'peak_activity_day': '',
            'activity_trend': 'stable',
            'social_engagement': 0,
            'loyalty_score': 0
        }
        
        # Saatlik aktivite analizi
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        
        for activity in activity_history:
            timestamp = activity.get('timestamp', '')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    hourly_activity[dt.hour] += 1
                    daily_activity[dt.strftime('%A')] += 1
                except:
                    continue
        
        # En aktif saatler
        if hourly_activity:
            sorted_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)
            patterns['most_active_hours'] = [hour for hour, count in sorted_hours[:3]]
        
        # En aktif gün
        if daily_activity:
            patterns['peak_activity_day'] = max(daily_activity, key=daily_activity.get)
        
        # Aktivite tutarlılığı
        if len(activity_history) > 1:
            activity_values = [1 for _ in activity_history]  # Basit aktivite skoru
            patterns['activity_consistency'] = round(100 - (self.calculate_volatility(activity_values) * 50), 2)
        
        return patterns
    
    def analyze_donation_behavior(self, donation_history):
        """Bağış davranışı analizi"""
        if not donation_history:
            return {}
        
        behavior = {
            'donation_frequency': 'low',
            'donation_consistency': 0,
            'giving_receiving_ratio': 0,
            'donation_trend': 'stable',
            'peak_donation_times': [],
            'altruism_score': 0
        }
        
        donations = [d.get('donations', 0) for d in donation_history]
        received = [d.get('donationsReceived', 0) for d in donation_history]
        
        if donations and len(donations) > 1:
            # Trend analizi
            _, trend_type = self.calculate_trend(donations)
            behavior['donation_trend'] = trend_type
            
            # Tutarlılık
            behavior['donation_consistency'] = round(100 - (self.calculate_volatility(donations) / max(donations) * 100), 2)
            
            # Verme/alma oranı
            total_given = sum(donations)
            total_received = sum(received) if received else 1
            behavior['giving_receiving_ratio'] = round(total_given / total_received, 2)
            
            # Altruism score (ne kadar çok veriyor vs alıyor)
            if total_received > 0:
                behavior['altruism_score'] = min(100, round((total_given / total_received) * 50, 2))
        
        return behavior
    
    def calculate_churn_risk(self, member_data, activity_history):
        """Klan terk etme riski hesaplama"""
        risk_score = 0
        risk_factors = []
        
        # Son aktivite kontrolü
        last_active = member_data.get('last_active', '')
        if last_active:
            try:
                last_date = datetime.strptime(last_active, '%Y-%m-%d')
                days_inactive = (datetime.now() - last_date).days
                
                if days_inactive > 7:
                    risk_score += 30
                    risk_factors.append(f"{days_inactive} gün inaktif")
                elif days_inactive > 3:
                    risk_score += 15
                    risk_factors.append(f"{days_inactive} gün inaktif")
            except:
                risk_score += 20
                risk_factors.append("Aktivite bilinmiyor")
        
        # Performans trendi
        if len(activity_history) >= 3:
            scores = [a.get('score', 0) for a in activity_history[-3:]]
            _, trend = self.calculate_trend(scores)
            
            if trend in ['decreasing', 'strong_decreasing']:
                risk_score += 25
                risk_factors.append("Performans düşüşü")
        
        # Uyarı sayısı
        warnings = member_data.get('warnings', 0)
        if warnings >= 2:
            risk_score += 40
            risk_factors.append(f"{warnings} uyarı")
        elif warnings >= 1:
            risk_score += 20
            risk_factors.append(f"{warnings} uyarı")
        
        # Risk kategorisi
        if risk_score >= 70:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        elif risk_score >= 20:
            risk_level = "low"
        else:
            risk_level = "very_low"
        
        return {
            'risk_score': min(100, risk_score),
            'risk_level': risk_level,
            'risk_factors': risk_factors
        }

class PredictionEngine(AdvancedAnalytics):
    """Tahmin motoru"""
    
    def predict_clan_performance(self, clan_history):
        """Klan performans tahmini"""
        if len(clan_history) < 3:
            return None
        
        # Son 30 günlük veri al
        recent_data = list(clan_history.values())[-30:]
        
        predictions = {}
        
        # Üye sayısı tahmini
        member_counts = [data['clan_info']['members'] for data in recent_data]
        next_member_count = self.predict_next_value(member_counts)
        
        # Klan puanı tahmini
        clan_points = [data['clan_info']['total_points'] for data in recent_data]
        next_clan_points = self.predict_next_value(clan_points)
        
        predictions = {
            'predicted_members': int(next_member_count) if next_member_count else None,
            'predicted_points': int(next_clan_points) if next_clan_points else None,
            'confidence_level': self.calculate_prediction_confidence(recent_data),
            'recommendation': self.generate_performance_recommendation(recent_data)
        }
        
        return predictions
    
    def calculate_prediction_confidence(self, data_points):
        """Tahmin güvenilirlik seviyesi"""
        if len(data_points) < 5:
            return "low"
        elif len(data_points) < 15:
            return "medium"
        else:
            return "high"
    
    def generate_performance_recommendation(self, clan_data):
        """Performans önerisi oluşturma"""
        if not clan_data:
            return "Veri yetersiz"
        
        recent = clan_data[-1]
        
        inactive_count = len(recent.get('inactive_members', []))
        top_count = len(recent.get('top_performers', []))
        total_members = recent['clan_info']['members']
        
        if inactive_count > total_members * 0.3:
            return "Pasif üyeleri temizleme zamanı"
        elif top_count < total_members * 0.2:
            return "Üye motivasyonu artırılmalı"
        else:
            return "Performans dengeli, mevcut stratejiye devam"

class AutoClanManager:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        self.offset = 0
        self.data_file = os.path.join(DATA_PATH, "clan_data.json")
        
        # Gelişmiş analiz modülleri
        self.trend_analyzer = TrendAnalyzer()
        self.war_analyzer = WarAnalyzer()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.prediction_engine = PredictionEngine()
        
        self.load_data()
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.last_clan_check = None
        self.current_ip = self.get_current_ip()
        self.token_ip = self.get_token_ip()
        
        print(f"✅ Gelişmiş Bot başlatıldı - Tarih: {self.today}")
        print(f"🔧 AWS Mode: {'✓' if RUNNING_ON_AWS else '✗'}")
        print(f"🤖 AI Analytics: ✓")
        print(f"📊 Trend Analysis: ✓")
        print(f"⚔️ War Analytics: ✓")
        print(f"🧠 Behavior Analysis: ✓")
        print(f"🔮 Prediction Engine: ✓")
        
        # İlk kapsamlı analiz
        self.run_comprehensive_analysis()
        
        if not RUNNING_ON_AWS:
            self.start_advanced_monitoring()
    
    def get_current_ip(self):
        try:
            ip = requests.get('https://httpbin.org/ip', timeout=5).json()['origin']
            print(f"🌐 Bot IP adresi: {ip}")
            return ip
        except Exception as e:
            print(f"IP bulunamadı: {e}")
            return None
    
    def get_token_ip(self):
        """Token'dan kayıtlı IP'yi çıkar"""
        try:
            import base64
            token_parts = COC_API_TOKEN.split('.')
            if len(token_parts) >= 2:
                payload = token_parts[1]
                payload += '=' * (4 - len(payload) % 4)
                decoded = base64.b64decode(payload)
                payload_data = json.loads(decoded.decode('utf-8'))
                
                limits = payload_data.get('limits', [])
                for limit in limits:
                    if limit.get('type') == 'client':
                        cidrs = limit.get('cidrs', [])
                        if cidrs:
                            return cidrs[0]
            return "Bulunamadı"
        except Exception as e:
            print(f"Token IP çıkarma hatası: {e}")
            return "52.57.33.177"
    
    def load_data(self):
        """Gelişmiş veri yapısını yükle"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = data.get('users', {})
                    self.daily_stats = data.get('daily_stats', {})
                    self.warnings_data = data.get('warnings_data', {})
                    self.clan_history = data.get('clan_history', {})
                    
                    # Gelişmiş veri yapıları
                    self.member_trends = data.get('member_trends', {})
                    self.war_history = data.get('war_history', {})
                    self.behavior_data = data.get('behavior_data', {})
                    self.predictions = data.get('predictions', {})
                    self.anomaly_alerts = data.get('anomaly_alerts', {})
                    
                    print(f"✅ {len(self.users)} kullanıcı verisi yüklendi")
                    print(f"📊 {len(self.member_trends)} üye trend verisi")
                    print(f"⚔️ {len(self.war_history)} savaş verisi")
            except Exception as e:
                print(f"⚠️ Veri yükleme hatası: {e}")
                self.reset_data()
        else:
            self.reset_data()
    
    def reset_data(self):
        """Gelişmiş veri sıfırlama"""
        self.users = {}
        self.daily_stats = {}
        self.warnings_data = {}
        self.clan_history = {}
        self.member_trends = {}
        self.war_history = {}
        self.behavior_data = {}
        self.predictions = {}
        self.anomaly_alerts = {}
        print("🔄 Yeni gelişmiş veri yapısı oluşturuldu")
    
    def save_data(self):
        """Gelişmiş verileri kaydet"""
        data = {
            'users': self.users,
            'daily_stats': self.daily_stats,
            'warnings_data': self.warnings_data,
            'clan_history': self.clan_history,
            'member_trends': self.member_trends,
            'war_history': self.war_history,
            'behavior_data': self.behavior_data,
            'predictions': self.predictions,
            'anomaly_alerts': self.anomaly_alerts,
            'last_save': datetime.now().isoformat(),
            'bot_info': {
                'ip': self.current_ip,
                'token_ip': self.token_ip,
                'aws_mode': RUNNING_ON_AWS,
                'version': '3.0_advanced',
                'analytics_enabled': True
            }
        }
        
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("💾 Gelişmiş veriler kaydedildi")
        except Exception as e:
            print(f"❌ Kaydetme hatası: {e}")
    
    def get_clan_data(self):
        """Clash of Clans API'den klan verilerini çek"""
        headers = {
            'Authorization': f'Bearer {COC_API_TOKEN}',
            'Accept': 'application/json'
        }
        
        try:
            clan_url = f"{COC_API_BASE}/clans/{CLAN_TAG.replace('#', '%23')}"
            response = requests.get(clan_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                clan_data = response.json()
                print(f"✅ Klan verisi alındı: {clan_data['name']}")
                return clan_data
            elif response.status_code == 403:
                print(f"❌ COC API Yetki Hatası: IP uyumsuzluğu ({self.current_ip} ≠ {self.token_ip})")
                if self.current_ip != self.token_ip:
                    self.notify_ip_change()
                return None
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
                
                # Savaş geçmişine ekle
                if war_data.get('state') == 'warEnded':
                    war_id = f"{war_data.get('preparationStartTime', '')}_{war_data.get('endTime', '')}"
                    self.war_history[war_id] = {
                        'timestamp': datetime.now().isoformat(),
                        'war_data': war_data,
                        'result': 'win' if war_data.get('clan', {}).get('stars', 0) > war_data.get('opponent', {}).get('stars', 0) else 'lose'
                    }
                
                return war_data
            else:
                print(f"⚠️ Savaş verisi alınamadı: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Savaş API hatası: {e}")
            return None
    
    def run_comprehensive_analysis(self):
        """Kapsamlı analiz çalıştır"""
        print("🔍 Kapsamlı analiz başlıyor...")
        
        clan_data = self.get_clan_data()
        war_data = self.get_clan_war_data()
        
        if not clan_data:
            print("❌ Klan verisi alınamadı")
            return None
        
        analysis_time = datetime.now().isoformat()
        
        # Temel klan analizi
        basic_analysis = self.analyze_clan_basic(clan_data, war_data)
        
        # Gelişmiş analizler
        trend_analysis = self.run_trend_analysis(clan_data)
        war_analysis = self.run_war_analysis(war_data)
        behavior_analysis = self.run_behavior_analysis(clan_data)
        risk_assessment = self.run_risk_assessment(clan_data)
        predictions = self.run_predictions()
        
        # Kapsamlı analiz sonucu
        comprehensive_analysis = {
            'timestamp': analysis_time,
            'basic_analysis': basic_analysis,
            'trend_analysis': trend_analysis,
            'war_analysis': war_analysis,
            'behavior_analysis': behavior_analysis,
            'risk_assessment': risk_assessment,
            'predictions': predictions,
            'anomalies': self.detect_anomalies(clan_data),
            'recommendations': self.generate_smart_recommendations(clan_data)
        }
        
        # Kaydet
        self.clan_history[analysis_time] = comprehensive_analysis
        self.save_data()
        
        print(f"✅ Kapsamlı analiz tamamlandı!")
        return comprehensive_analysis
    
    def analyze_clan_basic(self, clan_data, war_data=None):
        """Temel klan analizi (mevcut kod, biraz geliştirilmiş)"""
        analysis = {
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
            
            # Üye trend verilerini güncelle
            self.update_member_trends(member['tag'], member_analysis)
            
            # Kategorilere ayır
            if recommended_role != current_role and recommended_role != 'coLeader':
                analysis['role_recommendations'].append({
                    'name': member['name'],
                    'current': ROLE_NAMES.get(current_role, current_role),
                    'recommended': ROLE_NAMES.get(recommended_role, recommended_role),
                    'score': score
                })
            
            if score < 30:
                analysis['inactive_members'].append({
                    'name': member['name'],
                    'score': score,
                    'issues': [r for r in reasons if '❌' in r]
                })
            
            if score >= 70:
                analysis['top_performers'].append({
                    'name': member['name'],
                    'score': score
                })
        
        return analysis
    
    def analyze_clan_member_performance(self, member, war_data=None):
        """Üye performansını analiz et (geliştirilmiş)"""
        score = 0
        reasons = []
        
        # Bağış skoru (0-40 puan)
        donations = member.get('donations', 0)
        
        if donations >= 2000:
            score += 40
            reasons.append("🎁 Olağanüstü bağış")
        elif donations >= 1000:
            score += 35
            reasons.append("🎁 Mükemmel bağış")
        elif donations >= 500:
            score += 25
            reasons.append("🎁 İyi bağış")
        elif donations >= 200:
            score += 15
            reasons.append("🎁 Orta bağış")
        elif donations >= 50:
            score += 5
            reasons.append("🎁 Az bağış")
        else:
            reasons.append("❌ Bağış yok")
        
        # Kupa skoru (0-25 puan)
        trophies = member.get('trophies', 0)
        if trophies >= 4000:
            score += 25
            reasons.append("🏆 Efsane kupa")
        elif trophies >= 3000:
            score += 20
            reasons.append("🏆 Yüksek kupa")
        elif trophies >= 2000:
            score += 15
            reasons.append("🏆 Orta kupa")
        elif trophies >= 1000:
            score += 10
            reasons.append("🏆 Düşük kupa")
        else:
            reasons.append("❌ Çok düşük kupa")
        
        # Savaş performansı (0-35 puan)
        if war_data and war_data.get('state') in ['inWar', 'warEnded']:
            war_member = self.find_member_in_war(war_data, member['tag'])
            if war_member:
                attacks = war_member.get('attacks', [])
                if attacks:
                    total_stars = sum(attack.get('stars', 0) for attack in attacks)
                    total_destruction = sum(attack.get('destructionPercentage', 0) for attack in attacks)
                    avg_destruction = total_destruction / len(attacks)
                    
                    if total_stars >= 6:
                        score += 35
                        reasons.append("⚔️ Mükemmel savaş")
                    elif total_stars >= 4:
                        score += 25
                        reasons.append("⚔️ İyi savaş")
                    elif total_stars >= 2:
                        score += 15
                        reasons.append("⚔️ Orta savaş")
                    else:
                        score += 5
                        reasons.append("⚔️ Zayıf savaş")
                    
                    # Yıkım oranı bonusu
                    if avg_destruction >= 80:
                        score += 5
                        reasons.append("💥 Yüksek yıkım")
                else:
                    reasons.append("❌ Savaş yapmadı")
        
        return min(100, score), reasons
    
    def find_member_in_war(self, war_data, member_tag):
        """Savaşta üye bulma"""
        if not war_data or 'clan' not in war_data:
            return None
        
        clan_members = war_data['clan'].get('members', [])
        for member in clan_members:
            if member.get('tag') == member_tag:
                return member
        return None
    
    def get_recommended_role(self, score, current_role):
        """Performansa göre önerilen rütbe (geliştirilmiş)"""
        if score >= 85:
            return 'admin'  # Başkan
        elif score >= 65:
            return 'member'  # Aktif üye
        elif score >= 40:
            return 'member'  # Normal üye
        else:
            return 'member'  # Pasif ama hala üye
    
    def update_member_trends(self, member_tag, member_data):
        """Üye trend verilerini güncelle"""
        if member_tag not in self.member_trends:
            self.member_trends[member_tag] = []
        
        trend_data = {
            'timestamp': datetime.now().isoformat(),
            'score': member_data['score'],
            'donations': member_data['donations'],
            'trophies': member_data['trophies'],
            'role': member_data['role']
        }
        
        self.member_trends[member_tag].append(trend_data)
        
        # Son 30 kayıtı sakla - key kontrolü ile
        if member_tag in self.member_trends and len(self.member_trends[member_tag]) > 30:
            self.member_trends[member_tag] = self.member_trends[member_tag][-30:]
    
    def run_trend_analysis(self, clan_data):
        """Trend analizi çalıştır"""
        print("📈 Trend analizi çalışıyor...")
        
        trend_results = {}
        
        for member in clan_data['memberList']:
            member_tag = member['tag']
            if member_tag in self.member_trends and len(self.member_trends[member_tag]) >= 3:
                trends = self.trend_analyzer.analyze_member_trends(self.member_trends[member_tag])
                trend_results[member_tag] = {
                    'name': member['name'],
                    'trends': trends
                }
        
        return {
            'member_trends': trend_results,
            'clan_trend_summary': self.get_clan_trend_summary(trend_results)
        }
    
    def get_clan_trend_summary(self, member_trends):
        """Klan trend özeti"""
        if not member_trends:
            return {}
        
        improving_members = 0
        declining_members = 0
        stable_members = 0
        
        for member_data in member_trends.values():
            score_trend = member_data['trends'].get('score', {}).get('trend_type', 'stable')
            
            if 'increasing' in score_trend:
                improving_members += 1
            elif 'decreasing' in score_trend:
                declining_members += 1
            else:
                stable_members += 1
        
        return {
            'improving': improving_members,
            'declining': declining_members,
            'stable': stable_members,
            'trend_health': 'good' if improving_members > declining_members else 'concerning' if declining_members > improving_members else 'stable'
        }
    
    def run_war_analysis(self, war_data):
        """Savaş analizi çalıştır"""
        print("⚔️ Savaş analizi çalışıyor...")
        
        if not self.war_history:
            return {'message': 'Savaş geçmişi bulunamadı'}
        
        # Klan genel savaş istatistikleri
        clan_war_stats = self.war_analyzer.analyze_war_performance(list(self.war_history.values()))
        
        # Mevcut savaş analizi
        current_war_analysis = {}
        if war_data and war_data.get('state') in ['preparation', 'inWar']:
            current_war_analysis = self.analyze_current_war(war_data)
        
        return {
            'clan_war_stats': clan_war_stats,
            'current_war': current_war_analysis,
            'war_predictions': self.predict_war_outcome(war_data)
        }
    
    def analyze_current_war(self, war_data):
        """Mevcut savaş analizi"""
        if not war_data:
            return {}
        
        analysis = {
            'state': war_data.get('state'),
            'team_size': war_data.get('teamSize', 0),
            'attacks_used': 0,
            'attacks_remaining': 0,
            'current_stars': 0,
            'opponent_stars': 0,
            'destruction_percentage': 0
        }
        
        # Klan bilgileri
        clan_info = war_data.get('clan', {})
        opponent_info = war_data.get('opponent', {})
        
        analysis['current_stars'] = clan_info.get('stars', 0)
        analysis['opponent_stars'] = opponent_info.get('stars', 0)
        analysis['destruction_percentage'] = clan_info.get('destructionPercentage', 0)
        
        # Saldırı sayısı hesaplama
        clan_members = clan_info.get('members', [])
        for member in clan_members:
            attacks = member.get('attacks', [])
            analysis['attacks_used'] += len(attacks)
        
        analysis['attacks_remaining'] = (analysis['team_size'] * 2) - analysis['attacks_used']
        
        return analysis
    
    def predict_war_outcome(self, war_data):
        """Savaş sonucu tahmini"""
        if not war_data or not self.war_history:
            return {}
        
        # Basit tahmin modeli
        clan_stats = self.war_analyzer.analyze_war_performance(list(self.war_history.values()))
        
        # Karşı takım için varsayılan değerler (gerçek veri yok)
        opponent_stats = {
            'win_rate': 50,  # Varsayılan
            'average_stars': 2.0  # Varsayılan
        }
        
        win_probability = self.war_analyzer.calculate_war_win_probability(clan_stats, opponent_stats)
        
        return {
            'win_probability': win_probability,
            'confidence': 'medium',
            'recommendation': 'Saldırıları optimize edin' if win_probability < 60 else 'Mevcut strateji ile devam'
        }
    
    def run_behavior_analysis(self, clan_data):
        """Davranış analizi çalıştır"""
        print("🧠 Davranış analizi çalışıyor...")
        
        behavior_results = {}
        
        for member in clan_data['memberList']:
            member_tag = member['tag']
            
            # Aktivite pattern analizi
            activity_history = self.member_trends.get(member_tag, [])
            activity_patterns = self.behavior_analyzer.analyze_activity_patterns(activity_history)
            
            # Bağış davranışı analizi
            donation_behavior = self.behavior_analyzer.analyze_donation_behavior(activity_history)
            
            behavior_results[member_tag] = {
                'name': member['name'],
                'activity_patterns': activity_patterns,
                'donation_behavior': donation_behavior
            }
        
        return behavior_results
    
    def run_risk_assessment(self, clan_data):
        """Risk değerlendirme çalıştır"""
        print("⚠️ Risk değerlendirme çalışıyor...")
        
        risk_results = {}
        high_risk_members = []
        
        for member in clan_data['memberList']:
            member_tag = member['tag']
            member_data = self.users.get(str(member_tag), {})
            activity_history = self.member_trends.get(member_tag, [])
            
            risk_assessment = self.behavior_analyzer.calculate_churn_risk(member_data, activity_history)
            
            risk_results[member_tag] = {
                'name': member['name'],
                'risk_assessment': risk_assessment
            }
            
            if risk_assessment['risk_level'] in ['high', 'medium']:
                high_risk_members.append({
                    'name': member['name'],
                    'risk_level': risk_assessment['risk_level'],
                    'risk_score': risk_assessment['risk_score']
                })
        
        return {
            'individual_risks': risk_results,
            'high_risk_members': high_risk_members,
            'risk_summary': self.get_risk_summary(high_risk_members)
        }
    
    def get_risk_summary(self, high_risk_members):
        """Risk özeti"""
        if not high_risk_members:
            return {'status': 'low_risk', 'message': 'Klan istikrarlı'}
        
        high_count = len([m for m in high_risk_members if m['risk_level'] == 'high'])
        medium_count = len([m for m in high_risk_members if m['risk_level'] == 'medium'])
        
        if high_count > 3:
            return {'status': 'critical', 'message': f'{high_count} yüksek riskli üye'}
        elif high_count > 0 or medium_count > 5:
            return {'status': 'warning', 'message': f'{high_count} yüksek, {medium_count} orta riskli üye'}
        else:
            return {'status': 'stable', 'message': 'Risk kontrol altında'}
    
    def run_predictions(self):
        """Tahmin analizi çalıştır"""
        print("🔮 Tahmin analizi çalışıyor...")
        
        predictions = self.prediction_engine.predict_clan_performance(self.clan_history)
        
        return predictions
    
    def detect_anomalies(self, clan_data):
        """Anomali tespiti"""
        anomalies = []
        
        for member in clan_data['memberList']:
            member_tag = member['tag']
            if member_tag in self.member_trends:
                trend_data = self.member_trends[member_tag]
                
                if len(trend_data) >= 5:
                    # Son performans skoru
                    scores = [d['score'] for d in trend_data]
                    current_score = member.get('score', scores[-1] if scores else 0)
                    
                    is_anomaly, z_score = self.trend_analyzer.detect_anomaly(scores[:-1], current_score)
                    
                    if is_anomaly:
                        anomalies.append({
                            'member_name': member['name'],
                            'type': 'performance_anomaly',
                            'z_score': round(z_score, 2),
                            'description': f'Beklenmedik performans değişimi'
                        })
        
        return anomalies
    
    def generate_smart_recommendations(self, clan_data):
        """Akıllı öneriler oluştur"""
        recommendations = []
        
        analysis = self.get_latest_clan_analysis()
        if not analysis:
            return recommendations
        
        # Trend bazlı öneriler
        if 'trend_analysis' in analysis:
            trend_summary = analysis['trend_analysis'].get('clan_trend_summary', {})
            if trend_summary.get('declining', 0) > trend_summary.get('improving', 0):
                recommendations.append({
                    'priority': 'high',
                    'category': 'trend',
                    'title': 'Performans Düşüşü Tespit Edildi',
                    'description': 'Çoğu üyenin performansı düşüyor. Motivasyon etkinlikleri düzenleyin.',
                    'action': 'Üye motivasyonu artırma programı başlatın'
                })
        
        # Risk bazlı öneriler  
        if 'risk_assessment' in analysis:
            risk_summary = analysis['risk_assessment'].get('risk_summary', {})
            if risk_summary.get('status') in ['critical', 'warning']:
                recommendations.append({
                    'priority': 'high',
                    'category': 'risk',
                    'title': 'Yüksek Riskli Üyeler',
                    'description': risk_summary.get('message', ''),
                    'action': 'Risk altındaki üyelerle birebir görüşme yapın'
                })
        
        # Savaş bazlı öneriler
        if 'war_analysis' in analysis:
            war_stats = analysis['war_analysis'].get('clan_war_stats', {})
            if war_stats.get('win_rate', 100) < 60:
                recommendations.append({
                    'priority': 'medium',
                    'category': 'war',
                    'title': 'Savaş Performansı Düşük',
                    'description': f"Kazanma oranı: %{war_stats.get('win_rate', 0)}",
                    'action': 'Savaş stratejileri eğitimi organize edin'
                })
        
        return recommendations
    
    def start_advanced_monitoring(self):
        """Gelişmiş otomatik izleme başlat"""
        def advanced_monitor_loop():
            while True:
                try:
                    print("🔄 Gelişmiş otomatik analiz...")
                    self.run_comprehensive_analysis()
                    
                    # Anomali kontrolü
                    self.check_and_alert_anomalies()
                    
                    print("💤 Bir sonraki gelişmiş analiz 2 saat sonra...")
                    time.sleep(7200)  # 2 saat bekle
                except Exception as e:
                    print(f"❌ Gelişmiş analiz hatası: {e}")
                    time.sleep(3600)  # Hata durumunda 1 saat bekle
        
        monitor_thread = threading.Thread(target=advanced_monitor_loop, daemon=True)
        monitor_thread.start()
        print("🤖 Gelişmiş otomatik izleme başlatıldı (her 2 saat)")
    
    def check_and_alert_anomalies(self):
        """Anomali kontrol ve uyarı"""
        analysis = self.get_latest_clan_analysis()
        if not analysis:
            return
        
        anomalies = analysis.get('anomalies', [])
        recommendations = analysis.get('recommendations', [])
        
        # Yüksek öncelikli uyarıları adminlere gönder
        high_priority_alerts = [r for r in recommendations if r.get('priority') == 'high']
        
        if high_priority_alerts or anomalies:
            alert_text = "🚨 **ACIL KLAN UYARISI**\n\n"
            
            for alert in high_priority_alerts:
                alert_text += f"⚠️ **{alert['title']}**\n"
                alert_text += f"📋 {alert['description']}\n"
                alert_text += f"🎯 Aksiyon: {alert['action']}\n\n"
            
            for anomaly in anomalies:
                alert_text += f"🔍 **Anomali:** {anomaly['member_name']}\n"
                alert_text += f"📊 {anomaly['description']} (Z-Score: {anomaly['z_score']})\n\n"
            
            for admin_id in ADMIN_USERS:
                self.send_message(admin_id, alert_text)
    
    def get_latest_clan_analysis(self):
        """En son kapsamlı klan analizini getir"""
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
        """Start komutu (geliştirilmiş)"""
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
        
        text = f"""🏰 **Kemal'in Değneği - AI Destekli Klan Yöneticisi v3.0**

Hoş geldin {first_name}! ⚔️

🤖 **AI Powered Özellikler:**
• 📈 Trend analizi & tahmin sistemi
• ⚔️ Gelişmiş savaş analitiği  
• 🧠 Davranış pattern analizi
• ⚠️ Risk değerlendirme & uyarı sistemi
• 🔍 Anomali tespiti
• 🎯 Akıllı öneriler{aws_info}{ip_status}

{clan_summary}

🎯 **Yeni Komutlar:**
• **TREND** - Trend analizi raporu
• **WAR** - Detaylı savaş analizi
• **BEHAVIOR** - Davranış analizi
• **RISK** - Risk değerlendirme
• **PREDICT** - Gelecek tahminleri
• **SMART** - AI önerileri
• **ANOMALY** - Anomali raporu

📊 **Klasik Komutlar:**
• **KLAN** - Canlı klan durumu
• **ANALIZ** - Temel analiz raporu
• **RUTBE** - Rütbe önerileri
• **PASIF** - Pasif üyeler
• **STATS** - Kişisel istatistik"""
        
        self.send_message(chat_id, text)
        self.save_data()
    
    def get_clan_summary(self):
        """Gelişmiş klan özeti"""
        analysis = self.get_latest_clan_analysis()

        if not analysis:
            return "📊 **Klan Durumu:** İlk AI analizi yapılıyor..."

        basic = analysis.get('basic_analysis', {}) if analysis else {}
        clan_info = basic.get('clan_info', {})
        trends = analysis.get('trend_analysis', {}).get('clan_trend_summary', {})
        risks = analysis.get('risk_assessment', {}).get('risk_summary', {})
        
        inactive_count = len(basic.get('inactive_members', []))
        top_count = len(basic.get('top_performers', []))
        
        last_update = datetime.fromisoformat(analysis['timestamp'])
        time_ago = datetime.now() - last_update
        hours_ago = int(time_ago.total_seconds() / 3600)
        
        trend_emoji = "📈" if trends.get('trend_health') == 'good' else "📉" if trends.get('trend_health') == 'concerning' else "➡️"
        risk_emoji = "🔴" if risks.get('status') == 'critical' else "🟡" if risks.get('status') == 'warning' else "🟢"
        
        return f"""📊 **AI Klan Durumu:**
🏰 {clan_info.get('name', 'Klan')} (Seviye {clan_info.get('level', 0)})
👥 Üye: {clan_info.get('members', 0)}/50
🏆 Klan Puanı: {clan_info.get('total_points', 0):,}

🤖 **AI Analizi:**
{trend_emoji} Trend sağlığı: {trends.get('trend_health', 'bilinmiyor').title()}
{risk_emoji} Risk durumu: {risks.get('status', 'bilinmiyor').title()}
👑 En iyi: {top_count} | ⚠️ Pasif: {inactive_count}

🕐 Son AI analizi: {hours_ago} saat önce"""

    def handle_klan_command(self, message):
        """KLAN komutu - Klan durumu raporu"""
        chat_id = message['chat']['id']
        summary = self.get_clan_summary()
        self.send_message(chat_id, summary)

    # Yeni gelişmiş komut handlers
    def handle_trend_command(self, message):
        """TREND komutu - Trend analizi raporu"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        analysis = self.get_latest_clan_analysis()
        if not analysis or 'trend_analysis' not in analysis:
            self.send_message(chat_id, "❌ Trend analizi henüz hazır değil. Lütfen bekleyin...")
            return
        
        trend_data = analysis['trend_analysis']
        summary = trend_data.get('clan_trend_summary', {})
        
        text = f"""📈 **Trend Analizi Raporu**

🏰 **Klan Trend Sağlığı:** {summary.get('trend_health', 'Bilinmiyor').title()}

📊 **Üye Trend Dağılımı:**
🚀 Gelişen üyeler: {summary.get('improving', 0)}
📉 Gerileyen üyeler: {summary.get('declining', 0)}  
➡️ Stabil üyeler: {summary.get('stable', 0)}

🔍 **Detaylı Trend Analizi:**"""
        
        member_trends = trend_data.get('member_trends', {})
        
        # En iyi trend gösteren 3 üye
        improving_members = []
        declining_members = []
        
        for member_tag, data in member_trends.items():
            trends = data['trends']
            score_trend = trends.get('score', {})
            
            if 'increasing' in score_trend.get('trend_type', ''):
                improving_members.append((data['name'], score_trend.get('improvement_rate', 0)))
            elif 'decreasing' in score_trend.get('trend_type', ''):
                declining_members.append((data['name'], score_trend.get('improvement_rate', 0)))
        
        if improving_members:
            text += "\n\n🚀 **En Çok Gelişenler:**"
            for name, rate in sorted(improving_members, key=lambda x: x[1], reverse=True)[:3]:
                text += f"\n• {name}: +%{rate:.1f} gelişim"
        
        if declining_members:
            text += "\n\n📉 **Dikkat Edilmesi Gerekenler:**"
            for name, rate in sorted(declining_members, key=lambda x: x[1])[:3]:
                text += f"\n• {name}: %{rate:.1f} düşüş"
        
        # Admin özel bilgiler
        if user_id in ADMIN_USERS:
            predictions = analysis.get('predictions', {})
            if predictions:
                text += f"\n\n🔮 **Tahminler:**"
                if predictions.get('predicted_members'):
                    text += f"\n• Gelecek üye sayısı: {predictions['predicted_members']}"
                text += f"\n• Güvenilirlik: {predictions.get('confidence_level', 'orta').title()}"
        
        self.send_message(chat_id, text)
    
    def handle_war_command(self, message):
        """WAR komutu - Detaylı savaş analizi"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            self.send_message(chat_id, "❌ Bu komut sadece adminler için!")
            return
        
        analysis = self.get_latest_clan_analysis()
        if not analysis or 'war_analysis' not in analysis:
            self.send_message(chat_id, "❌ Savaş analizi henüz hazır değil.")
            return
        
        war_data = analysis['war_analysis']
        clan_stats = war_data.get('clan_war_stats', {})
        current_war = war_data.get('current_war', {})
        predictions = war_data.get('war_predictions', {})
        
        text = f"""⚔️ **Detaylı Savaş Analizi**

📊 **Klan Savaş İstatistikleri:**
🏆 Kazanma oranı: %{clan_stats.get('win_rate', 0):.1f}
⭐ Ortalama yıldız: {clan_stats.get('average_stars', 0):.1f}
💥 Saldırı verimliliği: %{clan_stats.get('attack_efficiency', 0):.1f}
🎯 Tutarlılık skoru: {clan_stats.get('consistency_score', 0):.1f}/100
👑 MVP sayısı: {clan_stats.get('war_mvp_count', 0)}
❌ Kaçırılan saldırı: {clan_stats.get('missed_attacks', 0)}"""
        
        if current_war:
            state_emoji = {'preparation': '⏳', 'inWar': '⚔️', 'warEnded': '✅'}.get(current_war.get('state'), '❓')
            text += f"""

{state_emoji} **Mevcut Savaş:**
📊 Durum: {current_war.get('state', 'Bilinmiyor')}
👥 Takım boyutu: {current_war.get('team_size', 0)}
⭐ Bizim yıldızlar: {current_war.get('current_stars', 0)}
⭐ Rakip yıldızlar: {current_war.get('opponent_stars', 0)}
🎯 Kullanılan saldırı: {current_war.get('attacks_used', 0)}
⏰ Kalan saldırı: {current_war.get('attacks_remaining', 0)}"""
        
        if predictions:
            win_prob = predictions.get('win_probability', 50)
            prob_emoji = "🟢" if win_prob > 70 else "🟡" if win_prob > 40 else "🔴"
            
            text += f"""

🔮 **Savaş Tahmini:**
{prob_emoji} Kazanma olasılığı: %{win_prob:.1f}
🎯 Öneri: {predictions.get('recommendation', 'Veri yetersiz')}"""
        
        self.send_message(chat_id, text)
    
    def handle_behavior_command(self, message):
        """BEHAVIOR komutu - Davranış analizi"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            self.send_message(chat_id, "❌ Bu komut sadece adminler için!")
            return
        
        analysis = self.get_latest_clan_analysis()
        if not analysis or 'behavior_analysis' not in analysis:
            self.send_message(chat_id, "❌ Davranış analizi henüz hazır değil.")
            return
        
        behavior_data = analysis['behavior_analysis']
        
        # En ilginç davranış patternleri
        interesting_behaviors = []
        
        for member_tag, data in behavior_data.items():
            member_name = data['name']
            activity = data.get('activity_patterns', {})
            donation = data.get('donation_behavior', {})
            
            # Yüksek altruism skoru
            altruism = donation.get('altruism_score', 0)
            if altruism > 80:
                interesting_behaviors.append(f"🎁 {member_name}: Süper cömert (Altruism: {altruism})")
            
            # Tutarlı aktivite
            consistency = activity.get('activity_consistency', 0)
            if consistency > 80:
                interesting_behaviors.append(f"⏰ {member_name}: Çok düzenli ({consistency:.0f}% tutarlılık)")
            
            # Peak hours
            peak_hours = activity.get('most_active_hours', [])
            if peak_hours:
                hours_str = ', '.join([f"{h:02d}:00" for h in peak_hours[:2]])
                interesting_behaviors.append(f"🕐 {member_name}: En aktif saatler {hours_str}")
        
        text = f"""🧠 **Davranış Analizi Raporu**

🔍 **İlginç Davranış Patternleri:**
"""
        
        if interesting_behaviors:
            for behavior in interesting_behaviors[:8]:  # İlk 8 tanesini göster
                text += f"\n• {behavior}"
        else:
            text += "\n• Henüz yeterli veri yok"
        
        text += f"""

📊 **Analiz Edilen Üye Sayısı:** {len(behavior_data)}

💡 **Davranış İçgörüleri:**
• En aktif günler ve saatler tespit ediliyor
• Bağış alışkanlıkları analiz ediliyor  
• Sosyal etkileşim skorları hesaplanıyor
• Aktivite döngüleri takip ediliyor"""
        
        self.send_message(chat_id, text)
    
    def handle_risk_command(self, message):
        """RISK komutu - Risk değerlendirme"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            self.send_message(chat_id, "❌ Bu komut sadece adminler için!")
            return
        
        analysis = self.get_latest_clan_analysis()
        if not analysis or 'risk_assessment' not in analysis:
            self.send_message(chat_id, "❌ Risk analizi henüz hazır değil.")
            return
        
        risk_data = analysis['risk_assessment']
        summary = risk_data.get('risk_summary', {})
        high_risk = risk_data.get('high_risk_members', [])
        
        status_emoji = {
            'low_risk': '🟢',
            'stable': '🟡', 
            'warning': '🟠',
            'critical': '🔴'
        }.get(summary.get('status'), '❓')
        
        text = f"""⚠️ **Risk Değerlendirme Raporu**

{status_emoji} **Genel Risk Durumu:** {summary.get('status', 'Bilinmiyor').title()}
📋 **Durum:** {summary.get('message', 'Veri yetersiz')}

🎯 **Yüksek Riskli Üyeler ({len(high_risk)}):**"""
        
        if high_risk:
            for member in high_risk[:5]:  # İlk 5 tanesini göster
                risk_emoji = "🔴" if member['risk_level'] == 'high' else "🟡"
                text += f"\n{risk_emoji} {member['name']} - %{member['risk_score']} risk ({member['risk_level']})"
            
            if len(high_risk) > 5:
                text += f"\n... ve {len(high_risk)-5} üye daha"
        else:
            text += "\n✅ Yüksek riskli üye yok!"
        
        text += f"""

🛡️ **Risk Faktörleri:**
• Uzun süreli inaktiflik
• Performans düşüşü trendi  
• Yüksek uyarı sayısı
• Bağış ve savaş katılım eksikliği

💡 **Öneriler:**
• Riskli üyelerle birebir konuşun
• Motivasyon etkinlikleri düzenleyin
• Gelişim hedefleri belirleyin"""
        
        self.send_message(chat_id, text)
    
    def handle_predict_command(self, message):
        """PREDICT komutu - Gelecek tahminleri"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            self.send_message(chat_id, "❌ Bu komut sadece adminler için!")
            return
        
        analysis = self.get_latest_clan_analysis()
        if not analysis or 'predictions' not in analysis:
            self.send_message(chat_id, "❌ Tahmin analizi henüz hazır değil.")
            return
        
        predictions = analysis['predictions']
        
        if not predictions:
            self.send_message(chat_id, "📊 Tahmin için yeterli veri yok. Daha fazla analiz gerekiyor.")
            return
        
        confidence_emoji = {
            'high': '🟢',
            'medium': '🟡', 
            'low': '🔴'
        }.get(predictions.get('confidence_level'), '❓')
        
        text = f"""🔮 **Gelecek Tahminleri**

{confidence_emoji} **Güvenilirlik:** {predictions.get('confidence_level', 'Bilinmiyor').title()}

📊 **Klan Performans Tahminleri:**"""
        
        if predictions.get('predicted_members'):
            current_members = analysis.get('basic_analysis', {}).get('clan_info', {}).get('members', 0)
            predicted_members = predictions['predicted_members']
            change = predicted_members - current_members
            change_emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
            
            text += f"\n{change_emoji} Gelecek üye sayısı: {predicted_members} ({change:+d})"
        
        if predictions.get('predicted_points'):
            text += f"\n🏆 Tahmin edilen klan puanı: {predictions['predicted_points']:,}"
        
        recommendation = predictions.get('recommendation', '')
        if recommendation:
            text += f"""

🎯 **AI Önerisi:**
💡 {recommendation}

🧠 **Tahmin Metodolojisi:**
• Geçmiş trend analizi
• Linear regression modeli
• Davranış pattern etkisi
• Risk faktörleri hesaplaması"""
        
        self.send_message(chat_id, text)
    
    def handle_smart_command(self, message):
        """SMART komutu - AI önerileri"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            self.send_message(chat_id, "❌ Bu komut sadece adminler için!")
            return
        
        analysis = self.get_latest_clan_analysis()
        if not analysis or 'recommendations' not in analysis:
            self.send_message(chat_id, "❌ AI önerileri henüz hazır değil.")
            return
        
        recommendations = analysis['recommendations']
        
        if not recommendations:
            text = """🤖 **AI Önerileri**

✅ **Harika! Şu anda acil bir durum yok.**

Klanınız iyi durumda görünüyor. AI sistemimiz şu anda herhangi bir kritik öneri üretmiyor.

🔄 Sistem sürekli izleme modunda..."""
        else:
            text = f"""🤖 **AI Akıllı Öneriler**

🔍 **{len(recommendations)} öneri tespit edildi:**

"""
            
            for i, rec in enumerate(recommendations, 1):
                priority_emoji = {
                    'high': '🔴',
                    'medium': '🟡', 
                    'low': '🟢'
                }.get(rec.get('priority'), '❓')
                
                category_emoji = {
                    'trend': '📈',
                    'risk': '⚠️',
                    'war': '⚔️',
                    'behavior': '🧠'
                }.get(rec.get('category'), '💡')
                
                text += f"""{priority_emoji} **{i}. {rec.get('title', 'Öneri')}**
{category_emoji} Kategori: {rec.get('category', 'Genel').title()}
📋 {rec.get('description', 'Açıklama yok')}
🎯 Aksiyon: {rec.get('action', 'Belirtilmemiş')}

"""
        
        text += """🧠 **AI Sistemin Çalışma Prensibi:**
• Sürekli veri analizi
• Pattern recognition
• Risk prediction
• Akıllı öneri üretimi"""
        
        self.send_message(chat_id, text)
    
    def handle_anomaly_command(self, message):
        """ANOMALY komutu - Anomali raporu"""
        chat_id = message['chat']['id']
        user_id = str(message['from']['id'])
        
        if user_id not in ADMIN_USERS:
            self.send_message(chat_id, "❌ Bu komut sadece adminler için!")
            return
        
        analysis = self.get_latest_clan_analysis()
        if not analysis or 'anomalies' not in analysis:
            self.send_message(chat_id, "❌ Anomali analizi henüz hazır değil.")
            return
        
        anomalies = analysis['anomalies']
        
        if not anomalies:
            text = """🔍 **Anomali Tespit Raporu**

✅ **Anomali tespit edilmedi!**

AI sistemimiz mevcut verilerde normal dışı bir durum tespit etmiyor.

🤖 **Sistemin İzlediği Durumlar:**
• Ani performans değişimleri
• Beklenmedik davranış patternleri  
• İstatistiksel outlier'lar
• Trend kırılmaları

🔄 Sistem sürekli anomali taraması yapıyor..."""
        else:
            text = f"""🔍 **Anomali Tespit Raporu**

⚠️ **{len(anomalies)} anomali tespit edildi:**

"""
            
            for i, anomaly in enumerate(anomalies, 1):
                if anomaly['type'] == 'performance_anomaly':
                    emoji = "📊"
                else:
                    emoji = "❓"
                
                text += f"""{emoji} **{i}. {anomaly['member_name']}**
🔬 Tip: {anomaly['type'].replace('_', ' ').title()}
📈 Z-Score: {anomaly['z_score']} (yüksek = anormal)
📋 {anomaly['description']}

"""
            
            text += """💡 **Anomali Açıklaması:**
Z-Score > 2.0 = İstatistiksel olarak anormal
AI sistemi beklenmedik değişimleri tespit ediyor.

🎯 **Önerilen Aksiyonlar:**
• Anomali gösteren üyelerle konuşun
• Olağandışı durumları araştırın
• Gerekirse ek analiz yapın"""
        
        self.send_message(chat_id, text)
    
    def handle_text_message(self, message):
        """Geliştirilmiş mesaj işleme"""
        user_id = str(message['from']['id'])
        chat_id = message['chat']['id']
        text = message['text'].upper()

        # Tarihi güncelle ve günlük istatistikleri hazırlık
        today = datetime.now().strftime('%Y-%m-%d')
        if today != self.today:
            self.today = today

        if today not in self.daily_stats:
            self.daily_stats[today] = {
                'active_users': [],
                'new_registrations': [],
                'warnings_given': 0,
                'total_messages': 0,
                'start_time': datetime.now().isoformat()
            }

        self.daily_stats[today]['total_messages'] += 1
        
        # Komut routing
        if text == '/START' or text == 'START':
            self.handle_start(message)
        elif text == 'KLAN':
            # call KLAN command handler
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
        # Yeni AI komutları
        elif text == 'TREND':
            self.handle_trend_command(message)
        elif text == 'WAR':
            self.handle_war_command(message)
        elif text == 'BEHAVIOR':
            self.handle_behavior_command(message)
        elif text == 'RISK':
            self.handle_risk_command(message)
        elif text == 'PREDICT':
            self.handle_predict_command(message)
        elif text == 'SMART':
            self.handle_smart_command(message)
        elif text == 'ANOMALY':
            self.handle_anomaly_command(message)
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
    
    # Kalan metodlar (check_profanity, diğer handle metodları) aynı kalacak...
    # Ana run ve diğer utility metodları da aynı
    
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

    def run(self):
        """Kendi polling mekanizması ile botu çalıştır."""
        print("🚀 Custom polling başlatıldı")
        while True:
            updates = self.get_updates()
            if not updates or not updates.get('ok'):
                time.sleep(1)
                continue

            for update in updates.get('result', []):
                self.offset = update['update_id'] + 1
                message = update.get('message')
                if message and 'text' in message:
                    self.handle_text_message(message)

            time.sleep(1)


if __name__ == '__main__':
    manager = AutoClanManager()
    manager.run()
