import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.stats import norm, chi2


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

file_path = r"C:\Users\HP\Documents\Downloads\Microsoft Inference\MSFT_stock_2021.xlsx"
df = pd.read_excel(file_path)

prices = df["Close"].values
R = np.log(prices[1:]/prices[:-1])
n = len(R)

print(f"n = {n}")
mean_R = R.mean()
sd_R = R.std(ddof=1)
print(f"mean = {mean_R:.10f}")
print(f"sd = {sd_R:.10f}")

pos = np.sum(R > 0)
neg = np.sum(R < 0)
zero = np.sum(R == 0)
N = pos+neg

mu_sign = N/2.0
sigma_sign = math.sqrt(N/4.0)

print("\n" + "="*50)
print(" (a) SIGN TEST: Directional Bias")
print(f"positives Ri = {pos}")
print(f"negatives Ri = {neg}")
print(f"zeros = {zero}")
print(f"N (new n)) = {N}")

print("="*50)
print("HYPOTHESIS TEST")
print("="*50)
print("H0: The median of log returns is zero (p = 0.5, symmetric direction)")
print("HA: The median is not zero (Directional bias exists)")
Z_sign = (pos - mu_sign) / sigma_sign
p_sign = 2 * (1 - norm.cdf(abs(Z_sign)))  # Two-tailed p-value
print(f"Z-statistic = {Z_sign:.4f}")
print(f"p-value     = {p_sign:.4e}")

if p_sign < 0.05:
    print("==> CONCLUSION: REJECT H0 at 5% significance level.")
    print("==> INSIGHT: The stock exhibits a statistically significant directional bias (upward drift).")
else:
    print("==> CONCLUSION: FAIL TO REJECT H0 at 5% significance level.")
    

plt.figure(figsize=(8, 6))
bars = plt.bar(['Positive Days', 'Negative Days', 'Zero/Flat Days'], [pos, neg, zero], color=['#2ca02c', '#d62728', '#7f7f7f'])
plt.title('Sign Test: Directional Bias of Daily Returns', fontsize=14)
plt.ylabel('Number of Trading Days', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 50, int(yval), ha='center', va='bottom', fontweight='bold')
    
plt.savefig('1_sign_test.png', bbox_inches='tight')
print("=> Saved: 1_sign_test.png")
plt.close()

R_nz = R[R != 0]
N_w = len(R_nz)

abs_R = np.abs(R_nz)
ranks = pd.Series(abs_R).rank(method="average").to_numpy()
signs = np.sign(R_nz)

W_plus = ranks[signs > 0].sum()
W_minus = ranks[signs < 0].sum()
W = np.sum(ranks*signs)

print("\n" + "="*50)
print(" (b) WILCOXON SIGNED-RANK TEST: Magnitude Asymmetry")
print(f"N (non-zero) = {N_w}")
print(f"W+ (positive ranks sum) = {W_plus:.1f}")
print(f"W- (negative ranks sum) = {W_minus:.1f}")
print(f"W = sum of signed ranks = {W:.1f}")

print("="*50)
print("HYPOTHESIS TEST")
print("="*50)
print("H0: The distribution of log returns is perfectly symmetric around zero")
print("HA: The distribution is asymmetric (Intensity of up/down days differ)")
sigma_W = math.sqrt(N_w * (N_w + 1) * (2 * N_w + 1) / 6.0)
Z_W = W / sigma_W
p_W = 2 * (1 - norm.cdf(abs(Z_W)))
print(f"Z-statistic = {Z_W:.4f}")
print(f"p-value     = {p_W:.4e}")

if p_W < 0.05:
    print("==> CONCLUSION: REJECT H0 at 5% significance level.")
    print("==> INSIGHT: The magnitude of positive returns is statistically larger than negative returns.")
else:
    print("==> CONCLUSION: FAIL TO REJECT H0 at 5% significance level.")

plt.figure(figsize=(8, 6))
bars = plt.bar(['W+ (Positive Ranks)', 'W- (Negative Ranks)'], [W_plus, W_minus], color=['#2ca02c', '#d62728'])
plt.title('Wilcoxon Signed-Rank Test: Momentum & Magnitude', fontsize=14)
plt.ylabel('Sum of Absolute Ranks', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Format y-axis to read in millions
plt.gca().yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 200000, f"{int(yval):,}", ha='center', va='bottom', fontweight='bold')

plt.savefig('2_wilcoxon_test.png', bbox_inches='tight')
print("=> Saved: 2_wilcoxon_test.png")
plt.close()

mu0 = 0.0
sigma0 = 0.02

bins = [-math.inf, -0.001, -0.0004, 0.0, 0.0004, 0.001, math.inf]
obs_counts = []
for i in range(len(bins)-1):
    a, b = bins[i], bins[i+1]
    if a == -math.inf:
        mask = R < b
    elif b == math.inf:
        mask = R >= a
    else:
        mask = (R >= a) & (R < b)
    obs_counts.append(mask.sum())

