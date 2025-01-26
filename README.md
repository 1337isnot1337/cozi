# Cozi - Vencord Plugin Manager

```
  ____ ___ ________
 / ___/ _ \__  /_ _|
| |  | | | |/ / | |
| |__| |_| / /_ | |
 \____\___/____|___|
```

Made by **1337isnot1337**

## Usage
```bash
cozi [command] [arguments]
```

## Main Commands
- **`add`** `[git link | file]`  
  Add a plugin repository (single git link or file with git links).

- **`patch`**  
  Build & inject Vencord.

## Other Commands
- **`delete`** `[repo name]`  
  Remove a specific plugin repository.

- **`export`** `[file]`  
  Export plugin configuration to a file.

- **`import`** `[file]`  
  Import plugin configuration from a file.

- **`list`**  
  List all installed plugins.

- **`status`**  
  Display a detailed status report of Cozi.

- **`update`**  
  Update all plugins.

- **`uninstall`**  
  Uninstall all Cozi-related files.

- **`help`**  
  Show this help menu.

## Example
```bash
# Add Venfetch to plugins
cozi add https://git.nin0.dev/userplugins/venfetch

# Patch Vencord so you can use the plugin
cozi patch
```

Make sure you enable the plugins in settings!
