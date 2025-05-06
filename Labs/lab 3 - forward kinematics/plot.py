from pyexpat import expat_CAPI
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import argparse

# Default robot parameters (cm)
DEFAULT_TRACK = 15.5
WRONG_TRACK = 20.0
LAP_TIME = 30.0  # seconds for one full circle


def compute_paths(df, track):
    tau = df['t_ms'].to_numpy() / 1000.0
    dt = np.diff(tau, prepend=0)

    # integrate encoder readings
    enc_l, enc_r = df['left_enc_cm'].to_numpy(), df['right_enc_cm'].to_numpy()
    x_o, y_o, th_o = [0.0], [0.0], [0.0]
    for i in range(1, len(df)):
        dL = enc_l[i] - enc_l[i-1]
        dR = enc_r[i] - enc_r[i-1]
        dtheta = (dR - dL) / track
        dcenter = 0.5 * (dR + dL)
        theta_mid = th_o[-1] + 0.5 * dtheta
        x_o.append(x_o[-1] + dcenter * np.cos(theta_mid))
        y_o.append(y_o[-1] + dcenter * np.sin(theta_mid))
        th_o.append(th_o[-1] + dtheta)
    x_obs = np.array(x_o)
    y_obs = np.array(y_o)

    return tau, x_obs, y_obs


def theoretical_path(exp, tau, track):

    if exp == 'forward_return':
        x_out = 15 * np.minimum(tau, 10)
        x_back = 15 * np.clip(tau - 10, 0, 10)
        return x_out - x_back, np.zeros_like(tau)

    if exp == 'forward_curve':
        # Straight for 5s @15cm/s → 75cm
        straight_x = np.linspace(0, 75, 50)
        straight_y = np.zeros_like(straight_x)
        # Quarter-circle arc radius (from TRACK_WIDTH and speeds 15 & 7.5)
        radius = 15.5 / 2 * (1 + 0.5/1 - 0.5)
        _theta = np.linspace(0, np.pi/2, 50)
        arc_x = straight_x[-1] + radius * np.sin(_theta)
        arc_y = radius - radius * np.cos(_theta)
        theoretical_x = np.concatenate([straight_x, arc_x])
        theoretical_y = np.concatenate([straight_y, arc_y])
        return theoretical_x, theoretical_y

    if exp == 'circle':
        # Compute R from the half-speed ratio used in circle.py
        LR_RATIO = 0.5
        R = (track/2) * (1 + LR_RATIO) / (1 - LR_RATIO)
        # Parametric angle for full lap over LAP_TIME seconds
        theta = 2 * np.pi * tau / LAP_TIME
        x0 = R * (1 - np.cos(theta))
        y0 = R * np.sin(theta)
        # Rotate entire circle left (CCW) by 90°: (x,y) -> (-y, x)
        x_th = -y0
        y_th = x0
        return x_th, y_th

    # fallback flat line
    return np.zeros_like(tau), np.zeros_like(tau)


def plot_experiment(fname, track, ax):
    exp = os.path.splitext(fname)[0]
    df = pd.read_csv(fname)
    tau, x_o, y_o = compute_paths(df, track)
    x_t, y_t = theoretical_path(exp, tau, track)

    ax.plot(x_t, y_t, '--', label=f'Theoretical (track=20cm)')
    ax.plot(x_o, y_o, '-',  label='Observed (encoder)')

    manual = f"{exp}_manual.csv"
    if os.path.exists(manual):
        dm = pd.read_csv(manual)
        ax.scatter(dm['x_cm'], dm['y_cm'], s=80,
                   facecolors='none', edgecolors='r',
                   label='Observed (tape)')

    ax.set_title(exp.replace('_',' ').title())
    ax.set(xlabel='X (cm)', ylabel='Y (cm)')
    ax.axis('equal')
    ax.legend()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--track-width', type=float, default=DEFAULT_TRACK,
                   help='Wheel track width in cm')
    args = p.parse_args()

    files = ['forward_return.csv', 'forward_curve.csv', 'circle.csv']
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))
    for fn, ax in zip(files, axs):
        plot_experiment(fn, args.track_width, ax)
    plt.tight_layout()
    plt.show()
