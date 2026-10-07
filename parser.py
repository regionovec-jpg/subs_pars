#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import urllib.error
import base64
import json
import socket
import ssl
import os
import re
import time
import concurrent.futures
import requests
from urllib.parse import urlparse, quote
from collections import Counter

# ============ ИСТОЧНИКИ ============
BLACK_SOURCES = [
    ("Gidroksi",    "https://gidroksi.fun/black-list"),
    ("Aetris",      "https://gitverse.ru/api/repos/flaafix/AetrisVPN_Black_list/raw/branch/master/configs.txt"),
    ("etoneya",     "https://etoskam.ru/other"),
    ("igareck",     "https://raw.githack.com/igareck/vpn-configs-for-russia/main/BLACK_VLESS_RUS_mobile.txt"),
    ("Diversan",    "https://raw.githubusercontent.com/Diversan313/apex-parser/main/subs/main/alive_bl.txt"),
    ("luxxuria",    "https://github.com/luxxuria/harvester/raw/refs/heads/main/non_ru.txt"),
    ("Akres",       "https://gitverse.ru/api/repos/Akres/VPN/raw/branch/master/all"),
    ("VLESSFORU",   "https://sub.vlessfo.ru/vlessforu/working_configs.txt"),
    ("RKP",         "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/blacklist.txt"),
    ("Pizduk-sub",  "https://gitverse.ru/api/repos/Pizduk/PizdukVPN/raw/branch/master/sub.txt"),
    ("LimeVPN",     "https://raw.githubusercontent.com/LimeHi/LimeVPN/refs/heads/main/blacklist.txt"),
    ("atbPars",     "https://raw.githubusercontent.com/djsigggmagg-ui/atbPars-sub/refs/heads/main/subscription.txt"),
    ("WarpGen",     "https://warp-gen.cyb-portal.org/CP-039"),
    ("BUNKER",      "https://gitverse.ru/api/repos/KOT_ANTIDOT/BUNKER/raw/branch/master/BUNKER_BLACK700.txt"),
    ("ImSketch",    "https://raw.githubusercontent.com/ImSketch1337/vless-/refs/heads/main/BLWLservers.txt"),
]

WHITE_SOURCES = [
    ("bikinitw22",  "https://gitverse.ru/api/repos/bikinitw22/apelsintel/raw/branch/main/alive_bs.txt"),
    ("Pizduk",      "https://gitverse.ru/api/repos/Pizduk/PizdukVPN/raw/branch/master/WlSubPiz.txt"),
    ("mos.ru",      "https://hub.mos.ru/kfwl/auto/raw/main/wl"),
    ("RKP-WL",      "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/whitelist.txt"),
    ("igareck-WL",  "https://raw.githack.com/igareck/vpn-configs-for-russia/main/Vless-Reality-White-Lists-Rus-Mobile.txt"),
    ("etoneya wl",  "https://etoskam.ru/whitelist"),
    ("ring-team",   "https://enc.ring-team.casa/sub/kuajs27ilzcz"),
    ("ImSketch",    "https://raw.githubusercontent.com/ImSketch1337/vless-/refs/heads/main/BLWLservers.txt"),
]

