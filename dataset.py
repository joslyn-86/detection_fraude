import pandas as pd
import random

statuses = ["normal", "consumer", "addict", "dealer"]

# distribution réaliste
def random_status():
    r = random.random()
    if r < 0.70:
        return "normal"
    elif r < 0.90:
        return "consumer"
    elif r < 0.98:
        return "addict"
    else:
        return "dealer"

data = []

for i in range(100):
    name = f"Personne{i}"  
    age = random.randint(15, 60)
    status = random_status()

    data.append([i, name, age, status])

df = pd.DataFrame(data, columns=["id", "name", "age", "status"])

df.to_csv("dataset_people.csv", index=False)

print("Dataset 200 personnes généré ✔")