import requests
import time
import sys

# URL API untuk mendapatkan informasi akun dan menyelesaikan tugas
get_info_url = "https://api.agent301.org/getMe"
complete_task_url = "https://api.agent301.org/completeTask"

# Membaca daftar token otorisasi dari file accounts.txt
def read_tokens_from_file(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Fungsi untuk menampilkan efek loading dan "Done" dengan nomor yang berubah dalam satu baris
def loading_animation_with_counter(task_title, counter):
    print(f"\r- {task_title} Processing {task_title}... Done {counter}", end="")
    sys.stdout.flush()  # Memastikan output ditampilkan secara langsung

# Fungsi untuk mendapatkan informasi akun
def get_account_info(authorization_token):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": authorization_token,
        "content-type": "application/json",
        "Referer": "https://telegram.agent301.org/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }
    
    payload_info = {
        "referrer_id": 0
    }
    
    response = requests.post(get_info_url, headers=headers, json=payload_info)
    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            result = data['result']
            account_name = result.get('username', 'Unknown')  # Mendapatkan nama akun
            print(f"\n=== Account Summary for {account_name} ===")  # Tampilkan nama akun
            print(f"Balance: {result['balance']}")
            print(f"Tickets: {result['tickets']}")
            print("\nEnrollments:")
            for key, value in result['enrollments'].items():
                print(f"  {key.capitalize()}: {value}")

            print("\nTasks:")
            tasks = result['tasks']
            # Periksa apakah semua tugas sudah diklaim
            all_tasks_claimed = all(task['is_claimed'] for task in tasks)

            if all_tasks_claimed:
                print("Semua task sudah dikerjakan")
            else:
                for task in tasks:
                    task_title = task['title']
                    task_reward = task['reward']
                    task_claimed = "Yes" if task['is_claimed'] else "No"

                    # Tampilkan hanya tugas yang belum diklaim
                    if not task['is_claimed']:
                        print(f"- {task_title} (Reward: {task_reward})", end="")
                        complete_task(headers, task['type'])
                        print()  # Baris baru setelah setiap tugas
        else:
            print("Failed to fetch account info.")
    else:
        print(f"Error: {response.status_code}")

# Fungsi untuk mengecek apakah tugas tertentu sudah diklaim
def check_task_claimed(headers, task_title_to_check):
    payload_info = {"referrer_id": 0}
    response = requests.post(get_info_url, headers=headers, json=payload_info)
    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            tasks = data['result']['tasks']
            for task in tasks:
                if task['title'] == task_title_to_check:
                    return task['is_claimed']
    return False

# Fungsi untuk menyelesaikan tugas tanpa mencetak hasil
def complete_task(headers, task_type):
    payload = {"type": task_type}
    response = requests.post(complete_task_url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        if data.get('ok'):
            return True
        else:
            print(f"  Failed to complete task '{task_type}'. Response: {data}")
    else:
        print(f"  Error completing task '{task_type}': {response.status_code}")
    return False

# Fungsi utama untuk menjalankan tugas harian untuk semua akun
def daily_login_for_all_accounts():
    tokens = read_tokens_from_file('accounts.txt')
    num_accounts = len(tokens)  # Hitung jumlah akun dari jumlah token
    print(f"Processing {num_accounts} accounts...")  # Tampilkan jumlah akun yang akan diproses

    # Proses setiap akun
    for token in tokens:
        get_account_info(token)
        print("=" * 40)  # Pemisah antara akun

# Menjalankan skrip setiap 24 jam sekali
while True:
    print("Starting daily login for all accounts...")
    daily_login_for_all_accounts()
    print("Completed daily login for all accounts. Waiting for 24 hours...")
    time.sleep(86400)  # Menunggu selama 24 jam (86.400 detik)