# ============ СЛОВАРЬ СТРАН ============
COUNTRY_NAMES = {
    "AD":"Andorra","AE":"UAE","AF":"Afghanistan","AG":"Antigua","AL":"Albania","AM":"Armenia",
    "AO":"Angola","AR":"Argentina","AT":"Austria","AU":"Australia","AZ":"Azerbaijan",
    "BA":"Bosnia","BB":"Barbados","BD":"Bangladesh","BE":"Belgium","BF":"Burkina Faso",
    "BG":"Bulgaria","BH":"Bahrain","BI":"Burundi","BJ":"Benin","BN":"Brunei","BO":"Bolivia",
    "BR":"Brazil","BS":"Bahamas","BT":"Bhutan","BW":"Botswana","BY":"Belarus","BZ":"Belize",
    "CA":"Canada","CD":"Congo","CF":"CAR","CG":"Congo","CH":"Switzerland","CI":"Côte d'Ivoire",
    "CL":"Chile","CM":"Cameroon","CN":"China","CO":"Colombia","CR":"Costa Rica","CU":"Cuba",
    "CV":"Cape Verde","CY":"Cyprus","CZ":"Czechia","DE":"Germany","DJ":"Djibouti","DK":"Denmark",
    "DM":"Dominica","DO":"Dominican Rep","DZ":"Algeria","EC":"Ecuador","EE":"Estonia",
    "EG":"Egypt","ER":"Eritrea","ES":"Spain","ET":"Ethiopia","FI":"Finland","FJ":"Fiji",
    "FM":"Micronesia","FR":"France","GA":"Gabon","GB":"United Kingdom","GD":"Grenada",
    "GE":"Georgia","GH":"Ghana","GM":"Gambia","GN":"Guinea","GQ":"Eq. Guinea","GR":"Greece",
    "GT":"Guatemala","GW":"Guinea-Bissau","GY":"Guyana","HK":"Hong Kong","HN":"Honduras",
    "HR":"Croatia","HT":"Haiti","HU":"Hungary","ID":"Indonesia","IE":"Ireland","IL":"Israel",
    "IN":"India","IQ":"Iraq","IR":"Iran","IS":"Iceland","IT":"Italy","JM":"Jamaica",
    "JO":"Jordan","JP":"Japan","KE":"Kenya","KG":"Kyrgyzstan","KH":"Cambodia","KI":"Kiribati",
    "KM":"Comoros","KN":"St Kitts","KP":"North Korea","KR":"South Korea","KW":"Kuwait",
    "KZ":"Kazakhstan","LA":"Laos","LB":"Lebanon","LC":"St Lucia","LI":"Liechtenstein",
    "LK":"Sri Lanka","LR":"Liberia","LS":"Lesotho","LT":"Lithuania","LU":"Luxembourg",
    "LV":"Latvia","LY":"Libya","MA":"Morocco","MC":"Monaco","MD":"Moldova","ME":"Montenegro",
    "MG":"Madagascar","MH":"Marshall Is","MK":"N. Macedonia","ML":"Mali","MM":"Myanmar",
    "MN":"Mongolia","MO":"Macao","MR":"Mauritania","MT":"Malta","MU":"Mauritius",
    "MV":"Maldives","MW":"Malawi","MX":"Mexico","MY":"Malaysia","MZ":"Mozambique",
    "NA":"Namibia","NE":"Niger","NG":"Nigeria","NI":"Nicaragua","NL":"Netherlands",
    "NO":"Norway","NP":"Nepal","NR":"Nauru","NZ":"New Zealand","OM":"Oman","PA":"Panama",
    "PE":"Peru","PG":"Papua N.G.","PH":"Philippines","PK":"Pakistan","PL":"Poland",
    "PT":"Portugal","PW":"Palau","PY":"Paraguay","QA":"Qatar","RO":"Romania","RS":"Serbia",
    "RU":"Russia","RW":"Rwanda","SA":"Saudi Arabia","SB":"Solomon Is","SC":"Seychelles",
    "SD":"Sudan","SE":"Sweden","SG":"Singapore","SI":"Slovenia","SK":"Slovakia",
    "SL":"Sierra Leone","SM":"San Marino","SN":"Senegal","SO":"Somalia","SR":"Suriname",
    "SS":"South Sudan","ST":"São Tomé","SV":"El Salvador","SY":"Syria","SZ":"Eswatini",
    "TD":"Chad","TG":"Togo","TH":"Thailand","TJ":"Tajikistan","TL":"Timor-Leste",
    "TM":"Turkmenistan","TN":"Tunisia","TO":"Tonga","TR":"Turkey","TT":"Trinidad",
    "TV":"Tuvalu","TW":"Taiwan","TZ":"Tanzania","UA":"Ukraine","UG":"Uganda","US":"USA",
    "UY":"Uruguay","UZ":"Uzbekistan","VA":"Vatican","VC":"St Vincent","VE":"Venezuela",
    "VN":"Vietnam","VU":"Vanuatu","WS":"Samoa","YE":"Yemen","ZA":"South Africa",
    "ZM":"Zambia","ZW":"Zimbabwe",
}

# ============ НАСТРОЙКИ ============
WORKERS = 120
TIMEOUT = 3

_FLAGS = {}

