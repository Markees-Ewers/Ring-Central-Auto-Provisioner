# RingCentral Phone Provisioning Tool

This app scans a phone's MAC address and adds the phone to RingCentral. It
supports a USB barcode scanner and support for scanning with a camera.
-note that the camera is not as reliable as a barcode scanner, and may require multiple attempts to read.

## Before you start

You need:

- Google Chrome
- A RingCentral account that can add phones
- A USB barcode scanner, or a camera
- Python installed on Windows

For the camera option, install Tesseract OCR separately from
[the Windows Tesseract installer](https://github.com/UB-Mannheim/tesseract/wiki).

## Start the special Chrome profile

The app cannot connect to a normal Chrome window. It needs a separate Chrome
profile started with remote debugging enabled. You do not need to download or
create this profile yourself; the command below creates it automatically the
first time it runs.

1. Close every regular Chrome window.
2. Open **PowerShell**.
3. Before running it, understand what the command does: it finds your Chrome
   installation, creates a separate profile for the app, and starts Chrome
   with a connection that allows the app to control that window. It does not
   change your normal Chrome profile or saved passwords.
4. Paste this entire command and press **Enter**:

```powershell
$chrome = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $chrome) {
  Write-Error "Google Chrome was not found. Install Chrome, then run this command again."
} else {
  Start-Process $chrome -ArgumentList @(
    "--remote-debugging-port=9222",
    "--user-data-dir=$env:TEMP\ringcentral-bot-profile"
  )
}
```

The command searches the usual Chrome installation folders and opens Chrome
with the profile named `ringcentral-bot-profile`. If the profile does not
exist, Chrome creates it in the Windows temporary folder.

In the new Chrome window:

1. Sign in to RingCentral.
2. Open **Phones & Devices > Unassigned**.
3. Leave this page open while using the app.

Always use this new Chrome window while running the app. Do not start another
Chrome window normally, and do not close the PowerShell-launched window.

## Install and start the app

Open PowerShell in the project folder and run:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe video_scanner.py
```

Choose a phone model on the first screen, then choose the input method.

## Using a USB barcode scanner

Choose **USB Scanner**, select the phone model, and click **Continue**.
Click inside the scan box if necessary, then scan the phone's barcode. The
scanner should send an Enter key after each scan.

The app will:

1. Find the first RingCentral phone with serial number **N/A**.
2. Open **Set Up and Provision**.
3. Select the closest matching phone model.
4. Enter the scanned MAC address.
5. Finish the setup and return to the Unassigned page.

After it returns to the Unassigned page, scan the next phone.

## Using the camera

Choose **Camera**, select a camera and phone model, then click **Scan label**.
Place the entire phone label inside the guide box. The app reads the MAC
address from the picture and shows the result on screen.

Use **Stop scan** to stop a slow scan and **Back** to return to the previous
screen. A MAC prefix can be entered when the first three parts of the address
are known.

## If a phone is already in RingCentral

If RingCentral reports that the MAC address is already associated with another
line, the app rejects that phone, returns to the Unassigned page, and displays
a rejection message. You can then scan another phone.

## If the app cannot connect to Chrome

Check that:

- Chrome was started with the command in this README.
- You are using the new Chrome window created by that command.
- RingCentral is open to **Phones & Devices > Unassigned**.
- You did not close the PowerShell-launched Chrome window.

The app does not save your RingCentral password or copy your Chrome cookies.
