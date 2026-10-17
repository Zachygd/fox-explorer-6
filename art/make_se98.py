#!/usr/bin/env python3
"""Copy the SE98 icons Fox Explorer uses into theme/fe6/se98/ and write se98.css.

SE98 is nestoris's Windows 98 SE style icon theme (https://github.com/nestoris/Win98SE),
licensed GPL-2.0; its licence and credits are copied alongside the icons.

Usage:  art/make_se98.py /path/to/Win98SE   (a clone of the SE98 repository)

Each Fox Explorer icon gets two files: NAME.png (22x22, for toolbars) and NAME-16.png
(16x16, for menus, panels, the sidebar, the Library and the status bar). Run this again
after changing ICONS below; the result is committed, so builds don't need the SE98 repo.
"""
import os, shutil, subprocess, sys

# Fox Explorer icon name -> SE98 icon name. Icons that show Microsoft logos (the IE "e",
# the Windows flag) are deliberately not used.
ICONS = {
    "back": "go-previous",
    "forward": "go-next",
    "stop": "process-stop",
    "refresh": "view-refresh",
    "home": "go-home",
    "search": "system-search",
    "favorites": "bookmarks",
    "history": "history",
    "mail": "mail-message-new",
    "print": "document-print",
    "downloads": "download",
    "extensions": "preferences-plugin",
    "sidebar": "view-dual",
    "go": "go-next",
    "account": "user-identity",
    "newtab": "tab-new",
    "newwindow": "window-new",
    "open": "document-open",
    "save": "document-save",
    "cut": "edit-cut",
    "copy": "edit-copy",
    "paste": "edit-paste",
    "find": "edit-find",
    "zoom-in": "zoom-in",
    "zoom-out": "zoom-out",
    "fullscreen": "view-fullscreen",
    "settings": "preferences-system",
    "forget": "user-trash",
    "private": "security-high",
    "fxview": "folder-saved-search",
    "developer": "utilities-terminal",
    "screenshot": "applets-screenshooter",
    "import": "document-import",
    "library": "system-file-manager",
    "key": "dialog-password",
    "share": "document-share",
    "synced": "emblem-synchronizing-symbolic",
    "sendtab": "document-send",
    "encoding": "font-x-generic",
    "tabgroups": "document-multiple",
    "splitview": "view-split-left-right",
    "pip": "video-display",
    "folder": "folder",
    "folder-favorites": "folder-favorites",
    "tag": "tag",
    "day": "calendar",
    "lock": "emblem-locked",
    "globe": "globe-symbolic",
    "computer": "computer",
    "chat": "system-users",
    "reader": "text-x-readme",
    "monitor": "utilities-system-monitor",
    "customize": "preferences-desktop-theme",
}

# Which CSS selectors use which icon (Firefox element ids). Toolbar placements get the
# 22px icon, everything else (menus, the overflow panel, app menu) the 16px one.
BUTTONS = {
    "back": ["#back-button"], "forward": ["#forward-button"],
    "stop": ["#fe6-stop-button", "#stop-button"], "refresh": ["#fe6-refresh-button", "#reload-button"],
    "home": ["#home-button"], "search": ["#fe6-search-button"],
    "favorites": ["#fe6-favorites-button", "#bookmarks-menu-button", "#bookmarks-toolbar-button"],
    "history": ["#fe6-history-button", "#history-panelmenu"],
    "mail": ["#fe6-mail-button", "#email-link-button"], "print": ["#fe6-print-button", "#print-button"],
    "downloads": ["#downloads-button"], "extensions": ["#unified-extensions-button"],
    "sidebar": ["#sidebar-button"], "account": ["#fxa-toolbar-menu-button"],
    "newtab": ["#new-tab-button"], "newwindow": ["#new-window-button"],
    "open": ["#open-file-button"], "save": ["#save-page-button"],
    "cut": ["#cut-button"], "copy": ["#copy-button"], "paste": ["#paste-button"],
    "find": ["#find-button"], "zoom-in": ["#zoom-in-button"], "zoom-out": ["#zoom-out-button"],
    "fullscreen": ["#fullscreen-button"], "settings": ["#preferences-button"],
    "forget": ["#panic-button"], "private": ["#privatebrowsing-button"],
    "fxview": ["#firefox-view-button"], "developer": ["#developer-button"],
    "screenshot": ["#screenshot-button"], "import": ["#import-button"],
    "library": ["#library-button"], "key": ["#logins-button"],
    "share": ["#share-tab-button", "#share-button"], "synced": ["#sync-button"],
    "sendtab": ["#send-tab-button"], "encoding": ["#characterencoding-button"],
    "tabgroups": ["#tab-groups-button"], "splitview": ["#split-view-button"],
    "pip": ["#picture-in-picture-button"],
}
TOOLBARS = ":is(#nav-bar, #toolbar-menubar, #TabsToolbar, #PersonalToolbar, #customization-palette, .customization-target)"


