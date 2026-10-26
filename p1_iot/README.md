# P1: IoT Telemetry Failure Prediction
- Data: synthetic CNC telemetry (100 machines, generate_data.py), with injected NaNs and spikes.
- Cleaning: per-machine interpolation, percentile clipping.
- Split: by machine_id to avoid leakage.
- RUL model: PolynomialFeatures + StandardScaler + LinearRegression (RMSE/MAE in outputs/threshold_report.txt).
- Failure model: LogisticRegression (class_weight=balanced); threshold tuned on cross-validated
  train predictions for recall >= 0.90.
- Outputs: outputs/threshold_report.txt, rul_pred_vs_actual.png, precision_recall_curve.png
