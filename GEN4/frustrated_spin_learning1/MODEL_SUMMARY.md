# Interpretable baselines

{
  "N": {
    "features": [
      "N"
    ],
    "coefficients": [
      -4.471288184443525,
      0.0702585155294195
    ],
    "loo_log_MAE": 0.8544624781490557,
    "fit_log_R2": 0.8415553156061055,
    "scope": "retrospective descriptive mixed-hardware atlas; not a frontier calibration"
  },
  "formal_state_count": {
    "features": [
      "N"
    ],
    "coefficients": [
      -4.471288184443525,
      0.0702585155294195
    ],
    "loo_log_MAE": 0.8544624781490557,
    "fit_log_R2": 0.8415553156061055,
    "scope": "retrospective descriptive mixed-hardware atlas; not a frontier calibration"
  },
  "fresh_width": {
    "features": [
      "pre_minfill_width"
    ],
    "coefficients": [
      -2.9314833663462743,
      0.20394999659681226
    ],
    "loo_log_MAE": 0.8453282746889179,
    "fit_log_R2": 0.8433834965176927,
    "scope": "retrospective descriptive mixed-hardware atlas; not a frontier calibration"
  },
  "component_assignments": {
    "features": [
      "pre_local_assignments"
    ],
    "coefficients": [
      -3.898260451735369,
      0.06523676999494149
    ],
    "loo_log_MAE": 0.919874564958045,
    "fit_log_R2": 0.8342701407274286,
    "scope": "retrospective descriptive mixed-hardware atlas; not a frontier calibration"
  },
  "components": {
    "features": [
      "pre_components",
      "pre_max_component"
    ],
    "coefficients": [
      -6.358268942656922,
      0.44923138270342694,
      0.08552822930275161
    ],
    "loo_log_MAE": 0.7141307366852166,
    "fit_log_R2": 0.8984361962463832,
    "scope": "retrospective descriptive mixed-hardware atlas; not a frontier calibration"
  },
  "arithmetic": {
    "features": [
      "pre_arithmetic_burden"
    ],
    "coefficients": [
      -4.792410685980889,
      0.18257252424104384
    ],
    "loo_log_MAE": 0.6971048124432182,
    "fit_log_R2": 0.8933596726392555,
    "scope": "retrospective descriptive mixed-hardware atlas; not a frontier calibration"
  },
  "structural": {
    "features": [
      "pre_minfill_width",
      "pre_components",
      "pre_max_component",
      "pre_root_bound",
      "pre_crt_primes"
    ],
    "coefficients": [
      -6.378499835137453,
      0.11151446903060318,
      0.3835528642900355,
      0.03998750068055926,
      0.12280216460057965,
      0.11988621248829663
    ],
    "loo_log_MAE": 0.6156543923388704,
    "fit_log_R2": 0.9271827865320763,
    "scope": "retrospective descriptive mixed-hardware atlas; not a frontier calibration"
  }
}

Hardware strata:
{
  "14_MIG_GPU_batched_readout": {
    "n": 22,
    "loo_log_MAE": 0.2333093642211553
  },
  "14_MIG_GPU_retained_readout": {
    "n": 96,
    "loo_log_MAE": 0.2519745264791657
  },
  "historical_CPU": {
    "n": 2,
    "status": "insufficient independent examples"
  }
}
No post-result features enter these fits. Historical selected-route comparisons are descriptive. N and log formal state-count carry identical information.