probs0 = []
for i in range(len(bins)-1):
    a, b = bins[i], bins[i+1]
    pa = 0.0 if a == -math.inf else phi((a-mu0)/sigma0)
    pb = 1.0 if b == math.inf else phi((b-mu0)/sigma0)
    probs0.append(pb-pa)

exp_counts0 = [p*n for p in probs0]

chi2_0 = sum((o-e)**2/e for o, e in zip(obs_counts, exp_counts0))

print("\n" + "="*50)
print(" (c) CHI-SQUARE GOODNESS-OF-FIT TESTS WITH STANDARD NORMAL DISTRIBUTION N(0, 0.02^2)")
print("Observed counts =", obs_counts)
print("Expected counts =", [round(e, 2) for e in exp_counts0])
print(f"chi^2 statistic = {chi2_0:.4f}")

print("="*50)
print("HYPOTHESIS TEST")
print("="*50)
print("H0: The data perfectly follows a theoretical N(0, 0.02^2) distribution")
print("HA: The data does not follow this normal distribution")
df_fixed = len(bins) - 1  # 6 bins - 1 = 5 degrees of freedom
crit_fixed = chi2.ppf(0.95, df_fixed)
p_fixed = 1 - chi2.cdf(chi2_0, df_fixed)

print(f"Chi^2 Statistic = {chi2_0:.4f}")
print(f"Critical Value  = {crit_fixed:.4f} (df={df_fixed})")
print(f"p-value         = {p_fixed:.4e}")
if chi2_0 > crit_fixed:
    print("==> CONCLUSION: REJECT H0.")
else:
    print("==> CONCLUSION: FAIL TO REJECT H0.")
    
    
mu_hat = mean_R
sigma_hat = math.sqrt(((R-mu_hat)**2).mean())

probs_hat = []
for i in range(len(bins)-1):
    a, b = bins[i], bins[i+1]
    pa = 0.0 if a == -math.inf else phi((a-mu_hat)/sigma_hat)
    pb = 1.0 if b == math.inf else phi((b-mu_hat)/sigma_hat)
    probs_hat.append(pb-pa)

exp_counts_hat = [p*n for p in probs_hat]
chi2_hat = sum((o-e)**2/e for o, e in zip(obs_counts, exp_counts_hat))

print("\n" + "="*50)
print(" (d) CHI-SQUARE GOODNESS-OF-FIT TESTS WITH FITTED NORMAL DISTRIBUTION N(\u03bc\u0302, \u03c3\u0302\u00b2)")
print(f"mu_hat    = {mu_hat:.10f}")
print(f"sigma_hat = {sigma_hat:.10f}")
print("Observed counts =", obs_counts)
print("Expected counts =", [round(e, 2) for e in exp_counts_hat])
print(f"chi^2 statistic = {chi2_hat:.4f}")

print("="*50)
print("HYPOTHESIS TEST")
print("="*50)
print("H0: The data follows a normal distribution tailored to its own sample mean/variance")
print("HA: The data rejects normality altogether (Presence of Fat Tails / Leptokurtosis)")
df_fitted = len(bins) - 1 - 2  # 6 bins - 1 - 2 estimated parameters (mu, sigma) = 3 df
crit_fitted = chi2.ppf(0.95, df_fitted)
p_fitted = 1 - chi2.cdf(chi2_hat, df_fitted)

print(f"Chi^2 Statistic = {chi2_hat:.4f}")
print(f"Critical Value  = {crit_fitted:.4f} (df={df_fitted})")
print(f"p-value         = {p_fitted:.4e}")
if chi2_hat > crit_fitted:
    print("==> CONCLUSION: REJECT H0.")
    print("==> INSIGHT: Even when perfectly calibrated, Normal Distributin curves fail to capture real market patterns.")
else:
    print("==> CONCLUSION: FAIL TO REJECT H0.")

labels = ['< -0.1%', '-0.1% to -0.04%', '-0.04% to 0%', '0% to 0.04%', '0.04% to 0.1%', '> 0.1%']
x = np.arange(len(labels))
width = 0.25

plt.figure(figsize=(12, 6))
# Plotting grouped bars side-by-side
plt.bar(x - width, obs_counts, width, label='Observed (Actual MSFT Data)', color='#1f77b4')
plt.bar(x, exp_counts0, width, label='Expected (Fixed Normal)', color='#ff7f0e')
plt.bar(x + width, exp_counts_hat, width, label='Expected (Fitted Normal)', color='#9467bd')

plt.title('Chi-Square Test: Real Returns vs. Theoretical Normal Curves', fontsize=14)
plt.ylabel('Frequency (Number of Days)', fontsize=12)
plt.xlabel('Daily Log Return Intervals', fontsize=12)
plt.xticks(x, labels)
plt.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.savefig('3_chisquare_test.png', bbox_inches='tight')
print("=> Saved: 3_chisquare_test.png")
plt.close()