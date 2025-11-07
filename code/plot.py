import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load the JSON file
with open("out.json", "r") as f:
    data = json.load(f)

print("JSON file loaded successfully!")

# --- Convert to DataFrame ---
df = pd.DataFrame(data)


for input_seq_len in df["input_seq_len"].unique():
    for output_seq_len in df["output_seq_len"].unique():
        for shift in df["shift"].unique():
                mse = df[(df["input_seq_len"]==input_seq_len) & (df["output_seq_len"]==output_seq_len) & (df["shift"]==shift)]['MSE'].values[0]
                print(f"input_seq_len:{input_seq_len} - output_seq_len: {output_seq_len} --> MSE = {mse:.3f}")


# --- Create a scatter plot for each shift ---
shifts = df["shift"].unique()
colors = plt.cm.get_cmap("tab10", len(df["input_seq_len"].unique()))

for i, shift_val in enumerate(sorted(shifts)):
    subset = df[df["shift"] == shift_val]
    plt.figure(figsize=(6, 4))
    
    # Plot one color per input_seq_len
    for j, (input_val, subsub) in enumerate(subset.groupby("input_seq_len")):
        plt.scatter(
            subsub["output_seq_len"],
            subsub["MSE"],
            label=f"input_seq_len = {input_val}",
            color=colors(j),
            s=80
        )

    plt.title(f"Shift = {shift_val}")
    plt.xlabel("Output Sequence Length")
    plt.ylabel("MSE")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    
    x_min, x_max = df["output_seq_len"].min(), df["output_seq_len"].max()
    plt.xticks(np.arange(x_min, x_max + 12, 12))

    plt.tight_layout()
    plt.show()
    


    