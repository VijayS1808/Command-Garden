# 🌱 Command Garden

**Your personal offline library for Linux commands, scripts, notes, images, and links.**

Command Garden is a native Linux desktop app with a colourful dark interface, emoji, a text editor, and local storage. Save useful commands and reference material in one place and find them quickly.

## ✨ Features

| Feature | What you can do |
| --- | --- |
| ⚡ Commands | Save terminal commands and copy them when needed. |
| 🐍 Scripts | Store scripts with basic syntax highlighting. |
| 📝 Notes | Write Markdown notes and read them in Preview. |
| 🔗 Links | Save web links and open a selected URL in your browser. |
| 🖼 Images | Attach images to any entry and view or export them. |
| 🎨 Colours | Choose Lavender, Mint, Peach, Sky, or Rose for entries. |
| 😀 Emoji | Choose an emoji or enter your own. |
| 📁 Categories | Organise entries into categories such as Linux, Recon, or PCBA. |
| 🏷 Tags | Add comma-separated tags and search for them. |
| ⭐ Favourites | Mark important items and filter the favourites list. |
| 🔍 Search | Search titles, content, categories, and tags. |
| ↕ Sorting | Sort by recently edited or title. |
| 💾 Autosave | Save edits automatically after a short pause. |
| 📦 Backups | Export and import entries with their images as a ZIP backup. |
| 🔒 Local storage | Keep your content on your PC without an account. |

> The app stores and copies commands and scripts. It does not execute them.

## 🐧 Requirements

- A Linux graphical desktop session.
- Python 3.9 or later.
- PyQt5 with Qt 5.15.
- An emoji font for emoji display.
- Internet access for installing missing system packages. The app works offline after setup.

The installation instructions below target **Kali Linux, Debian, Ubuntu, and Linux Mint**. The app was tested in an offscreen Linux Qt environment; installation on every distribution and desktop has not been tested.

## 📥 Installation

### 1. Extract the app

Download `Command-Garden-Linux.zip` and extract it using your archive manager.

Open the extracted `command-garden` folder. Right-click inside the folder and select **Open Terminal Here**, if your file manager provides this option.

The folder should contain:

```text
command-garden/
├── app.py
├── store.py
├── install.sh
├── icon.svg
├── README.md
└── test_app.py
```

### 2. Install dependencies

```bash
sudo apt update
sudo apt install python3-pyqt5 fonts-noto-color-emoji
```

### 3. Install Command Garden

From inside the extracted folder:

```bash
bash install.sh
```

**Run this command as your normal desktop user, without sudo.** The installer creates a launcher for that user.

### 4. Launch the app

Search for **Command Garden** in your application menu, or run:

```bash
~/.local/bin/command-garden
```

### Run directly without installing a launcher

After installing the dependencies, run this from the extracted folder:

```bash
/usr/bin/python3 app.py
```

On other Linux distributions, install Python 3 and PyQt5 using your distribution's package manager, then run `app.py` with the Python interpreter that has PyQt5 installed. The supplied installer uses `/usr/bin/python3`.

## 🚀 Usage

### Create your first entry

1. Click **＋ New item** or press **Ctrl+N**.
2. Select **Command**, **Script**, **Note**, **Link**, or **Image**.
3. Enter a title.
4. Choose an emoji and colour.
5. Enter a category and optional tags.
6. Add your content in **Editor**.
7. Wait for **✓ Saved locally**, or press **Ctrl+S**.

Edits autosave after approximately 650 milliseconds of inactivity. Autosave also runs when switching entries or closing the app. If saving fails, the app shows an error and retains the unsaved text in the editor.

### ⚡ Save a command

Example entry:

| Field | Example |
| --- | --- |
| Title | Search text in files |
| Type | Command |
| Category | Linux |
| Tags | search, files, terminal |
| Emoji | 🔍 |

Paste this into the editor:

