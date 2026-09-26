# N96 plan/backend research

Qualification is separate from training. The expanded plan has16 branches,width21,203956800 weighted entries; older fresh plan has32,width22,641754752. Fresh observations:

```json
[
  {
    "method": "expanded_portfolio",
    "plan_hash": "e6a3c5b7678a2e6761257ab6156de12e275c5ef60853165d1e7622bdfaa0592a",
    "weighted_entries": 203956800,
    "retained_width": 21,
    "branch_count": 16,
    "cache_state": "COLD",
    "timings": {
      "structural_planning_seconds": 0.0006917470600455999,
      "source_preparation_seconds": 0.5773739520227537,
      "worker_preparation_seconds": 10.280719171,
      "modular_gpu_seconds": 2.825785901,
      "readout_seconds": 0.017804487142711878,
      "crt_reconstruction_seconds": 0.03676033385728812,
      "verification_seconds": 0.007926205988042057,
      "end_to_end_solve_seconds": 13.212408462,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "fresh_min_fill",
    "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2",
    "weighted_entries": 641754752,
    "retained_width": 22,
    "branch_count": 32,
    "cache_state": "WARM_NEW_PLAN",
    "timings": {
      "structural_planning_seconds": 0.0006917470600455999,
      "source_preparation_seconds": 0.5773739520227537,
      "worker_preparation_seconds": 1.033534613,
      "modular_gpu_seconds": 9.017987203,
      "readout_seconds": 0.01407018513418734,
      "crt_reconstruction_seconds": 0.03628456186581266,
      "verification_seconds": 0.007225780049338937,
      "end_to_end_solve_seconds": 10.161436213,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "fresh_min_fill",
    "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2",
    "weighted_entries": 641754752,
    "retained_width": 22,
    "branch_count": 32,
    "cache_state": "WARM_SAME_SOURCE",
    "timings": {
      "structural_planning_seconds": 0.0006917470600455999,
      "source_preparation_seconds": 0.5773739520227537,
      "worker_preparation_seconds": 0.811094045,
      "modular_gpu_seconds": 9.007030412,
      "readout_seconds": 0.013918349053710699,
      "crt_reconstruction_seconds": 0.040551772946289304,
      "verification_seconds": 0.00728091795463115,
      "end_to_end_solve_seconds": 9.923256731,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "expanded_portfolio",
    "plan_hash": "e6a3c5b7678a2e6761257ab6156de12e275c5ef60853165d1e7622bdfaa0592a",
    "weighted_entries": 203956800,
    "retained_width": 21,
    "branch_count": 16,
    "cache_state": "WARM_NEW_PLAN",
    "timings": {
      "structural_planning_seconds": 0.0006917470600455999,
      "source_preparation_seconds": 0.5773739520227537,
      "worker_preparation_seconds": 0.523773894,
      "modular_gpu_seconds": 2.762313572,
      "readout_seconds": 0.009112754953093827,
      "crt_reconstruction_seconds": 0.04421652804690617,
      "verification_seconds": 0.007196099031716585,
      "end_to_end_solve_seconds": 3.386353948,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "expanded_portfolio",
    "plan_hash": "e6a3c5b7678a2e6761257ab6156de12e275c5ef60853165d1e7622bdfaa0592a",
    "weighted_entries": 203956800,
    "retained_width": 21,
    "branch_count": 16,
    "cache_state": "WARM_SAME_SOURCE",
    "timings": {
      "structural_planning_seconds": 0.0006917470600455999,
      "source_preparation_seconds": 0.5773739520227537,
      "worker_preparation_seconds": 0.491128196,
      "modular_gpu_seconds": 2.762568088,
      "readout_seconds": 0.012628859956748784,
      "crt_reconstruction_seconds": 0.03446863604325122,
      "verification_seconds": 0.0075951530598104,
      "end_to_end_solve_seconds": 3.354809071,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "fresh_min_fill",
    "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2",
    "weighted_entries": 641754752,
    "retained_width": 22,
    "branch_count": 32,
    "cache_state": "WARM_NEW_PLAN",
    "timings": {
      "structural_planning_seconds": 0.0006917470600455999,
      "source_preparation_seconds": 0.5773739520227537,
      "worker_preparation_seconds": 0.856703648,
      "modular_gpu_seconds": 8.978054087,
      "readout_seconds": 0.014506586943753064,
      "crt_reconstruction_seconds": 0.02828061705624694,
      "verification_seconds": 0.007322616991586983,
      "end_to_end_solve_seconds": 9.925774385,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "fresh_min_fill",
    "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2",
    "weighted_entries": 641754752,
    "retained_width": 22,
    "branch_count": 32,
    "cache_state": "WARM_SAME_SOURCE",
    "timings": {
      "structural_planning_seconds": 0.0006917470600455999,
      "source_preparation_seconds": 0.5773739520227537,
      "worker_preparation_seconds": 0.818898775,
      "modular_gpu_seconds": 8.972807872,
      "readout_seconds": 0.012508222949691117,
      "crt_reconstruction_seconds": 0.03412934205030888,
      "verification_seconds": 0.007256848970428109,
      "end_to_end_solve_seconds": 9.908070487,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "expanded_portfolio",
    "plan_hash": "e6a3c5b7678a2e6761257ab6156de12e275c5ef60853165d1e7622bdfaa0592a",
    "weighted_entries": 203956800,
    "retained_width": 21,
    "branch_count": 16,
    "cache_state": "WARM_NEW_PLAN",
    "timings": {
      "structural_planning_seconds": 0.0006917470600455999,
      "source_preparation_seconds": 0.5773739520227537,
      "worker_preparation_seconds": 0.538318691,
      "modular_gpu_seconds": 2.76241446,
      "readout_seconds": 0.013214058941230178,
      "crt_reconstruction_seconds": 0.03401196505876982,
      "verification_seconds": 0.007652670959942043,
      "end_to_end_solve_seconds": 3.401549803,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "expanded_portfolio",
    "plan_hash": "e6a3c5b7678a2e6761257ab6156de12e275c5ef60853165d1e7622bdfaa0592a",
    "weighted_entries": 203956800,
    "retained_width": 21,
    "branch_count": 16,
    "cache_state": "WARM_NEW_SOURCE",
    "timings": {
      "structural_planning_seconds": 0.00029839493799954653,
      "source_preparation_seconds": 0.5121627140324563,
      "worker_preparation_seconds": 0.651540937,
      "modular_gpu_seconds": 2.776350841,
      "readout_seconds": 0.006410134956240654,
      "crt_reconstruction_seconds": 0.018055441043759345,
      "verification_seconds": 0.00973324291408062,
      "end_to_end_solve_seconds": 3.50172066,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "fresh_min_fill",
    "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2",
    "weighted_entries": 641754752,
    "retained_width": 22,
    "branch_count": 32,
    "cache_state": "WARM_NEW_PLAN",
    "timings": {
      "structural_planning_seconds": 0.00029839493799954653,
      "source_preparation_seconds": 0.5121627140324563,
      "worker_preparation_seconds": 1.055851836,
      "modular_gpu_seconds": 8.984113596,
      "readout_seconds": 0.013502174871973693,
      "crt_reconstruction_seconds": 0.036116545128026305,
      "verification_seconds": 0.009180304012261331,
      "end_to_end_solve_seconds": 10.143108812,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "fresh_min_fill",
    "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2",
    "weighted_entries": 641754752,
    "retained_width": 22,
    "branch_count": 32,
    "cache_state": "WARM_SAME_SOURCE",
    "timings": {
      "structural_planning_seconds": 0.00029839493799954653,
      "source_preparation_seconds": 0.5121627140324563,
      "worker_preparation_seconds": 0.844887621,
      "modular_gpu_seconds": 8.976395307,
      "readout_seconds": 0.012494823895394802,
      "crt_reconstruction_seconds": 0.055155740104605194,
      "verification_seconds": 0.009362260927446187,
      "end_to_end_solve_seconds": 9.935375629,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "expanded_portfolio",
    "plan_hash": "e6a3c5b7678a2e6761257ab6156de12e275c5ef60853165d1e7622bdfaa0592a",
    "weighted_entries": 203956800,
    "retained_width": 21,
    "branch_count": 16,
    "cache_state": "WARM_NEW_PLAN",
    "timings": {
      "structural_planning_seconds": 0.00029839493799954653,
      "source_preparation_seconds": 0.5121627140324563,
      "worker_preparation_seconds": 0.512626915,
      "modular_gpu_seconds": 2.767333435,
      "readout_seconds": 0.01000890787690878,
      "crt_reconstruction_seconds": 0.02612333612309122,
      "verification_seconds": 0.010749535053037107,
      "end_to_end_solve_seconds": 3.374622203,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "expanded_portfolio",
    "plan_hash": "e6a3c5b7678a2e6761257ab6156de12e275c5ef60853165d1e7622bdfaa0592a",
    "weighted_entries": 203956800,
    "retained_width": 21,
    "branch_count": 16,
    "cache_state": "WARM_SAME_SOURCE",
    "timings": {
      "structural_planning_seconds": 0.00029839493799954653,
      "source_preparation_seconds": 0.5121627140324563,
      "worker_preparation_seconds": 0.497326053,
      "modular_gpu_seconds": 2.760281942,
      "readout_seconds": 0.012606981908902526,
      "crt_reconstruction_seconds": 0.038199037091097475,
      "verification_seconds": 0.009585136082023382,
      "end_to_end_solve_seconds": 3.361383974,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "fresh_min_fill",
    "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2",
    "weighted_entries": 641754752,
    "retained_width": 22,
    "branch_count": 32,
    "cache_state": "WARM_NEW_PLAN",
    "timings": {
      "structural_planning_seconds": 0.00029839493799954653,
      "source_preparation_seconds": 0.5121627140324563,
      "worker_preparation_seconds": 0.813214616,
      "modular_gpu_seconds": 8.977406658,
      "readout_seconds": 0.0051241659093648195,
      "crt_reconstruction_seconds": 0.02250001309063518,
      "verification_seconds": 0.008572845021262765,
      "end_to_end_solve_seconds": 9.892354529,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "fresh_min_fill",
    "plan_hash": "a865de1d7956b8d7ad9fab90e8e195a4a86a1366c3d9af1520240f38d60034c2",
    "weighted_entries": 641754752,
    "retained_width": 22,
    "branch_count": 32,
    "cache_state": "WARM_SAME_SOURCE",
    "timings": {
      "structural_planning_seconds": 0.00029839493799954653,
      "source_preparation_seconds": 0.5121627140324563,
      "worker_preparation_seconds": 0.832376598,
      "modular_gpu_seconds": 8.977637403,
      "readout_seconds": 0.008777430048212409,
      "crt_reconstruction_seconds": 0.026903482951787593,
      "verification_seconds": 0.00988594105001539,
      "end_to_end_solve_seconds": 9.901914535,
      "process_startup_seconds": 0.0
    }
  },
  {
    "method": "expanded_portfolio",
    "plan_hash": "e6a3c5b7678a2e6761257ab6156de12e275c5ef60853165d1e7622bdfaa0592a",
    "weighted_entries": 203956800,
    "retained_width": 21,
    "branch_count": 16,
    "cache_state": "WARM_NEW_PLAN",
    "timings": {
      "structural_planning_seconds": 0.00029839493799954653,
      "source_preparation_seconds": 0.5121627140324563,
      "worker_preparation_seconds": 0.509777167,
      "modular_gpu_seconds": 2.757739138,
      "readout_seconds": 0.013209110125899315,
      "crt_reconstruction_seconds": 0.03440258687410069,
      "verification_seconds": 0.008955968078225851,
      "end_to_end_solve_seconds": 3.367308566,
      "process_startup_seconds": 0.0
    }
  }
]
```
