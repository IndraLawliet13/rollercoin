# bot_allinone.py
import requests
import time
import sys
import os
import json
import math
from datetime import datetime, timezone, timedelta
JKT_TZ = timezone(timedelta(hours=7))

LOG_FILE = 'activity_log.json'

def _now_jkt():
    return datetime.now(JKT_TZ).strftime('%Y-%m-%d %H:%M:%S %z')

def _init_log():
    base = {
        "meta": {"version": 1, "tz": "Asia/Jakarta"},
        "task": [],
        "spin_wheel": [],
        "upgrade": [],
        "buy": [],
        "daily_claim": [],
        "boost": [] 
    }
    try:
        if not os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                json.dump(base, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def log_activity(kind, payload):
    try:
        _init_log()
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if kind not in data:
            data[kind] = []
        data[kind].append({
            "ts": _now_jkt(),
            "payload": payload
        })
        with open(LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️ Log write failed: {e}")

try:
    from colorama import init, Fore, Style
except Exception:
    class _Dummy: __getattr__ = lambda *a, **k: ''
    Fore = Style = _Dummy()
    def init(*a, **k): pass
init(autoreset=True, strip=not sys.stdout.isatty())


try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
EMOJI_OK = ('UTF-8' in (getattr(sys.stdout, 'encoding', '') or '').upper()) and (os.environ.get('NO_EMOJI') != '1')
_EMOJI_REPL = {'🚀':'[*]','🔋':'[PWR]','⚠️':'[!]','👤':'[USR]','💰':'[$]','⛏️':'[MINE]','⚡':'[EN]','✨':'[+]','🔍':'[?]','🎡':'[WHEEL]','🤖':'[BOT]','📈':'[UP]','🛒':'[BUY]','✅':'[OK]','⏳':'[WAIT]'}
_FANCY_REPL = {'—':'-','–':'-','…':'...','\u200b':'','\ufe0f':''}
import builtins as _builtins
_print_orig = _builtins.print
def print(*args, **kwargs):
    if EMOJI_OK:
        return _print_orig(*args, **kwargs)
    norm = []
    for a in args:
        if isinstance(a, str):
            for k, v in _EMOJI_REPL.items():
                a = a.replace(k, v)
            for k, v in _FANCY_REPL.items():
                a = a.replace(k, v)
        norm.append(a)
    return _print_orig(*norm, **kwargs)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def load_token():
    env_token = os.environ.get('ROLLERCOIN_BEARER_TOKEN', '').strip()
    if env_token:
        return env_token
    try:
        with open('token.txt', 'r') as f:
            token = f.read().strip()
            if not token:
                print(f"{Fore.RED}{Style.BRIGHT}Error: token.txt is empty. Please paste your token into the file or set ROLLERCOIN_BEARER_TOKEN.")
                sys.exit()
            return token
    except FileNotFoundError:
        print(f"{Fore.RED}{Style.BRIGHT}Error: token.txt not found! Create token.txt or set ROLLERCOIN_BEARER_TOKEN.")
        sys.exit()


def print_animated_timer(seconds):
    for i in range(seconds, -1, -1):
        minutes, secs = divmod(i, 60)
        timer_str = f"{Fore.CYAN}⏳ Next cycle in {minutes:02d}:{secs:02d}"
        sys.stdout.write(f"\r{timer_str}")
        sys.stdout.flush()
        time.sleep(1)
    print()


class RollerTapBot:
    def __init__(self, token):
        self.base_url = "https://tapp.rlr.app/api"
        self.session = requests.Session()
        self.token = token
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0"
        })

    def _make_request(self, method, endpoint, json_payload=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, timeout=15)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=json_payload, timeout=15)
            else:
                return None
            if not response.content:
                return None
            data = response.json()
            if data.get("success"):
                return data.get("data")
            else:
                print(f"{Fore.RED}⚠️ Request to {endpoint} failed: {data.get('error', 'Unknown error')}")
                if "invalid token" in data.get('error', '').lower() or "unauthorized" in data.get('error', '').lower():
                    print(f"{Fore.RED}{Style.BRIGHT}🔥 TOKEN EXPIRED! Please update token.txt or ROLLERCOIN_BEARER_TOKEN.")
                    sys.exit()
                return None
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}❌ Connection Error: {e}")
            return None
        except requests.exceptions.JSONDecodeError:
            print(f"{Fore.RED}❌ Failed to parse JSON from {endpoint}.")
            return None

    def get_user_data(self): return self._make_request('GET', '/auth/user-data')
    def get_balance(self): return self._make_request('GET', '/game/balance')
    def collect_taps(self, taps_count): return self._make_request('POST', '/game/collect-token', json_payload={"tapsCount": taps_count})
    def get_tasks(self):
        data = self._make_request('GET', '/game/quests/get-quests')
        return data.get('quests', []) if data else []
    def claim_task(self, quest_id): return self._make_request('POST', '/game/quests/claim-task', json_payload={"questId": quest_id})
    def get_shop_miners(self):
        data = self._make_request('GET', '/game/market-offers?categoryCode=miners')
        return data.get('items', []) if data else []
    def get_my_miners(self):
        data = self._make_request('GET', '/game/user-miners-list?type=basic')
        return data.get('items', []) if data else []
    def buy_or_upgrade_miner(self, offer_id): return self._make_request('POST', '/game/purchase-market-offer', json_payload={"offerID": offer_id, "quantity": 1})
    def check_wheel(self): return self._make_request('GET', '/wheel/balance')
    def spin_wheel(self, wof_id): return self._make_request('POST', '/wheel/spin', json_payload={"wheelOfFortuneID": wof_id})
    def recharge_energy(self): return self._make_request('POST', '/game/recharge-energy')
    def collect_daily_reward(self): return self._make_request('POST', '/game/collect-daily-reward')
    def purchase_tap_level(self): return self._make_request('POST', '/game/purchase-tap-level')
    def purchase_energy_level(self): return self._make_request('POST', '/game/purchase-energy-level')


