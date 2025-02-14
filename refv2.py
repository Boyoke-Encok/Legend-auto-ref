import requests
import time
import random
import re
import string
from colorama import Fore, init
from concurrent.futures import ThreadPoolExecutor

init(autoreset=True)

def load_proxies():
    try:
        with open("proxy.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
        return proxies
    except FileNotFoundError:
        print(Fore.RED + "proxy.txt not found.")
        return []

def get_proxy_session(proxies):
    if not proxies:
        print(Fore.YELLOW + "No proxies available. Use the default session.")
        return requests.Session()
    
    random.shuffle(proxies)  
    
    for proxy in proxies:
        session = requests.Session()
        session.proxies = {"http": proxy, "https": proxy}
        
        try:
            response = session.get("https://api.ipify.org?format=json", timeout=5)
            if response.status_code == 200:
                ip = response.json().get("ip")
                print(Fore.GREEN + f"Proxy IP: {ip}")
                return session
        except requests.RequestException:
            print(Fore.RED + f"Proxy failed: {proxy}")
    
    print(Fore.YELLOW + "All proxies fail. Use the default session.")
    return requests.Session()

def generate_random_email(session):
    username = ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 8)))
    username += str(random.randint(100, 999))
    domain = session.get("https://api.mail.tm/domains").json()["hydra:member"][0]["domain"]
    return f"{username}@{domain}"

def get_random_country():
    countries = [
        "🇺🇸 United States", "🇨🇦 Canada", "🇦🇼 Aruba", "🇦🇫 Afghanistan", "🇦🇴 Angola",
        "🇦🇮 Anguilla", "🇦🇸 Åland Islands", "🇦🇱 Albania", "🇦🇩 Andorra", "🇦🇪 United Arab Emirates",
        "🇦🇷 Argentina", "🇦🇲 Armenia", "🇦🇸 American Samoa", "🇦🇶 Antarctica", "🇹🇰 French Southern and Antarctic Lands",
        "🇦🇬 Antigua and Barbuda", "🇦🇺 Australia", "🇦🇹 Austria", "🇦🇿 Azerbaijan"
    ]
    return random.choice(countries)

def get_random_name():
    first_names = [
        "Liam", "Noah", "Oliver", "Elijah", "James", "William", "Benjamin", "Lucas", "Henry", "Alexander",
        "Mason", "Michael", "Ethan", "Daniel", "Jacob", "Logan", "Jackson", "Sebastian", "Aiden", "Matthew",
        "David", "Joseph", "Carter", "Owen", "Wyatt", "John", "Jack", "Luke", "Julian", "Levi",
        "Isaac", "Gabriel", "Mateo", "Samuel", "David", "Anthony", "Jaxon", "Christopher", "Andrew", "Lincoln",
        "Joshua", "Isaiah", "Charles", "Thomas", "Eli", "Aaron", "Ryan", "Nathan", "Adrian", "Christian",
        "Colton", "Landon", "Jonathan", "Parker", "Asher", "Cameron", "Jeremiah", "Ezekiel", "Angel", "Robert",
        "Austin", "Gavin", "Chase", "Xavier", "Jace", "Dominic", "Tyler", "Zachary", "Cody", "Kevin",
        "Brayden", "Adam", "Jason", "Brody", "Zane", "Kai", "Hayden", "Silas", "Kaden", "Ryder",
        "Diego", "Jax", "Kylan", "Emmett", "Harrison", "Jett", "Dalton", "Nolan", "Santiago", "Brandon",
        "Kameron", "Maverick", "Tucker", "Tristan", "Wesley", "Riley", "Zander", "Sawyer", "Jasper", "Kellan"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
        "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
        "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
        "Green", "AdAMS", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
        "Gonzales", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Edwards", "Collins", "Stewart", "Sanchez",
        "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell", "Murphy", "Bailey", "Rivera", "Cooper",
        "Richardson", "Cox", "Howard", "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James", "Watson",
        "Brooks", "Kelly", "Sanders", "Price", "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman",
        "Jenkins", "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington", "Butler", "Simmons"
    ]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    return first_name, last_name

def get_referred_by():
    try:
        with open("ref.txt", "r") as file:
            return file.readline().strip()
    except FileNotFoundError:
        return ""

