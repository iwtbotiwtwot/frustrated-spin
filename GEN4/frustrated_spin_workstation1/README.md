# Workstation frustrated-spin restart

Owner: Sean Brady.

Verified inherited packet checkpoint through N1350. Full older answers remain on T500 at /home/sam/mnt/lilhelper-t500/SAM_POD_BACKUPS/frustrated-spin-20260926/restored/packet/results. Local working results start with the final checkpoint; sources, methods and full verification are preserved. CPU local hardware qualification passed against retained N120 authority in a separate directory.

Next exact N: 1351.

Run one next N (all three packet families):

    /home/sam/PycharmProjects/SAM_Research_Project/.venv-r3/bin/python /home/sam/PycharmProjects/SAM_Research_Project/GEN4/frustrated_spin_workstation1/workstation_launch.py --steps 1 --hours 1

Use --steps and --hours to bound continuation. Exact source answers are always independently recomputed and compared. Native runtime is isolated; no global selectors changed. CPU cost observations carry this workstation runtime identity. This launcher continues packet exact results; completed dense magnetization GPU work and dense graph sources are retained on T500.

Stop safely with packet/STOP or SIGTERM. Remove that STOP file only when intentionally resuming.
