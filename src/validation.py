import numpy as np
import pandas as pd
from sklearn.metrics import (roc_auc_score, accuracy_score, balanced_accuracy_score,
                             f1_score, matthews_corrcoef, brier_score_loss)


def purged_walk_forward(df, feats, horizon, make_model, start="2018-01-01", step=63, purge=True,
                        min_train=300, window=None):
    # Train trên quá khứ, dự đoán `step` ngày tiếp theo, rồi trượt lên.
    # purge=True: bỏ `horizon` dòng cuối của tập train vì nhãn của chúng dùng giá nằm trong block test.
    # df cần index liên tục 0..n-1 và cột target_{h}d.
    tcol = f"target_{horizon}d"
    ok = df[feats].notna().all(axis=1)
    first = int(np.argmax((df["date"] >= pd.Timestamp(start)).values))
    preds = []
    for b in range(first, len(df), step):
        cut = b - horizon if purge else b
        lo = 0 if window is None else max(0, cut - window)
        tr = df.iloc[lo:max(cut, 0)]
        tr = tr[tr[tcol].notna() & ok.iloc[lo:max(cut, 0)]]
        te = df.iloc[b:b + step]
        te = te[ok.iloc[b:b + step]]
        if len(tr) < min_train or len(te) == 0 or tr[tcol].nunique() < 2:
            continue
        m = make_model()
        m.fit(tr[feats].values, tr[tcol].values.astype(int))
        preds.append(pd.Series(m.predict_proba(te[feats].values)[:, 1], index=te.index))
    return pd.concat(preds).rename("p_up")


def classification_metrics(y, p, thr=0.5):
    yhat = (p >= thr).astype(int)
    return {
        "AUC": roc_auc_score(y, p) * 100,
        "Balanced Acc": balanced_accuracy_score(y, yhat) * 100,
        "Accuracy": accuracy_score(y, yhat) * 100,
        "F1 (Up)": f1_score(y, yhat, zero_division=0) * 100,
        "MCC": matthews_corrcoef(y, yhat),
        "Brier": brier_score_loss(y, np.clip(p, 0, 1)),
    }


def block_bootstrap_auc(y, p, block=63, n_boot=1000, seed=42):
    # lấy mẫu theo từng khối 63 ngày vì các nhãn liền nhau gần như giống nhau
    y, p = np.asarray(y), np.asarray(p)
    n = len(y)
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(n / block))
    out = []
    for _ in range(n_boot):
        starts = rng.integers(0, n - block + 1, n_blocks)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        if np.unique(y[idx]).size < 2:
            continue
        out.append(roc_auc_score(y[idx], p[idx]))
    return np.percentile(out, [2.5, 97.5]) * 100


def three_state_position(p, buy=0.60, sell=0.40):
    # p > buy thì mua, p < sell thì bán, ở giữa thì giữ nguyên vị thế
    pos, cur = [], 1.0
    for v in p:
        if v > buy:
            cur = 1.0
        elif v < sell:
            cur = 0.0
        pos.append(cur)
    return pd.Series(pos, index=p.index)


def backtest(position, ret_next, cost_bps=5):
    # vị thế chốt lúc đóng cửa ngày t, ăn lợi nhuận từ t đến t+1, mỗi lần đổi vị thế mất phí
    position = position.astype(float)
    turnover = position.diff().abs().fillna(position.iloc[0])
    r = position * ret_next - turnover * cost_bps / 1e4
    return r.fillna(0)


def perf_stats(log_ret):
    eq = np.exp(log_ret.cumsum())
    years = len(log_ret) / 252
    simple = np.expm1(log_ret)
    return {
        "CAGR %": (eq.iloc[-1] ** (1 / years) - 1) * 100,
        "Vol %": simple.std() * np.sqrt(252) * 100,
        "Sharpe": simple.mean() / simple.std() * np.sqrt(252),
        "Max DD %": (eq / eq.cummax() - 1).min() * 100,
        "Final x": eq.iloc[-1],
    }
