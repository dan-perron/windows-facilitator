from app_factory import create_app
from agent.service import OOTPScreenshotMonitor, debug_manager

app = create_app()

screenshot_monitor = None

def start_ootp_screenshot_monitor():
    global screenshot_monitor
    if screenshot_monitor is None:
        screenshot_monitor = OOTPScreenshotMonitor(debug_manager)
        screenshot_monitor.start()

if __name__ == "__main__":
    start_ootp_screenshot_monitor()
    app.run(host="0.0.0.0", port=5050, debug=True) 