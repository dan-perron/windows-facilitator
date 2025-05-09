# windows-facilitator

## Setup & Configuration

### 1. Create and Activate a Virtual Environment (Recommended)

It is strongly recommended to use a Python virtual environment to avoid dependency conflicts:

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies

Make sure you have Python 3.7+ installed. Then, install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure Slack Integration

This application can send debug screenshots and messages to a Slack channel. To enable this:

1. **Create a Slack App** (if you don't have one):
   - Go to https://api.slack.com/apps and create a new app.
   - Add the following OAuth scopes: `chat:write`, `files:write`.
   - Install the app to your workspace and copy the **Bot User OAuth Token** (starts with `xoxb-`).

2. **Find Your Channel ID:**
   - In Slack, right-click the channel name and choose "Copy Link". The part after `/archives/` is your channel ID (e.g., `C1234567890`).

3. **Configure Credentials:**
   - Copy `config.env` to your project root (it is already git-ignored).
   - Fill in your values:
     ```env
     SLACK_BOT_TOKEN=your-slack-bot-token-here
     SLACK_CHANNEL=your-slack-channel-id-here
     ```

### 4. Run the Application

Start the Flask server:

```bash
python main.py
```

The app will load your Slack credentials from `config.env` automatically.

### 5. (Recommended) Run at Login with Windows Task Scheduler

To ensure the app can interact with the OOTP window, use Windows Task Scheduler to run it at login in your user session:

#### a. Open Task Scheduler
- Press `Win + R`, type `taskschd.msc`, and press Enter.

#### b. Create a New Task
- In the right pane, click **Create Task...**
- **Name:** e.g., `OOTP Facilitator`
- **User:** Make sure your user account is selected.
- **Security options:** Select **Run only when user is logged on** (crucial for GUI interaction).

#### c. Triggers Tab
- Click **New...**
- **Begin the task:** On logon
- **Settings:** Any user (or just your user)
- Click **OK**.

#### d. Actions Tab
- Click **New...**
- **Action:** Start a program
- **Program/script:** Path to your Python executable (e.g., `C:\Users\youruser\venv\Scripts\python.exe`)
- **Add arguments:** The script to run, e.g., `main.py`
- **Start in:** The folder where your script is, e.g., `C:\Users\youruser\repos\windows-facilitator`
- Click **OK**.

#### e. Conditions/Settings
- (Optional) Uncheck **Start the task only if the computer is on AC power** if you want it to run on battery.
- (Optional) Check **Restart the task if it fails** for reliability.

#### f. Save and Test
- Click **OK** to save.
- Log out and log back in, or reboot, to test.

#### g. Log File Location
- All logs are written to: `C:\Users\<youruser>\Documents\ootp_logs\stdout.log`
- Open this file in any text editor to view logs.

---

#### Troubleshooting: OOTP Window Not Found
If you see errors like:
```
{"message": "Could not find OOTP window", "status": "error"}
```
Make sure you used Task Scheduler and selected **Run only when user is logged on**. The app must run in your interactive session to see the OOTP window.

---

#### Troubleshooting: Installing numpy on Windows

If you encounter errors when installing `numpy` with pip (such as build failures or missing compilers), you can install numpy using Chocolatey:

```
choco install numpy
```

After installing numpy with Chocolatey, retry installing opencv-python:

```
pip install opencv-python
```

This can help resolve issues with building numpy from source on Windows systems.

## Security
- **Never check your `config.env`