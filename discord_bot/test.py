import random
import string
from faker import Faker

fake = Faker()

def generate_random_username():
    options = [
        lambda: fake.first_name().lower(),
        lambda: fake.last_name().lower(),
        lambda: fake.word(),
        lambda: fake.color_name(),
    ]
    return random.choice(options)()

def generate_random_time():
    hour = random.randint(6, 17)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}"

unique_entries = set()
while len(unique_entries) < 50:
    first_name = fake.first_name()
    last_name = fake.last_name()
    username = generate_random_username()
    id_number = ''.join(random.choices(string.digits, k=18))
    military_time = generate_random_time()
    unique_entries.add((first_name, last_name, username, id_number, military_time))

entries_list = list(unique_entries)
for entry in entries_list:
    print(entry)
