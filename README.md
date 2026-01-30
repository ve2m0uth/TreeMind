## Introduction

TreeMind is a tool designed to automatically reproduce Android bug reports by combining **large language models (LLMs)** with **Monte Carlo Tree Search (MCTS)**. We introduce a novel method for real-world crash reproduction, leveraging the reasoning capabilities of LLMs to guide the exploration of the app's UI in a structured and efficient manner.

### Key Features

- **LLM-Empowered**:  LLMs generate candidate actions and score it by interpreting bug reports, providing reasoning-based guidance for the reproduction process.
- **Monte Carlo Tree Guided**: MCTS systematically explores the action space and directs the LLM towards promising sequences, improving efficiency and accuracy.
- **Automated Execution**: Generated actions are executed directly on emulators or devices using uiautomator2, closing the loop between reasoning and actual bug reproduction.

### Getting Started

Follow these steps to run **TreeMind** and reproduce Android bug reports:

#### 1. Clone the repository 

```
git https://github.com/Vermouth-hub/TreeMind.git
cd TreeMind
```

#### 2. Install dependencies 

```
pip install -r requirements.txt
```

#### 3. Prepare inputs 

- **App name** : The package name of the Android app you want to test.
- **Bug report file** : A text file containing the bug report.
- **Device port**  *(optional)*: The port of your emulator or connected device. Defaults to `emulator-5554`.

#### 4. Run the reproduction script 

Using emulator-5554:

```
python reproduction.py <app_name> <report_file_path>
```

With a specific device port:

```
python reproduction.py <app_name> <report_file_path> <device_port>
```

Display help:

```
python reproduction.py -h
```

#### 5. Example 

```
python reproduction.py myapp reports/bug1.txt
```

This command runs **TreeMind** on the `myapp` app using the bug report in `reports/bug1.txt` and the default emulator.Remember to install the target app which you need to reproduce in the emulator before run TreeMind.

#### Tips 

- Ensure your emulator or device is running and accessible via the specified port .
- The output actions will be automatically executed on the device using **uiautomator2** .
- For better reproducibility, make sure the app is in the expected initial state  before running TreeMind.

### Comparison with Baseline 

<table>
  <thead>
    <tr>
      <th style="width: 200px;">APK ID</th>
      <th style="width: 100px;">TreeMind</th>
      <th style="width: 100px;">ReActDroid</th>
      <th style="width: 100px;">ReBL</th>
      <th style="width: 100px;">AdbGPT</th>
      <th style="width: 100px;">Reprobot</th>
    </tr>
  </thead>
  <tbody>
    <tr><td>NewPipe-7825</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>sdbviewer-10</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>Anki-Android-9914</td><td>✅</td><td>❌</td><td>✅</td><td>✅</td><td>❌</td></tr>
    <tr><td>ankidroid-10584</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>Alarmio-47</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>plusTimer-19</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>GrowTracker-89</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>Shuttle-456</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>ankidroid-3370</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>ankidroid-2765</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>ankidroid-2564</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>ankidroid-2681</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>WhereYouGo-368</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>food-tracker-55</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>GrowTracker-87</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>markor-1565</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>Mesh-495</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>✅</td></tr>
    <tr><td>sdbviewer-7</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>FakeStandby-30</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>revolution-irc-183</td><td>✅</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td></tr>
    <tr><td>ankidroid-3224</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>pedometer-101</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>andror2-7</td><td>✅</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td></tr>
    <tr><td>andror2-11</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>andror2-23</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>andror2-159</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>andror2-162</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>andror2-164</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>andror2-168</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>andror2-198</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>andror2-276</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-1</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-2</td><td>✅</td><td>❌</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-3</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-5</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-7</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-8</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-9</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-11</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-12</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-13</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-14</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-15</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-17</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-21</td><td>✅</td><td>❌</td><td>✅</td><td>✅</td><td>❌</td></tr>
    <tr><td>recdroid-23</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-24</td><td>✅</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td></tr>
    <tr><td>recdroid-25</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-26</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-27</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>❌</td></tr>
    <tr><td>recdroid-28</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-29</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-30</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-31</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-33</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-34</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-35</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-38</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-39</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-42</td><td>❌</td><td>❌</td><td>✅</td><td>✅</td><td>❌</td></tr>
    <tr><td>recdroid-45</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-49</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-53</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-55</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-56</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-57</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-58</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>recdroid-60</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-61</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>✅</td></tr>
    <tr><td>recdroid-62</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td></tr>
    <tr><td>recdroid-64</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>saner2022-2</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>✅</td></tr>
    <tr><td>saner2022-8</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-11</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>saner2022-18</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-23</td><td>❌</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-129</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-271</td><td>❌</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-1089</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>saner2022-1096</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-1133</td><td>✅</td><td>❌</td><td>✅</td><td>✅</td><td>✅</td></tr>
    <tr><td>saner2022-1160</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-1207</td><td>❌</td><td>✅</td><td>✅</td><td>✅</td><td>❌</td></tr>
    <tr><td>saner2022-1215</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-1227</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-1299</td><td>✅</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-1430</td><td>✅</td><td>✅</td><td>✅</td><td>✅</td><td>❌</td></tr>
    <tr><td>saner2022-1447</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-1568</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>saner2022-1645</td><td>✅</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td></tr>
    <tr><td>yakusu-1</td><td>❌</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>yakusu-35</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>❌</td></tr>
    <tr><td>yakusu-98</td><td>✅</td><td>❌</td><td>❌</td><td>❌</td><td>✅</td></tr>
  </tbody>
</table>

