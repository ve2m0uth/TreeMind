### Introduction

TreeMind is a tool designed to automatically reproduce Android bug reports by combining **large language models (LLMs)** with **Monte Carlo Tree Search (MCTS)**. We introduce a novel method for real-world crash reproduction, leveraging the reasoning capabilities of LLMs to guide the exploration of the app's UI in a structured and efficient manner.

#### Key Features🚀

- **💡LLM-Empowered**:  LLMs generate candidate actions and score it by interpreting bug reports, providing reasoning-based guidance for the reproduction process.
- **🎄Monte Carlo Tree Guided**: MCTS systematically explores the action space and directs the LLM towards promising sequences, improving efficiency and accuracy.
- ⚙️**Automated Execution**: Generated actions are executed directly on emulators or devices using uiautomator2, closing the loop between reasoning and actual bug reproduction.

#### Getting Started

Follow these steps to run **TreeMind** and reproduce Android bug reports:

##### 1. Clone the repository 📂

```
git https://github.com/Vermouth-hub/TreeMind.git
cd TreeMind
```

##### 2. Install dependencies ⚙️

```
pip install -r requirements.txt
```

##### 3. Prepare inputs 📝

- **App name** 📱: The package name of the Android app you want to test.
- **Bug report file** 🐛: A text file containing the bug report.
- **Device port** 🔌 *(optional)*: The port of your emulator or connected device. Defaults to `emulator-5554`.

##### 4. Run the reproduction script ▶️

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

##### 5. Example 💡

```
python reproduction.py myapp reports/bug1.txt
```

This command runs **TreeMind** on the `com.example.myapp` app using the bug report in `reports/bug1.txt` and the default emulator.

##### Tips ⚠️

- Ensure your emulator or device is running and accessible via the specified port 🔌.
- The output actions will be automatically executed on the device using **uiautomator2** 🤖.
- For better reproducibility, make sure the app is in the expected initial state 🏠 before running TreeMind.

#### Comparison with Baseline 

| APK NAME           | TreeMind | ReActDroid | ReBL | AdbGPT | Reprobot |
| :----------------- | :------: | :--------: | :--: | :----: | :------: |
| NewPipe-7825       |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| sdbviewer-10       |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| Anki-Android-9914  |    ✅     |     ❌      |  ✅   |   ✅    |    ❌     |
| ankidroid-10584    |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| Alarmio-47         |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| plusTimer-19       |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| GrowTracker-89     |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| Shuttle-456        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| ankidroid-3370     |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| ankidroid-2765     |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| ankidroid-2564     |    ✅     |     ✅      |  ❌   |   ❌    |    ❌     |
| ankidroid-2681     |    ✅     |     ✅      |  ❌   |   ❌    |    ❌     |
| WhereYouGo-368     |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| food-tracker-55    |    ✅     |     ✅      |  ❌   |   ❌    |    ❌     |
| GrowTracker-87     |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| markor-1565        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| Mesh-495           |    ✅     |     ✅      |  ❌   |   ❌    |    ✅     |
| sdbviewer-7        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| FakeStandby-30     |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| revolution-irc-183 |    ✅     |     ✅      |  ✅   |   ❌    |    ❌     |
| ankidroid-3224     |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| pedometer-101      |    ✅     |     ✅      |  ❌   |   ❌    |    ❌     |
| andror2-7          |    ✅     |     ✅      |  ✅   |   ❌    |    ❌     |
| andror2-11         |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| andror2-23         |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| andror2-159        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| andror2-162        |    ✅     |     ✅      |  ❌   |   ❌    |    ❌     |
| andror2-164        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| andror2-168        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| andror2-198        |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| andror2-276        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-1         |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-2         |    ✅     |     ❌      |  ✅   |   ✅    |    ✅     |
| recdroid-3         |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-5         |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-7         |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-8         |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-9         |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-11        |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-12        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-13        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-14        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-15        |    ✅     |     ✅      |  ❌   |   ❌    |    ❌     |
| recdroid-17        |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-21        |    ✅     |     ❌      |  ✅   |   ✅    |    ❌     |
| recdroid-23        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-24        |    ✅     |     ✅      |  ❌   |   ✅    |    ❌     |
| recdroid-25        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-26        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-27        |    ✅     |     ✅      |  ✅   |   ✅    |    ❌     |
| recdroid-28        |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-29        |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-30        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-31        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-33        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-34        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-35        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-38        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-39        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-42        |    ✅     |     ❌      |  ✅   |   ✅    |    ❌     |
| recdroid-45        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-49        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-53        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-55        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-56        |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| recdroid-57        |    ✅     |     ❌      |  ✅   |   ❌    |    ❌     |
| recdroid-58        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| recdroid-60        |    ✅     |     ✅      |  ❌   |   ❌    |    ❌     |
| recdroid-61        |    ✅     |     ✅      |  ❌   |   ❌    |    ✅     |
| recdroid-62        |    ✅     |     ❌      |  ✅   |   ❌    |    ❌     |
| recdroid-64        |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| saner2022-2        |    ✅     |     ✅      |  ❌   |   ❌    |    ✅     |
| saner2022-8        |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| saner2022-11       |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| saner2022-18       |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| saner2022-23       |    ❌     |     ❌      |  ✅   |   ❌    |    ❌     |
| saner2022-129      |    ❌     |     ✅      |  ❌   |   ❌    |    ❌     |
| saner2022-271      |    ❌     |     ❌      |  ✅   |   ❌    |    ❌     |
| saner2022-1089     |    ✅     |     ✅      |  ✅   |   ✅    |    ✅     |
| saner2022-1096     |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| saner2022-1133     |    ✅     |     ❌      |  ✅   |   ✅    |    ✅     |
| saner2022-1160     |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| saner2022-1207     |    ✅     |     ✅      |  ✅   |   ✅    |    ❌     |
| saner2022-1215     |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| saner2022-1227     |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| saner2022-1299     |    ❌     |     ✅      |  ❌   |   ❌    |    ❌     |
| saner2022-1430     |    ✅     |     ✅      |  ✅   |   ✅    |    ❌     |
| saner2022-1447     |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| saner2022-1568     |    ❌     |     ❌      |  ❌   |   ❌    |    ❌     |
| saner2022-1645     |    ✅     |     ❌      |  ✅   |   ❌    |    ❌     |
| yakusu-1           |    ❌     |     ✅      |  ❌   |   ❌    |    ❌     |
| yakusu-35          |    ✅     |     ❌      |  ❌   |   ❌    |    ❌     |
| yakusu-98          |    ✅     |     ❌      |  ❌   |   ❌    |    ✅     |