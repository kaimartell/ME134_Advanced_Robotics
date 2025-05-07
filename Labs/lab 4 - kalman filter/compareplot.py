# compareplot.py
import pandas as pd
import matplotlib.pyplot as plt

def load_csv(fname):
    """
    Load a CSV, ignoring lines that start with '#' and blank lines,
    and trimming spaces after commas.
    """
    return pd.read_csv(
        fname,
        comment='#',
        skip_blank_lines=True,
        skipinitialspace=True
    )

def detect_xy(df, df_name):
    """
    Return (x_series, y_series) by looking for x_cm/y_cm or x/y.
    """
    if "x_cm" in df.columns and "y_cm" in df.columns:
        return df["x_cm"], df["y_cm"]
    if "x" in df.columns and "y" in df.columns:
        return df["x"], df["y"]
    raise KeyError(f"No x/y columns found in {df_name}: {df.columns.tolist()}")

# Load FK data
fk = load_csv("fk_log.csv")                # FK estimates
gt_fk = load_csv("ground_truth_fk.csv")    # FK ground truth

# Load KF data
kf = load_csv("kalman_log.csv")            # KF estimates
gt_kf = load_csv("ground_truth_kf.csv")    # KF ground truth

# Extract positions
x_fk_est, y_fk_est = detect_xy(fk,   "fk_log.csv")
x_fk_gt,  y_fk_gt  = detect_xy(gt_fk, "ground_truth_fk.csv")

x_kf_est, y_kf_est = detect_xy(kf,   "kalman_log.csv")
x_kf_gt,  y_kf_gt  = detect_xy(gt_kf, "ground_truth_kf.csv")

plt.figure(figsize=(8,6))

# FK plots
plt.scatter(x_fk_gt, y_fk_gt, marker='o', s=100, label="FK Ground Truth")
plt.scatter(x_fk_est, y_fk_est, marker='x', label="FK Estimate")

# KF plots
plt.scatter(
    x_kf_gt, y_kf_gt,
    marker='o',
    facecolors='none',
    edgecolors='b',
    s=100,                          # increase marker size
    label="KF Ground Truth"
)
plt.scatter(x_kf_est, y_kf_est, marker='x', label="KF Estimate")

plt.title("Forward Kinematics & Kalman Filter: Estimates vs. Ground Truths")
plt.xlabel("X position (cm)")
plt.ylabel("Y position (cm)")
plt.grid(True)
plt.legend()
plt.show()
