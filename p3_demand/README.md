# P3: Demand Forecasting with MLP + Optuna
- Data: synthetic (generate_data.py), 200 SKUs x 365 days, with promo, weather, season and shipping-delay effects.
- Split: by time (train 0-270 d, validation 270-320 d, test last 45 d); no random shuffling.
- Model: PyTorch MLP with BatchNorm and Dropout; target is log1p(units).
- Tuning: Optuna (20 trials) over depth, width, dropout, learning rate, L2 and activation.
- Results: outputs/model_comparison.csv; plots: loss_curves.png, optuna_convergence.png.
