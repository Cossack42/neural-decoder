# Decision log

One entry per choice, newest last. Each has the reason and the alternative rejected. Status is one of: adopted, proposed, to revisit, reversed.

| # | Date | Decision | Why | Alternative rejected | Status |
|---|---|---|---|---|---|
| 1 | 2026-09-20 | Kalman filter as the main decoder, with a small neural network as a comparison | It is the standard decoder in clinical BCI work, and its small fixed-size matrices suit fixed-point maths on a microcontroller | Neural network only: harder to port and harder to explain | Adopted |
| 2 | 2026-09-20 | Target the Pico 2's RISC-V cores under FreeRTOS | No FPU, so fixed-point is forced, which is the interesting engineering. Same board as COMP2323 | The ARM cores, which have an FPU | Adopted |
| 3 | 2026-09-20 | O'Doherty and Sabes reaching data as the primary dataset, MC_Maze as the second | Standard motor decoding benchmark with spikes and cursor kinematics, plus raw broadband for spike detection | Synthetic data: results would not be credible | Adopted |
| 4 | 2026-10-05 | Keep the Pico 2 as the decoder; use a ClockworkPi DevTerm as the host that replays data and shows the cursor | A Linux machine with an FPU removes the real-time, fixed-point challenge | Running the decoder on the DevTerm | Proposed |
| 5 | 2026-10-05 | Pool sorted and unsorted spikes on each channel | The Pico will only ever see threshold crossings, so Python and on-device results stay comparable | Sorted single units: likely better R² but not reproducible on the device | Adopted |
| 6 | 2026-10-05 | 50 ms bins for the first baseline | Common starting point | 20 ms from the start, which is closer to the planned on-device cadence | To revisit |
| 7 | 2026-10-05 | Keep both arrays (M1 and S1) and drop channels firing under 0.5 Hz | Simplest start; M1 only is a planned experiment | M1 only | To revisit |
| 8 | 2026-10-05 | Write the core signal chain and fixed-point maths by hand; use AI for plumbing and review | I need to be able to explain and defend every layer | AI-written core | Adopted |
| 9 | 2026-10-08 | Trunk-based repo: commit straight to `main`, with lint and tests run on every push | One person, small codebase; the checks are the gate | Branches and pull requests | Adopted |

## How to add an entry

Add a row when a choice is made, not afterwards. If a decision is reversed, change its status to "reversed" and add a new row that says what replaced it and why. Never delete rows.