if not os.path.exists('config.json'):
    default_config = {
        "RESERVE_MODE": "auto_topk_payback",
        "RESERVE_MANUAL_AMOUNT": 500000,
        "AUTO_TOPK_K": 3,
        "ROI_HOURS_THRESHOLD": 72.0,
        "RESERVE_SAFETY_FACTOR": 1.0,
        "BOOST_ENABLED": False,
        "BOOST_MIN_BALANCE_FACTOR": 1.0,
        "MULTI_BUY": True,
        "MAX_ACTIONS_PER_CYCLE": 5,
        "RECOMPUTE_BETWEEN_PURCHASES": True,
        "SLEEP_SECONDS": 300
    }
    CONFIG = default_config
    try:
        with open('config.json', 'w') as f:
            json.dump(default_config, f, indent=2)
            print(f"{Fore.YELLOW}⚠️ config.json not found. A default config file has been created. Please review and adjust settings as needed.")
            time.sleep(3)
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to create default config.json: {e}")
        sys.exit()
else:
    try:
        with open('config.json', 'r') as f:
            CONFIG = json.load(f)
    except Exception as e:
        print(f"{Fore.RED}❌ Failed to load config.json: {e}")
        sys.exit()



RESERVE_MODE = os.environ.get('RESERVE_MODE', CONFIG['RESERVE_MODE'])
RESERVE_MANUAL_AMOUNT = int(os.environ.get('RESERVE_MANUAL_AMOUNT', CONFIG['RESERVE_MANUAL_AMOUNT']))
AUTO_TOPK_K = int(os.environ.get('AUTO_TOPK_K', CONFIG['AUTO_TOPK_K']))
ROI_HOURS_THRESHOLD = float(os.environ.get('ROI_HOURS_THRESHOLD', CONFIG['ROI_HOURS_THRESHOLD']))
RESERVE_SAFETY_FACTOR = float(os.environ.get('RESERVE_SAFETY_FACTOR', CONFIG['RESERVE_SAFETY_FACTOR']))
MULTI_BUY = (os.environ.get('MULTI_BUY', str(CONFIG['MULTI_BUY'])).lower() in ['1','true','yes'])
BOOST_ENABLED = (os.environ.get('BOOST_ENABLED', str(CONFIG.get('BOOST_ENABLED', False))).lower() in ['1','true','yes'])
BOOST_MIN_BALANCE_FACTOR = float(os.environ.get('BOOST_MIN_BALANCE_FACTOR', CONFIG.get('BOOST_MIN_BALANCE_FACTOR', 1.0)))
MAX_ACTIONS_PER_CYCLE = int(os.environ.get('MAX_ACTIONS_PER_CYCLE', CONFIG['MAX_ACTIONS_PER_CYCLE']))
RECOMPUTE_BETWEEN_PURCHASES = (os.environ.get('RECOMPUTE_BETWEEN_PURCHASES', str(CONFIG['RECOMPUTE_BETWEEN_PURCHASES'])).lower() in ['1','true','yes'])
SLEEP_SECONDS = int(os.environ.get('SLEEP_SECONDS', CONFIG['SLEEP_SECONDS']))
AUTO_BUY_ENABLED = (
    os.environ.get('AUTO_BUY_ENABLED', str(CONFIG.get('AUTO_BUY_ENABLED', True)))
    .lower() in ['1', 'true', 'yes']
)


