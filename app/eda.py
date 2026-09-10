from app.data_loader import load_tickets


df = load_tickets()

print("\n========== DATASET INFO ==========")
print(df.info())

print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

print("\n========== DUPLICATES ==========")
print("Duplicate rows:", df.duplicated().sum())

print("\n========== TARGET DISTRIBUTION ==========")
print(df["ground_truth_priority"].value_counts())

print("\n========== TARGET PERCENTAGE ==========")
print(df["ground_truth_priority"].value_counts(normalize=True) * 100)

print("\n========== NUMERICAL COLUMNS ==========")
print(df.select_dtypes(include="number").columns.tolist())

print("\n========== CATEGORICAL COLUMNS ==========")
print(df.select_dtypes(include="object").columns.tolist())