# ============ ПАРСИНГ ============
def parse_config(line, source_label):
    line = line.strip()
    if not line or line.startswith('#'): return None
    try:
        if line.startswith('vmess://'):
            raw = base64.b64decode(line[8:] + '=' * (-len(line[8:]) % 4)).decode('utf-8')
            cfg = json.loads(raw)
            return {'host': cfg['add'], 'port': int(cfg['port']), 'raw': line,
                    'tls': cfg.get('tls') in ('tls', 'reality'),
                    'sni': cfg.get('sni') or cfg.get('host') or cfg['add'],
                    'label': source_label, 'type': 'VMess'}
        elif line.startswith('vless://'):
            p = urlparse(line)
            q = dict(x.split('=', 1) for x in p.query.split('&') if '=' in x)
            sec = q.get('security', '')
            return {'host': p.hostname, 'port': p.port or 443, 'raw': line,
                    'tls': sec in ('tls', 'reality'),
                    'sni': q.get('sni') or p.hostname,
                    'label': source_label, 'type': 'VLESS'}
        elif line.startswith('trojan://'):
            p = urlparse(line)
            q = dict(x.split('=', 1) for x in p.query.split('&') if '=' in x)
            sec = q.get('security', '')
            return {'host': p.hostname, 'port': p.port or 443, 'raw': line,
                    'tls': sec in ('tls', 'reality'),
                    'sni': q.get('sni') or p.hostname,
                    'label': source_label, 'type': 'Trojan'}
        elif line.startswith('ss://'):
            p = urlparse(line)
            return {'host': p.hostname, 'port': p.port or 8388, 'raw': line,
                    'tls': False, 'sni': None, 'label': source_label, 'type': 'Shadowsocks'}
        elif line.startswith(('hysteria2://', 'hy2://')):
            p = urlparse(line)
            return {'host': p.hostname, 'port': p.port or 443, 'raw': line,
                    'tls': True, 'sni': p.hostname, 'label': source_label, 'type': 'Hysteria2'}
        elif line.startswith('tuic://'):
            p = urlparse(line)
            return {'host': p.hostname, 'port': p.port or 443, 'raw': line,
                    'tls': True, 'sni': p.hostname, 'label': source_label, 'type': 'TUIC'}
    except Exception:
        return None
    return None

def fetch_sub(url, retries=1):
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'ru,en;q=0.9',
                'Referer': url,
            })
            resp = urllib.request.urlopen(req, timeout=20)
            data = resp.read()

            if not data:
                return [], "Пустой ответ", "empty"

            try:
                decoded = base64.b64decode(data + b'=' * (-len(data) % 4)).decode('utf-8', errors='ignore')
                if any(p in decoded for p in ('vless://', 'vmess://', 'trojan://', 'ss://', 'hysteria2://')):
                    return decoded.splitlines(), None, None
            except Exception:
                pass

            text = data.decode('utf-8', errors='ignore')
            if any(p in text for p in ('vless://', 'vmess://', 'trojan://', 'ss://', 'hysteria2://')):
                return text.splitlines(), None, None

            head = text[:500].lower()
            if '<html' in head or '<!doctype' in head or '<body' in head:
                return [], "HTML-страница вместо подписки", "html"
            if 'proxies:' in head or 'proxy-groups:' in head or 'rules:' in head:
                return [], "YAML (Clash) — не поддерживается", "yaml"
            if 'access denied' in head or 'forbidden' in head or '403' in head:
                return [], "Доступ запрещён (403)", "forbidden"
            if 'not found' in head or '404' in head:
                return [], "Не найдено (404)", "notfound"
            if len(text.strip()) < 20:
                return [], f"Слишком короткий ответ ({len(text)} байт)", "short"

            b64_blocks = re.findall(r'[A-Za-z0-9+/=]{100,}', text)
            for block in b64_blocks:
                try:
                    dec = base64.b64decode(block + '=' * (-len(block) % 4)).decode('utf-8', errors='ignore')
                    if any(p in dec for p in ('vless://', 'vmess://', 'trojan://', 'ss://')):
                        return dec.splitlines(), None, None
                except Exception:
                    continue

            return [], f"Не распознан формат ({len(text)} байт)", "unknown"

        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries:
                print(f"   ⏳ 429, повтор через 5с...")
                time.sleep(5)
                continue
            return [], f"HTTP {e.code} {e.reason}", f"http{e.code}"
        except urllib.error.URLError as e:
            if attempt < retries and 'timed out' in str(e).lower():
                print(f"   ⏳ Timeout, повтор через 3с...")
                time.sleep(3)
                continue
            return [], f"Сеть: {e.reason}", "network"
        except Exception as e:
            return [], f"{type(e).__name__}: {e}", "error"
    return [], "Все попытки провалились", "failed"