```bash
# Search recursively and show line numbers
rg -n "search phrase" ./notes
```

Click **Copy** to copy the complete editor content to your clipboard. You can then paste it into a terminal when you want to use it.

### 🐍 Save a script

Create a **Script** entry and paste your script into the editor.

You can also click **Import text** and select a UTF-8 script or text file. If the entry already has text, the app asks before replacing it.

- Maximum text import size: **2 MB**.
- Imported text becomes a local copy in the app.
- Later changes to the original file do not update the saved entry.
- Syntax highlighting is basic and is not a script validator.

### 📝 Write formatted notes

Create a **Note** entry. Use Markdown in **Editor**, then click **Preview**.

```markdown
# My Linux notes

**Important:** Make a backup before major changes.

*Reminder:* Review saved commands.

- Read the documentation
- Save useful examples

- [ ] Complete this task

Use `pwd` to display the current directory.

[Python documentation](https://docs.python.org/3/)
```

Toolbar buttons insert Markdown:

| Button | Action |
| --- | --- |
| B | Wrap selected text in `**bold**` markers. |
| I | Wrap selected text in `*italic*` markers. |
| Code | Wrap selected text in backticks. |
| ☑ List | Insert a Markdown task-list marker. |
| Link | Insert a sample Markdown link to edit. |

The editor stores plain text with Markdown markers. Preview renders supported Markdown. Command and Script previews display plain text.

### 🔗 Save and open links

1. Create a **Link** entry.
2. Paste a complete URL beginning with `https://` or `http://`.
3. Add any notes around it.
4. Click **Open link ↗**.
5. Choose a URL and confirm to open it in your browser.

You can keep several links in one entry. Opening an online page requires a network connection.

### 🖼 Add images

1. Select or create an entry.
2. Click **＋ Add image**.
3. Choose one or more images.
4. Double-click an attachment to view it.

The image window lets you **Save image as…** or **Remove attachment**.

- Supported file choices: PNG, JPG/JPEG, WebP, GIF, and BMP, subject to installed Qt image support.
- Maximum size: **20 MB per image**.
- Images are copied into the local database. Moving the original file does not remove the attachment.
- GIF previews show a static frame.
- Attachments are listed below the editor; they are not inserted inline into notes.

### 🔍 Find and organise entries

- Use the left sidebar to filter by entry type or **Favourites**.
- Click the star on an entry to mark or unmark it as a favourite.
- Enter a category such as `Linux`, `Bug Bounty`, `PCBA`, or `Learning`.
- Use the category dropdown above the list to filter entries.
- Search by title, content, category, or tags.
- Select **Recently edited** or **Title A → Z** to change the order.
- Drag the divider between the list and editor to adjust their widths.

### 🗑 Delete an entry

Select the entry and click **Delete**. Confirm the prompt to delete the entry and its attachments.

**Deletion has no undo.** Export a backup before removing important content.

## ⌨️ Keyboard shortcuts

| Shortcut | Action |
| --- | --- |
| Ctrl+N | Create a new entry. |
| Ctrl+S | Save the current entry immediately. |
| Ctrl+F | Focus the search box. |

## 💾 Local storage

Default data location:

```text
~/.local/share/command-garden/garden.sqlite3
```

If `XDG_DATA_HOME` is set, the data folder is:

```text
$XDG_DATA_HOME/command-garden/
```

Entries and image attachments are stored in SQLite. SQLite may also create companion files while the app is open. Use **Export backup** for a complete portable copy instead of copying only the database while the app is running.

Program installation locations:

```text
~/.local/share/command-garden-app/
~/.local/bin/command-garden
~/.local/share/applications/command-garden.desktop
```

The program folder and your saved-data folder are separate. Only one app instance can use a data folder at a time.

## 📦 Backup and restore

### Export a backup

1. Click **↗ Export backup** in the sidebar.
2. Choose a destination and ZIP filename.
3. Save the file.
4. Copy it to another drive if you want protection against PC loss or disk failure.