def build_candidates(shop_miners, my_miners):
    potential_actions = []
    if shop_miners:
        for miner in shop_miners:
            if miner.get('userCount', 1) == 0:
                price = miner.get('priceInfo', {}).get('price', 0)
                income = miner.get('item', {}).get('miningCoinsPerHour', 0)
                reffCount = miner.get('referralsCount', 0)
                reffUnblock = miner.get('referralsCountToUnblock', 0)
                if price > 0 and income > 0 and reffCount >= reffUnblock:
                    payback_h = price / income
                    potential_actions.append({'type': 'New Purchase','id': miner['id'],'title': miner.get('title','Unknown'),'price': price,'payback_hours': payback_h,'payback_days': payback_h/24.0,'roi': payback_h})
    if my_miners:
        for miner in my_miners:
            offer = miner.get('upgradeOffer')
            if offer:
                price = offer.get('priceInfo', {}).get('price', 0)
                current_income = miner.get('miningCoinsPerHour', 0)
                new_income = offer.get('item', {}).get('miningCoinsPerHour', 0)
                inc = new_income - current_income
                if price > 0 and inc > 0:
                    payback_h = price / inc
                    potential_actions.append({'type': 'Upgrade','id': offer['id'],'title': offer.get('title','Upgrade'),'price': price,'payback_hours': payback_h,'payback_days': payback_h/24.0,'roi': payback_h})
    return potential_actions


def compute_reserve(potential_actions, shop_miners):
    reserve_balance = RESERVE_MANUAL_AMOUNT
    try:
        if RESERVE_MODE == 'auto_max_unlocked':
            max_price = 0
            for miner in (shop_miners or []):
                if miner.get('itemType') == 'miners' and miner.get('priceInfo', {}).get('price'):
                    price = miner['priceInfo']['price']
                    userCount = miner.get('userCount', 0)
                    reffCount = miner.get('referralsCount', 0)
                    reffUnblock = miner.get('referralsCountToUnblock', 0)
                    if userCount == 0 and reffCount >= reffUnblock:
                        if price > max_price: max_price = price
            if max_price > 0:
                reserve_balance = int(max_price * RESERVE_SAFETY_FACTOR)
        elif RESERVE_MODE == 'auto_topk_payback':
            good = [a for a in potential_actions if a.get('payback_hours', 1e18) <= ROI_HOURS_THRESHOLD]
            good.sort(key=lambda x: (x.get('payback_hours', 1e18), -x.get('price', 0)))
            good = good[:max(1, AUTO_TOPK_K)]
            if good:
                reserve_balance = int(max(a.get('price', 0) for a in good) * RESERVE_SAFETY_FACTOR)
    except Exception:
        pass
    return reserve_balance

def choose_best_action(potential_actions):
    """
    Pilih 1 aksi terbaik berdasarkan payback_hours.
    - Kalau ROI_HOURS_THRESHOLD > 0 dan ada yang payback <= threshold,
      pakai hanya yang itu.
    - Kalau tidak ada yang lolos, tetap pilih yang payback paling kecil
      dari semua kandidat (biar tetap beli, nggak ke-skip semua).
    """
    if not potential_actions:
        return None

    # Soft filter dengan ROI cap (kalau mau)
    candidates = potential_actions
    if ROI_HOURS_THRESHOLD > 0:
        filtered = [
            a for a in potential_actions
            if a.get('payback_hours', a.get('roi', 1e18)) <= ROI_HOURS_THRESHOLD
        ]
        if filtered:
            candidates = filtered  # kalau ada yang di bawah threshold, pakai itu saja

    # Sort by payback_hours (paling cepet balik modal)
    candidates.sort(key=lambda x: x.get('payback_hours', x.get('roi', 1e18)))
    return candidates[0]