def load_flags_batch(hosts):
    ips = [h for h in hosts if h and h.count('.') == 3 and all(p.isdigit() for p in h.split('.'))]
    if not ips: return
    print(f"\n🌍 Определение стран для {len(ips)} IP...")
    for i in range(0, len(ips), 100):
        chunk = ips[i:i+100]
        try:
            payload = json.dumps([{"query": ip} for ip in chunk]).encode()
            req = urllib.request.Request("http://ip-api.com/batch?fields=countryCode,query",
                data=payload, headers={'Content-Type': 'application/json'})
            resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
            for item in resp:
                _FLAGS[item['query']] = item.get('countryCode', '')
        except Exception as e:
            print(f"   ⚠️ Батч {i//100}: {e}")
        time.sleep(1.5)

def get_flag_and_name(host):
    code = _FLAGS.get(host, '')
    if not code or len(code) != 2: return "🌐", "Unknown"
    return chr(ord(code[0]) + 127397) + chr(ord(code[1]) + 127397), COUNTRY_NAMES.get(code, code)

def check_tls(cfg):
    try:
        start = time.time()
        if cfg['tls'] and cfg['sni']:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((cfg['host'], cfg['port']), timeout=TIMEOUT) as s:
                with ctx.wrap_socket(s, server_hostname=cfg['sni']):
                    return cfg, int((time.time() - start) * 1000)
        else:
            with socket.create_connection((cfg['host'], cfg['port']), timeout=TIMEOUT):
                return cfg, int((time.time() - start) * 1000)
    except Exception:
        return None, None

def format_line(cfg, ping):
    flag, country = get_flag_and_name(cfg['host'])
    pstr = f"{ping}ms" if ping and ping > 0 else "?ms"
    new_name = f"cool [{cfg['label']}] {flag} {country} |{pstr}|"
    raw = cfg['raw']
    if '#' in raw:
        base, _ = raw.rsplit('#', 1)
        return f"{base}#{quote(new_name)}"
    return f"{raw}#{quote(new_name)}"

# ============ ОСНОВНАЯ ЛОГИКА ============
def run_subscription(sources, remote_name, label):
    global _FLAGS
    _FLAGS = {}
    t0 = time.time()

    print(f"\n═══ {label} → {remote_name} ═══")
    print(f"⚙️  Потоки: {WORKERS} | Таймаут: {TIMEOUT}s")

    print("\n🌐 Загрузка источников...")
    all_configs = []
    type_counter = Counter()
    problems = []

    for src_label, url in sources:
        lines, error, reason = fetch_sub(url, retries=1)
        configs_from_src = []
        for line in lines:
            cfg = parse_config(line, src_label)
            if cfg:
                all_configs.append(cfg)
                configs_from_src.append(cfg)
                type_counter[cfg['type']] += 1

        if error:
            print(f"   ❌ [{src_label}] {error}")
            problems.append((src_label, error))
        elif len(configs_from_src) == 0 and reason:
            print(f"   ⚠️  [{src_label}] строк {len(lines)} — {reason}")
            problems.append((src_label, reason))
        else:
            print(f"   ✅ [{src_label}] {len(lines)} строк → {len(configs_from_src)} конфигов")

    if problems:
        print("\n⚠️  ПРОБЛЕМНЫЕ ИСТОЧНИКИ:")
        for lbl, reason in problems:
            print(f"   • {lbl:<14} → {reason}")

    print(f"\n✅ Всего конфигов к проверке: {len(all_configs)}")
    if not all_configs:
        print("⚠️ Нечего проверять")
        return

    load_flags_batch(list({c['host'] for c in all_configs}))

    print(f"\n🚀 TLS-проверка в {WORKERS} потоков...")
    working = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for i, (cfg, ping) in enumerate(ex.map(check_tls, all_configs)):
            if cfg and ping is not None:
                working.append((cfg, ping))
            if (i + 1) % 200 == 0:
                print(f"   {i+1}/{len(all_configs)} | рабочих: {len(working)}")

    print(f"\n🔥 Рабочих: {len(working)}")
    if not working:
        print("⚠️ Ничего не работает")
        return

    working.sort(key=lambda x: x[1])
    output = [format_line(c, p) for c, p in working]

    with open(remote_name, "w", encoding="utf-8") as f:
        f.write("\n".join(output))
    print(f"💾 {remote_name}: {len(output)} серверов")

    print(f"⏱️  Всего: {time.time() - t0:.1f}с")

if __name__ == "__main__":
    print("🚀 Запуск парсера подписок...")
    run_subscription(BLACK_SOURCES, "subs_bl.txt", "⚫ ЧЁРНАЯ")
    run_subscription(WHITE_SOURCES, "subs_wl.txt", "⚪ БЕЛАЯ")
    print("\n✅ Готово!")