def find_icon(root, name, size):
    for cat in sorted(os.listdir(root)):
        p = os.path.join(root, cat, str(size), name + ".png")
        if os.path.exists(p):
            return os.path.realpath(p)
    return None


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    repo = sys.argv[1]
    root = os.path.join(repo, "SE98")
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "..", "theme", "fe6", "se98")
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for ours, theirs in ICONS.items():
        for size, suffix in ((22, ""), (16, "-16")):
            src = find_icon(root, theirs, size)
            dst = os.path.join(out, ours + suffix + ".png")
            if src:
                shutil.copyfile(src, dst)
            else:
                # no icon at this size: centre the nearest smaller one, never blur-scale
                small = find_icon(root, theirs, 16)
                if not small:
                    sys.exit(f"SE98 has no {theirs} icon")
                subprocess.run(["convert", small, "-background", "none", "-gravity", "center",
                                "-extent", f"{size}x{size}", dst], check=True)
    shutil.copyfile(os.path.join(repo, "LICENSE"), os.path.join(out, "LICENSE"))
    with open(os.path.join(out, "README.md"), "w") as f:
        f.write("# SE98 icons\n\nThese icons are from **SE98** by nestoris "
                "(https://github.com/nestoris/Win98SE), licensed under the GNU GPL version 2 "
                "(see LICENSE in this folder). They are unmodified copies, renamed to the names "
                "Fox Explorer uses; `art/make_se98.py` lists which SE98 icon each one is.\n\n"
                "The one exception is `downloading.png`, the Downloads button animation: "
                "`art/make_download_anim.py` draws its frames over SE98's download icon, so it is "
                "a modified SE98 icon and is also under the GPL-2.0.\n")

    css = ["/* Generated by art/make_se98.py: SE98 icons by nestoris (GPL-2.0), see se98/README.md */"]
    for name, sels in BUTTONS.items():
        small = ", ".join(f"{s}, {s} .toolbarbutton-icon" for s in sels)
        big = ", ".join(f"{TOOLBARS} {s}, {TOOLBARS} {s} .toolbarbutton-icon" for s in sels)
        css.append(f'{small} {{ list-style-image: url("{name}-16.png") !important; }}')
        css.append(f'{big} {{ list-style-image: url("{name}.png") !important; }}')
    css += [
        '#fe6-go-button, #fe6-go-button .toolbarbutton-icon { list-style-image: url("go-16.png") !important; }',
        '#downloads-indicator-icon { list-style-image: url("downloads.png") !important; }',
        '#PersonalToolbar toolbarbutton.bookmark-item[container] { list-style-image: url("folder-16.png") !important; }',
        '#fe6-status-lock { list-style-image: url("lock-16.png") !important; }',
        '#fe6-status-zone-icon { list-style-image: url("globe-16.png") !important; }',
        '#fe6-status-zone[zone="local"] #fe6-status-zone-icon { list-style-image: url("computer-16.png") !important; }',
        '#tabs-newtab-button, #tabbrowser-tabs .tabs-newtab-button { list-style-image: url("newtab-16.png") !important; }',
        # Library / bookmarks / history trees
        'treechildren::-moz-tree-image(title, open), treechildren::-moz-tree-image(query),'
        ' treechildren::-moz-tree-image(title, query, hostContainer), treechildren::-moz-tree-image(title, query, folder)'
        ' { list-style-image: url("folder-16.png") !important; }',
        'treechildren::-moz-tree-image(container, queryFolder_menu________) { list-style-image: url("folder-favorites-16.png") !important; }',
        'treechildren::-moz-tree-image(query, OrganizerQuery_allbms_____v) { list-style-image: url("favorites-16.png") !important; }',
        'treechildren::-moz-tree-image(query, OrganizerQuery_downloads__v) { list-style-image: url("downloads-16.png") !important; }',
        'treechildren::-moz-tree-image(query, OrganizerQuery_tags_______v) { list-style-image: url("tag-16.png") !important; }',
        'treechildren::-moz-tree-image(title, query, dayContainer) { list-style-image: url("day-16.png") !important; }',
        'treechildren::-moz-tree-image(query, OrganizerQuery_history____v) { list-style-image: url("history-16.png") !important; }',
        # the sidebar header shows which panel is open
        '#sidebar-box[sidebarcommand="viewBookmarksSidebar"] #sidebar-icon { list-style-image: url("favorites-16.png") !important; -moz-context-properties: none !important; }',
        '#sidebar-box[sidebarcommand="viewHistorySidebar"] #sidebar-icon { list-style-image: url("history-16.png") !important; -moz-context-properties: none !important; }',
        '#sidebar-box[sidebarcommand="viewTabsSidebar"] #sidebar-icon { list-style-image: url("synced-16.png") !important; -moz-context-properties: none !important; }',
        ':root:not([windowtype="navigator:browser"]) #back-button, :root:not([windowtype="navigator:browser"]) #back-button > .toolbarbutton-icon { list-style-image: url("back-16.png") !important; -moz-context-properties: none !important; fill: none !important; }',
        ':root:not([windowtype="navigator:browser"]) #forward-button, :root:not([windowtype="navigator:browser"]) #forward-button > .toolbarbutton-icon { list-style-image: url("forward-16.png") !important; -moz-context-properties: none !important; fill: none !important; }',
    ]
    with open(os.path.join(out, "se98.css"), "w") as f:
        f.write("\n".join(css) + "\n")
    print("wrote", len(ICONS) * 2, "icons and se98.css to", os.path.normpath(out))


if __name__ == "__main__":
    main()
