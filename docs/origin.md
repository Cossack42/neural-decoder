# Origin

## The idea (20 September 2026)

Most of my work so far has been high in the stack: AI products, agent pipelines, web MVPs. I want to work on brain-computer interfaces, and the software that matters most there sits much lower: signal processing on constrained hardware, under real-time deadlines. That was the gap in my experience.

The project was scoped to close it. Build a neural decoder twice:

1. **Offline in Python**, to understand the signal processing and the decoding maths on real recordings.
2. **On a Raspberry Pi Pico 2 in C**, on the RISC-V cores, which have no floating point unit. That forces fixed-point arithmetic and makes latency, memory and scheduling real problems.

It also joins two of my second-year modules at Southampton: COMP2321 (Artificial Intelligence) and COMP2323 (Computer Systems II), which uses the same board.

## Why this is a fair miniature of the real thing

An implant records from many electrodes, detects spikes, and turns them into an intent signal such as cursor velocity. It does this on a small chip, on a tight power budget, every few milliseconds. The same chain exists here at small scale:

```
raw signal -> band-pass filter -> threshold crossings -> binned counts -> decoder -> cursor velocity
```

## The go decision (5 October 2026)

After advice from an engineer in the field that depth and rigour on a single project count for more than breadth, I committed to this as my main project for the next five months, with a week-by-week plan to early March 2027.

## What done looks like

- A decoder running on the Pico 2 that turns streamed spike data into cursor velocity within a fixed time budget.
- Measured numbers for accuracy (R² against the Python reference), latency, throughput, RAM and flash.
- A closed-loop demo: a host replays a recording and draws the decoded cursor against the true one.
- A record of every decision and every dead end, in this folder.