def main():
    auth_token = load_token()
    bot = RollerTapBot(auth_token)
    cycle_idx = 0
    cycles_per_day = max(1, math.ceil(86400 / SLEEP_SECONDS))
    next_daily_claim_cycle = 0

    while True:
        clear_screen()
        print(f"\n{Style.BRIGHT}{Fore.YELLOW}" + "="*50)
        print(f"🚀 Starting new cycle at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)

        user_data = bot.get_user_data()
        balance_data = bot.get_balance()
        if not user_data or not balance_data:
            print(f"{Fore.RED}Failed to fetch initial data, retrying later.")
            print_animated_timer(SLEEP_SECONDS); continue

        balance = balance_data.get('balance', 0)
        game_profile = user_data.get('gameProfile', {})
        user_name = user_data.get('userInfo', {}).get('fullName', 'Unknown')
        passive_income = game_profile.get('passiveIncomePerHour', 0)
        print(f"{Fore.WHITE}👤 User: {user_name}")
        print(f"{Fore.GREEN}💰 Current Balance: {balance:,} RCC")
        print(f"{Fore.GREEN}⛏️  Passive Income: {passive_income:,} RCC/hr")

        # === Daily Claim ===
        try:
            if cycle_idx >= next_daily_claim_cycle:
                print(f"\n{Fore.MAGENTA}🎁 Trying daily reward claim...")
                dr = bot.collect_daily_reward()
                if dr:  # success => _make_request return 'data' saat success=true
                    reward = (dr or {}).get('reward', {})
                    amount = reward.get('rewardAmount', 0)
                    day_no = reward.get('dayNumber')
                    # Update balance jika server kirim
                    balance = dr.get('balance', balance)
                    print(f"{Fore.GREEN}✅ Daily claim success: +{amount:,} RCC (Day {day_no})")
                    log_activity("daily_claim", {
                        "status": "success",
                        "amount": amount,
                        "dayNumber": day_no,
                        "balance_after": balance
                    })
                    next_daily_claim_cycle = cycle_idx + cycles_per_day
                    approx_minutes = (cycles_per_day * SLEEP_SECONDS) // 60
                    print(f"{Fore.CYAN}📅 Next daily-claim scheduled ~{cycles_per_day} cycles (~{approx_minutes} min)")
                else:
                    # Gagal (mis. "already been claimed") -> coba lagi 4 cycle
                    next_daily_claim_cycle = cycle_idx + 4
                    approx_minutes = (4 * SLEEP_SECONDS) // 60
                    print(f"{Fore.YELLOW}⏭️ Daily claim failed; will retry in 4 cycles (~{approx_minutes} min)")
            else:
                remaining = max(0, next_daily_claim_cycle - cycle_idx)
                approx_minutes = (remaining * SLEEP_SECONDS) // 60
                print(f"\n{Fore.WHITE}🎁 Daily claim: next attempt in {remaining} cycles (~{approx_minutes} min)")
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Daily claim block error: {e}")


        # Recharge & taps
        print(f"\n{Fore.MAGENTA}🔋 Mencoba recharge energy...")
        recharge_result = bot.recharge_energy()
        if recharge_result and 'activeEnergyCount' in recharge_result:
            print(f"{Fore.GREEN}⚡ Energy recharged! New energy count: {recharge_result['activeEnergyCount']}")
        # Use latest energy value if available after recharge
        energy = (recharge_result.get('activeEnergyCount')
                  if (recharge_result and 'activeEnergyCount' in recharge_result)
                  else game_profile.get('activeEnergyCount', 0))
        if energy > 0:
            max_taps = energy
            print(f"{Fore.BLUE}⚡ Energy available: {max_taps}. Sending {max_taps} max taps...")
            collect_result = bot.collect_taps(max_taps)
            if collect_result and 'balance' in collect_result:
                print(f"{Fore.GREEN}✨ Coins collected! New balance: {collect_result['balance']:,} RCC")
                balance = collect_result['balance']
        else:
            print(f"{Fore.YELLOW}⚡ No energy to tap.")

        # Claim tasks
        print(f"\n{Fore.MAGENTA}🔍 Checking for claimable tasks...")
        tasks = bot.get_tasks()
        claimed_count = 0
        if tasks:
            for task in tasks:
                if task.get('progress', 0) > 0 and not task.get('isClaimed'):
                    title = task.get('title',{}).get('en') or task.get('title',{}).get('ru') or task.get('title',{}).get('id') or 'Task'
                    print(f"{Fore.WHITE}✅ Found task: {title}. Attempting to claim...")
                    claim_result = bot.claim_task(task['id'])
                    if claim_result:
                        reward = claim_result.get('reward', {})
                        reward_amount = reward.get('rewardAmount', 0)
                        print(f"{Fore.GREEN}🎉 Successfully claimed {reward_amount:,} RCC!")
                        log_activity("task", {
                            "task_id": task['id'],
                            "title": title,
                            "reward_amount": reward_amount
                        })
                        claimed_count += 1
                        time.sleep(1.5)
        if claimed_count == 0:
            print(f"{Fore.YELLOW}No new tasks to claim.")
            
            
        # Wheel of Fortune
        print(f"\n{Fore.MAGENTA}🎡 Checking Wheel of Fortune...")
        wheel_data = bot.check_wheel()

        if not wheel_data:
            print(f"{Fore.YELLOW}🎡 Failed to fetch wheel data.")
        else:
            balances = wheel_data.get('balances', []) or []

            # === FREE SPIN ===
            # Pakai hanya flag isFreeSpinAvailable, JANGAN percaya amount di tiket free
            if wheel_data.get('isFreeSpinAvailable'):
                free_ticket = next(
                    (t for t in balances if t.get('type') == 'free'),
                    None
                )
                if free_ticket:
                    print(f"{Fore.CYAN}🎡 Free spin available, spinning...")
                    reward = bot.spin_wheel(free_ticket['wofID'])
                    if reward:
                        won_amt = reward.get('amount')
                        won_typ = reward.get('type')
                        won_cur = reward.get('currency')

                        log_activity("spin_wheel", {
                            "wof_id": free_ticket['wofID'],
                            "amount": won_amt,
                            "type": won_typ,
                            "currency": won_cur,
                            "ticket_kind": "free"
                        })

                        print(f"{Fore.GREEN}🎉 Free spin reward: {won_amt:,} {won_cur} ({won_typ})")

                        # refresh balance setelah spin
                        bal_data = bot.get_balance()
                        if bal_data and 'balance' in bal_data:
                            balance = bal_data['balance']
                            print(f"{Fore.GREEN}💰 New balance: {balance:,} RCC")
                    else:
                        print(f"{Fore.RED}❌ Failed to spin free wheel.")
                else:
                    print(f"{Fore.YELLOW}🎡 isFreeSpinAvailable = true, but no free ticket found in balances.")
            else:
                print(f"{Fore.YELLOW}🎡 No free spin available at this time.")

            # === PAID TICKET SPIN ===
            # Fokus utama: kalau ada paid ticket, spin sekali per cycle
            paid_ticket = next(
                (t for t in balances
                 if t.get('type') == 'paid' and t.get('amount', 0) > 0),
                None
            )

            if paid_ticket:
                print(
                    f"{Fore.CYAN}🎡 Paid tickets detected: {paid_ticket.get('amount', 0)}. "
                    f"Spinning once with paid ticket..."
                )

                # Simpan balance sebelum spin
                balance_before_spin = balance

                reward = bot.spin_wheel(paid_ticket['wofID'])
                if reward:
                    # Setelah spin, ambil balance terbaru
                    bal_data = bot.get_balance()
                    if bal_data and 'balance' in bal_data:
                        new_balance = bal_data['balance']
                        gained = max(0, new_balance - balance_before_spin)
                        balance = new_balance

                        won_typ = reward.get('type')
                        won_cur = reward.get('currency')

                        log_activity("spin_wheel", {
                            "wof_id": paid_ticket['wofID'],
                            "amount_raw": reward.get('amount'),
                            "amount_effective": gained,
                            "type": won_typ,
                            "currency": won_cur,
                            "ticket_kind": "paid"
                        })

                        print(
                            f"{Fore.GREEN}🎉 Paid spin reward (effective): {gained:,} RCC "
                            f"(raw: {reward.get('amount')} {won_cur}, {won_typ})"
                        )
                        print(f"{Fore.GREEN}💰 New balance: {balance:,} RCC")
                    else:
                        print(f"{Fore.YELLOW}⚠️ Spin done, but failed to refresh balance.")
                else:
                    print(f"{Fore.RED}❌ Failed to spin paid ticket.")
            else:
                print(f"{Fore.YELLOW}🎡 No paid tickets available right now.")
        time.sleep(3)
        

        # === Boost Upgrades (gated) ===
        # Default OFF; if ON: only if balance >= reserve*factor AND there is no miner candidate under ROI cap
        if BOOST_ENABLED:
            try:
                _my_miners   = bot.get_my_miners()
                _shop_miners = bot.get_shop_miners()
                _actions = build_candidates(_shop_miners, _my_miners)
                _reserve = compute_reserve(_actions, _shop_miners)
                _has_good = any(a.get('payback_hours', a.get('roi', 1e18)) <= ROI_HOURS_THRESHOLD for a in _actions)
                if balance >= int(_reserve * BOOST_MIN_BALANCE_FACTOR) and not _has_good:
                    # 1) Tap boost
                    tap_res = bot.purchase_tap_level()
                    if tap_res and 'balance' in tap_res:
                        balance = tap_res['balance']
                        print(f"{Fore.GREEN}📈 Tap boost upgraded! New balance: {balance:,} RCC")
                        log_activity("boost", {"kind": "tap", "balance_after": balance})
                    # 2) Energy boost
                    energy_res = bot.purchase_energy_level()
                    if energy_res and 'balance' in energy_res:
                        balance = energy_res['balance']
                        print(f"{Fore.GREEN}🔋 Energy boost upgraded! New balance: {balance:,} RCC")
                        log_activity("boost", {"kind": "energy", "balance_after": balance})
                else:
                    print(f"{Fore.YELLOW}⏭️ Boost skipped (gated).")
            except Exception:
                pass

                # Purchase strategy (simple: ambil 1 kartu terbaik saja)
        print(f"\n{Fore.MAGENTA}🤖 Running purchase & upgrade strategy...")

        if not AUTO_BUY_ENABLED:
            print(f"{Fore.YELLOW}🛑 Auto buy/upgrade disabled (AUTO_BUY_ENABLED = false).")
        else:
            my_miners   = bot.get_my_miners()
            shop_miners = bot.get_shop_miners()
            potential_actions = build_candidates(shop_miners, my_miners)

            if potential_actions:
                # simpan ke file untuk debug
                try:
                    with open('potential_actions.json', 'w') as f:
                        json.dump(potential_actions, f, indent=2)
                except Exception:
                    pass

                reserve_balance = compute_reserve(potential_actions, shop_miners)
                print(f"🧮 Reserve mode: {RESERVE_MODE}; reserve = {reserve_balance:,} RCC")

                if balance < reserve_balance:
                    print(
                        f"🧯 Purchase gated: balance {balance:,} RCC < reserve {reserve_balance:,} RCC. "
                        f"Skipping purchases this cycle."
                    )
                else:
                    best = choose_best_action(potential_actions)
                    if not best:
                        print(f"{Fore.YELLOW}🚧 No candidate actions found.")
                    else:
                        print(
                            f"📈 Best candidate: {best['type']} '{best['title']}' | "
                            f"Price: {best['price']:,} RCC | "
                            f"Payback: {best['payback_hours']:.2f} jam "
                            f"(~{best['payback_days']:.2f} hari)"
                        )

                        if balance < best['price']:
                            print(f"{Fore.YELLOW}💸 Not enough balance to buy best candidate.")
                        else:
                            print(f"{Fore.CYAN}🛒 Executing best action...")
                            result = bot.buy_or_upgrade_miner(best['id'])
                            if result:
                                new_balance = result.get('balance', balance - best['price'])
                                balance = new_balance
                                print(f"{Fore.GREEN}✅ Action successful! New balance: {balance:,} RCC")

                                if best['type'].lower().startswith('new'):
                                    log_activity("buy", {
                                        "offer_id": best['id'],
                                        "title": best['title'],
                                        "price": best['price'],
                                        "payback_hours": best['payback_hours'],
                                        "payback_days": best['payback_days']
                                    })
                                else:
                                    log_activity("upgrade", {
                                        "offer_id": best['id'],
                                        "title": best['title'],
                                        "price": best['price'],
                                        "payback_hours": best['payback_hours'],
                                        "payback_days": best['payback_days']
                                    })
            else:
                print(f"{Fore.YELLOW}No purchase or upgrade actions available.")

        cycle_idx += 1
        print_animated_timer(SLEEP_SECONDS)


if __name__ == '__main__':
    main()
