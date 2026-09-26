# Packet hardware placement

Packet and connected-prefix identities remain separate. Fresh matched decisions:

```json
[
  {
    "source_hash": "f4f512facb6a5b46acbf03543c91d6653cb961b30ea9f2a1c1af33255bb1aa0b",
    "source_key": "N100",
    "preferred_backend": "LOCAL_FLINT_CPU",
    "warm_end_to_end_seconds": {
      "LOCAL_FLINT_CPU": 0.02259392896667123,
      "COOP14_MIG_BRANCH_GROUP": 0.09102504
    },
    "execution_context": {
      "LOCAL_FLINT_CPU": {
        "method": "variable_elimination",
        "plan_hash": "da0c3ebe1a22b3ad2df71939cd5815aa6e1c35f645c366a9a0155ea98b1508b3",
        "cache_state": "WARM_SAME_SOURCE"
      },
      "COOP14_MIG_BRANCH_GROUP": {
        "method": "fresh_min_fill",
        "plan_hash": "9bba112fdafcc7ff8767041e14b7104dc56bb4e85722a3fea8c9f3578fb4077f",
        "cache_state": "WARM_SAME_SOURCE"
      }
    },
    "status": "REPEATED_EMPIRICAL_RULE",
    "scope": "Matched source and ordered observable; native route includes internal checks; startup and external verification excluded; cache reuse alternatives separately recorded"
  },
  {
    "source_hash": "5776b29715e9a50cd9f500c1b53e676b5e8d4ed040d40ac02cad5f3eb90e7774",
    "source_key": "N105",
    "preferred_backend": "LOCAL_FLINT_CPU",
    "warm_end_to_end_seconds": {
      "LOCAL_FLINT_CPU": 0.024194170022383332,
      "COOP14_MIG_BRANCH_GROUP": 0.107189816
    },
    "execution_context": {
      "LOCAL_FLINT_CPU": {
        "method": "variable_elimination",
        "plan_hash": "36f415dc55f796534a8292eff61c9d1ffba193f9b9c59e84c444064502b52234",
        "cache_state": "WARM_NEW_SOURCE"
      },
      "COOP14_MIG_BRANCH_GROUP": {
        "method": "fresh_min_fill",
        "plan_hash": "4ce49b3bd57787671e8d84190fc6ac27792c247097b95e747076012c6fbf8164",
        "cache_state": "WARM_SAME_SOURCE"
      }
    },
    "status": "REPEATED_EMPIRICAL_RULE",
    "scope": "Matched source and ordered observable; native route includes internal checks; startup and external verification excluded; cache reuse alternatives separately recorded"
  }
]
```

CPU cache reuse is reported separately from fresh recomputation. All saved rows retain timing scopes and verification identity.
