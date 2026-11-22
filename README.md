# Power per machine from one factory meter

> **In short:** give it a factory's total power and which machines are on. It tells you how much power each machine uses.
> Best method: **Gaussian allocation**, off by **6.4 W** per machine on average (a simple split is off by 17.5 W).

## What it does

```mermaid
flowchart LR
    total["Plant meter:<br/>total power"] --> method["Method,<br/>e.g. Gaussian allocation"]
    states["Control system:<br/>which machines are on"] --> method
    method --> m1["Machine 1:<br/>power"]
    method --> m2["Machine 2:<br/>power"]
    method --> mn["...<br/>Machine N:<br/>power"]
```

* **In:** the total power from the plant's main meter, and each machine's on/off state (a plant usually has this already, from its control system, the PLC).
* **Out:** each machine's power, for every sample.
* **Why it helps:** no meter is needed on each machine. This is called NILM: non-intrusive load monitoring.

## Try it

Needs [uv](https://docs.astral.sh/uv/).

```sh
uv run src/preprocessing/fetch_hipe.py   # 1. download the HIPE data: 1.3 GB, 31 GB unpacked
uv run src/preprocessing/hipe.py         # 2. build training and test sets: about 30 min
uv run src/allocation/allocation.py --dataset hipe --machines 9   # 3. run the best method
uv run src/validation/validation.py      # 4. score it
```

Every Python folder has a self-check: `uv run src/<folder>/test_<name>.py`.

## Methods

| Method | Code | How it works |
|---|---|---|
| **Gaussian allocation** | [`src/allocation`](src/allocation) | Learns each machine's typical power levels (idle, heating, ...), then splits the total among the running machines in the most likely way. |
| Neural network | [`src/neural_network`](src/neural_network) | A small neural network, trained to make the running machines' estimates add up to the total. |
| Polynomial model | [`src/polynomial`](src/polynomial) | Each machine's power is a polynomial of the total, fitted by optimisation algorithms. C++: needs CMake and a C++20 compiler. |
| Hart-inspired | [`src/hart_inspired`](src/hart_inspired) | Reads each machine's power from the drop in the total when it switches off. |

The neural network and the polynomial model come from my [MSc dissertation](docs/Dissertation_NILM.pdf) (University of Coimbra). Gaussian allocation was added later.

## Results

**Gaussian allocation wins on every test. Nothing else beats the simple proportional split on average.**

![Metered and estimated power of four HIPE machines over six hours of 5 December 2017. The estimate closely follows the vacuum pump, the screen printer and the high-temperature oven's heating cycles. Around 09:30, while both ovens run, part of the soldering oven's power goes to the high-temperature oven.](docs/allocation_example.png)

*Blue: metered power. Orange: Gaussian allocation's estimate. Four of the nine machines in HIPE group 9, on a busy December morning (data: KIT, CC BY 4.0).*
*Mostly a close match. The main miss is around 09:30: both ovens run at once, and part of the SolderingOven's power goes to the HighTemperatureOven.*

* **Data:** [HIPE](https://www.energystatusdata.kit.edu/hipe.php), ten machines at an electronics production site in Germany, each with its own meter.
* **Test:** add the machine meters into a total, let each method split it back, and compare with the real meters. Repeated for nine groups of 2 to 10 machines.
* **Fair:** tuned on October 2017, trained on November, scored on December, a month no method saw beforehand.

| Method | Average error per machine (W) |
|---|---|
| **Gaussian allocation** | **6.4** |
| Simple split: in proportion to each machine's average power | 17.5 |
| Neural network | 18.7 |
| Polynomial model | 21.6 |
| Simple split: equally among the running machines | 28.4 |
| Hart-inspired | 51.0 |
| Guess 0 W (= the machines' average power) | 51.4 |

On a second dataset, [IMDELD](https://ieee-dataport.org/open-access/industrial-machines-dataset-electrical-load-disaggregation), no method clearly beats guessing 0 W. Its machines almost always switch on and off together, so their power can't be told apart.

## Limits

* **It needs to know when each machine is on.** A 10 s delay barely matters. A 60 s delay, or 1% of the signals wrong, doubles the error or worse.
* **Machines that always run together can't be told apart.**

## More

* [docs/notes.md](docs/notes.md): every number, option and design choice, with a table to jump to what you need.
* [src/polynomial/README.md](src/polynomial/README.md): building and running the polynomial model.

## License

[CC BY-NC-SA 4.0](LICENSE), © 2023 [Daniel Torres](https://github.com/danctorres). The datasets keep their own terms.
