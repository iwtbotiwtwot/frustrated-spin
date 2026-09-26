# N100/N105 structural forensics

Retrospective family transfer, not a located preregistered prediction. N100 ran before N105 on August2. The causal claim about skippingN108 is not established.

[
  {
    "N": 99,
    "pre_source_family": "N120_INDUCED_PREFIX_GAP1",
    "pre_components": 1,
    "pre_component_sizes": [
      99
    ],
    "pre_local_assignments": 633825300114114700748351602688,
    "pre_minfill_width": 26,
    "post_seconds": 18.39074689,
    "post_hardware": "14_MIG_GPU_batched_readout",
    "post_method": "inherited_N120_plan"
  },
  {
    "N": 100,
    "pre_source_family": "N100_P2_PACKET_PLUS_DEPTH_V1",
    "pre_components": 8,
    "pre_component_sizes": [
      5,
      10,
      10,
      15,
      15,
      15,
      15,
      15
    ],
    "pre_local_assignments": 165920,
    "pre_minfill_width": 5,
    "post_seconds": 0.5009514410048723,
    "post_hardware": "historical_CPU",
    "post_method": "components"
  },
  {
    "N": 101,
    "pre_source_family": "N120_INDUCED_PREFIX_GAP1",
    "pre_components": 1,
    "pre_component_sizes": [
      101
    ],
    "pre_local_assignments": 2535301200456458802993406410752,
    "pre_minfill_width": 26,
    "post_seconds": 23.841435986,
    "post_hardware": "14_MIG_GPU_batched_readout",
    "post_method": "inherited_N120_plan"
  },
  {
    "N": 104,
    "pre_source_family": "N120_INDUCED_PREFIX_GAP1",
    "pre_components": 1,
    "pre_component_sizes": [
      104
    ],
    "pre_local_assignments": 20282409603651670423947251286016,
    "pre_minfill_width": 32,
    "post_seconds": 33.207589012,
    "post_hardware": "14_MIG_GPU_batched_readout",
    "post_method": "inherited_N120_plan"
  },
  {
    "N": 105,
    "pre_source_family": "N105_P9G0_HISTORICAL_PACKET_RESTORATION_V1",
    "pre_components": 8,
    "pre_component_sizes": [
      10,
      10,
      10,
      15,
      15,
      15,
      15,
      15
    ],
    "pre_local_assignments": 166912,
    "pre_minfill_width": 5,
    "post_seconds": 0.3618633120204322,
    "post_hardware": "historical_CPU",
    "post_method": "components"
  },
  {
    "N": 106,
    "pre_source_family": "N120_INDUCED_PREFIX_GAP1",
    "pre_components": 1,
    "pre_component_sizes": [
      106
    ],
    "pre_local_assignments": 81129638414606681695789005144064,
    "pre_minfill_width": 32,
    "post_seconds": 72.374879583,
    "post_hardware": "14_MIG_GPU_batched_readout",
    "post_method": "inherited_N120_plan"
  }
]

Minimal explanation: independent components bound local enumeration by the sum of component state counts, followed by polynomial convolution. Packet N100/N105 have largest component15; nearby canonical connected sources cannot use that decomposition. Adding the restored packet changes local assignment work only modestly. Hardware and historical execution scopes differ, so the time ratio alone is not a causal measurement. New within-host component/VE comparisons and bridge ablations test this explanation.
