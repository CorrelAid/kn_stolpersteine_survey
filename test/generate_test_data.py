import pickle
import argparse
from faker import Faker
import random
from pathlib import Path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-n', dest="num_persons", default=10, metavar='N',
                        help="Number of fake persons", type=int)
    args = parser.parse_args()

    fake = Faker("de_DE")

    full_data = []

    for _ in range(args.num_persons):
        if random.random() < .5:
            first = fake.first_name_female()
            maiden = fake.last_name()
        else:
            first = fake.first_name_male()
            maiden = None
        last = fake.last_name()
        address = fake.address()
        birthplace = fake.city()

        full_data.append({
            "vorname":first,
            "nachname":last,
            "data": {
                "adresse": address,
                "geburtsname" : maiden,
                "geburtsort":birthplace
            }
        })

    with open(Path(__file__).parents[0].joinpath("data.pickle"), "wb") as f:
        pickle.dump(full_data, f)