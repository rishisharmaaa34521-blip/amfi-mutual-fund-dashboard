# Project Liquidity Risk Classification Framework

This project-only framework compares the scenario's forecast outflow requirement with a buffer entered by the user. AMFI industry AUM is not used as a liquidity buffer.

- **LOW:** scenario outflow requirement is below 80% of the entered buffer and scenario net flow is non-negative.
- **MODERATE:** the buffer covers the outflow requirement, but utilization is at least 80%, or scenario net flow is negative.
- **HIGH:** scenario outflow requirement exceeds the entered buffer (positive liquidity gap).
- **UNASSESSED:** no buffer has been entered. The dashboard leaves the classification unassessed rather than treating a missing input as a zero buffer.

The 80% utilization threshold is an illustrative project assumption, not a regulatory threshold. A negative net flow is not by itself a liquidity crisis. Suggested actions are monitoring considerations, not investment advice.