The ZIP includes all entries and image attachments.

### Import a backup

1. Click **↙ Import backup**.
2. Select a Command Garden backup ZIP.
3. Confirm the import.

Existing entries remain unchanged. Imported entries are added as **new copies**. Repeated imports create duplicates.

Maximum total uncompressed backup import size: **256 MB**. Export does not enforce this limit, so very large collections may produce backups beyond the current import limit.

> Autosave is not a backup. The app does not automatically create backups or synchronise to another device.

## 🔐 Privacy and limitations

- No account, telemetry, or cloud sync is built into the app.
- Content is stored under your local user account.
- The database and exported backups are **not encrypted**.
- This app is not a password manager.
- No command execution, automatic backup, or GitHub sync is included.
- Basic code colouring does not check whether commands are valid or safe.

## 🔄 Update the app

1. Export a backup.
2. Close Command Garden.
3. Extract the new app version.
4. Open a terminal in its `command-garden` folder.
5. Run:

```bash
bash install.sh
```

The installer replaces program files while keeping your saved-data folder.

## 🛠 Troubleshooting

### “No module named PyQt5”

Install the dependency:

```bash
sudo apt install python3-pyqt5
```

Run the app using the system Python from the extracted app folder:

```bash
/usr/bin/python3 app.py
```

### The installer says not to run as root

Use a terminal opened by your normal desktop account. Run `bash install.sh` without `sudo`. Use `sudo` only for installing system packages.

### The app is missing from the application menu

Launch it directly:

```bash
~/.local/bin/command-garden
```

If the launcher is missing, rerun `bash install.sh` from the extracted folder. Some desktops may need a logout and login before showing a new menu entry.

### “install.sh: No such file or directory”

Your terminal is in the wrong folder. Open the extracted `command-garden` folder and start a terminal there. Confirm that it contains `install.sh`:

```bash
ls
```

### Emoji appear as empty squares

Install the emoji font and restart the app:

```bash
sudo apt install fonts-noto-color-emoji
```

Emoji appearance depends on your installed fonts and Qt environment.

### Qt reports that it cannot connect to a display

Launch the app from a terminal inside your normal Linux graphical desktop session. It needs a working desktop display and will not show a window in a plain headless terminal.

### “Command Garden is already open”

Check your desktop for the existing window. The app prevents simultaneous access to the same data folder. If no window is visible, inspect running processes before restarting your desktop session.

### An image cannot be imported

Check that the file is a supported image, is not damaged, and is smaller than 20 MB. If a format is unavailable in your Qt installation, try PNG or JPEG.

### A backup cannot be imported

Select a ZIP created by **Export backup**, not the app installation ZIP. Check that it is intact and within the 256 MB uncompressed import limit. A failed import should leave existing entries unchanged.

### A save fails

Keep the app open and copy important editor text to a separate file. Check available disk space and write access to your data folder. The app retains unsaved editor text when a save fails.

## 🧹 Uninstall

Close the app. Using your file manager, remove these program files:

```text
~/.local/share/command-garden-app/
~/.local/bin/command-garden
~/.local/share/applications/command-garden.desktop
```

Your saved entries remain in the separate data folder. Export a backup before deleting that folder if you also want to remove all saved content.

## 🧪 Source code and tests

| File | Purpose |
| --- | --- |
| `app.py` | Desktop interface, editor, search, and attachment controls. |
| `store.py` | SQLite storage and ZIP backup export/import. |
| `install.sh` | Per-user installation and application-menu launcher. |
| `icon.svg` | Application icon. |
| `test_app.py` | Persistence, backup recovery, invalid-import, and editor-switching checks. |

From the source folder, run:

```bash
QT_QPA_PLATFORM=offscreen /usr/bin/python3 -m unittest -v test_app.py
```

The included checks passed in an offscreen Linux Qt test session. They do not replace testing on your own desktop.