def create_account(session):
    try:
        email = generate_random_email(session)
        password = "Password123!"
        
        payload = {"address": email, "password": password}
        response = session.post("https://api.mail.tm/accounts", json=payload, timeout=10)

        if response.status_code == 201:
            print(Fore.CYAN + f"Account created: {email}")
            return email, password
        else:
            print(Fore.RED + f"Failed to create an account (Status {response.status_code}): {response.text}")
            return None, None
    except requests.RequestException:
        print(Fore.RED + "Proxy Disconnected when creating an account.")
        return None, None

def post_to_waitlist(session, email):
    try:
        country = get_random_country()
        referred_by = get_referred_by()
        first_name, last_name = get_random_name()
        
        payload = {
            "country": country,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "referred_by": referred_by
        }
        
        response = session.post("https://api.legend.xyz/waitlist", json=payload, timeout=10)
        if response.status_code == 201:
            print(Fore.GREEN + f"Successfully signed up to waitlist: {first_name} {last_name}")
        else:
            print(Fore.RED + "Failed to register to waitlist:", response.json())
    except requests.RequestException:
        print(Fore.RED + "Proxy Disconnected when registering to waitlist.")

def get_token(session, email, password):
    try:
        response = session.post("https://api.mail.tm/token", json={"address": email, "password": password}, timeout=10)
        if response.status_code == 200:
            return response.json()["token"]
        else:
            print(Fore.RED + "Failed to get tokens:", response.json())
            return None
    except requests.RequestException:
        print(Fore.RED + "Proxy terminated when getting an email token.")
        return None

def get_email_content(session, token, message_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = session.get(f"https://api.mail.tm/messages/{message_id}", headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json().get("text") or response.json().get("html") or ""
        return ""
    
    except requests.RequestException:
        print(Fore.RED + "Proxy Disconnected while retrieving email content.")
        return ""

def get_inbox_messages(session, token):
    headers = {"Authorization": f"Bearer {token}"}
    
    for _ in range(15):
        try:
            response = session.get("https://api.mail.tm/messages", headers=headers, timeout=10)
            
            if response.status_code == 200:
                messages = response.json().get("hydra:member", [])
                if messages:
                    latest_message = messages[0]
                    print(Fore.YELLOW + f"Email from: {latest_message['from']['address']}, Content: {latest_message['subject']}")
                    return latest_message["id"], get_email_content(session, token, latest_message["id"])
            
            time.sleep(1)
        
        except requests.RequestException:
            print(Fore.RED + "Proxy Disconnected while retrieving email inbox.")
            return None, None
    
    print(Fore.YELLOW + "No incoming emails after 15 seconds.")
    return None, None

def extract_verification_token(email_text):
    if email_text:
        match = re.search(r'https://legend\.xyz/waitlist_confirmation\?confirmation_token=([\w\-._]+)', email_text)
        if match:
            return match.group(1)
    return None

def verify_email(session, token):
    if token:
        try:
            url = "https://api.legend.xyz/waitlist/confirm"
            response = session.post(url, json={"token": token}, timeout=10)

            if response.status_code == 200:
                print(Fore.GREEN + "The email was successfully verified.")
                return True
            else:
                print(Fore.RED + "Email verification failed:", response.text)
                return False

        except requests.RequestException:
            print(Fore.RED + "Proxy Disconnected during email verification.")
            return False

    return False

def check_latest_email(session, email, password):
    token = get_token(session, email, password)
    if not token:
        print(Fore.RED + "next referral...\n")
        return
    
    message_id, email_text = get_inbox_messages(session, token)
    if not message_id or not email_text:
        print(Fore.YELLOW + "next referral...\n")
        return
    
    verification_token = extract_verification_token(email_text)
    if verification_token:
        verify_email(session, verification_token)

def process_referral(i, proxies):
    print(Fore.BLUE + f"Register account {i+1}...\n")
    
    session = get_proxy_session(proxies)
    
    email, password = create_account(session)
    if not email or not password:
        print(Fore.YELLOW + "Continue to the next referral...")
        return  # Skip to the next referral
    
    post_to_waitlist(session, email)
    check_latest_email(session, email, password)

def main():
    try:
        print(Fore.YELLOW + "BOT INI DI KEMBANGKAN OLEH BOYOKE ENCOK")
        referral_count = int(input(Fore.BLUE + "Mau berapa ref? "))
    except ValueError:
        print(Fore.RED + "Enter a valid number!")
        return

    proxies = load_proxies()

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {executor.submit(process_referral, i, proxies): i for i in range(referral_count)}
        
        for future in futures:
            try:
                future.result()  # Wait for the thread to finish
            except Exception as e:
                print(Fore.RED + f"Error processing referral {futures[future]}: {e}")

if __name__ == "__main__":
    main()