/* Fox Explorer 6 — chrome customisation layer.
 * Loaded once per process by foxexplorer.cfg (Firefox autoconfig). Everything here uses
 * public Firefox chrome APIs (CustomizableUI, gBrowser, StatusPanel, prefs), so extensions,
 * tabs, customise mode and about:preferences keep working. */

import { setTimeout, clearTimeout } from "resource://gre/modules/Timer.sys.mjs";

const CSS_URI = "resource://fe6/fe6.css";
const AGENT_CSS_URI = "resource://fe6/fe6-agent.css";
const CHROME_CSS_URI = "resource://fe6/fe6-chrome.css";
// Firefox UI documents that get the Win98 controls sheet (sidebar pages, Library, dialogs)
const CHROME_DOC_PREFIXES = [
  "chrome://browser/content/sidebar/",
  "chrome://browser/content/places/",
  "chrome://browser/content/genai/",
  "chrome://browser/content/syncedtabs/",
  "chrome://global/content/megalist/",
  "chrome://global/content/commonDialog",
  "chrome://browser/content/downloads/",
  "chrome://mozapps/content/downloads/",
  "chrome://browser/content/pageinfo/",
  "chrome://browser/content/sanitize",
  "chrome://browser/content/aboutDialog",
  "chrome://global/content/print.html",
];
// Optional: original IE6 icons converted from the user's own IE6 CD by scripts/import-ie6-icons.py
const IE6_CSS_URI = "resource://fe6/ie6/ie6.css";
let ie6IconsPresent = null;
function hasIE6Icons() {
  if (ie6IconsPresent === null) {
    try {
      const res = Services.io.getProtocolHandler("resource").QueryInterface(Ci.nsIResProtocolHandler);
      const spec = res.resolveURI(Services.io.newURI(IE6_CSS_URI));
      ie6IconsPresent = Services.io.newURI(spec).QueryInterface(Ci.nsIFileURL).file.exists();
    } catch (e) {
      ie6IconsPresent = false;
    }
  }
  return ie6IconsPresent;
}
const PREF = {
  scheme: "foxexplorer.colorScheme",       // "light" | "dark" | "system"
  statusbar: "foxexplorer.statusBar",      // bool
  caption: "foxexplorer.classicTitlebar",  // bool: draw the Win98 title bar
  historyMenu: "foxexplorer.showHistoryMenu",
  appMenu: "foxexplorer.showAppMenu",
  layout: "foxexplorer.layoutVersion",     // int, user pref: which default layout has been applied
};
const LAYOUT_VERSION = 3;
const XUL_NS = "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul";

/* CustomizableUI moved from resource:///modules/ to moz-src:/// around Firefox 150;
   try the current location first, then the old one. */
const CUI_URLS = [
  "moz-src:///browser/components/customizableui/CustomizableUI.sys.mjs",
  "resource:///modules/CustomizableUI.sys.mjs",
];
let cuiModule = null;
const lazy = {
  get CustomizableUI() {
    if (!cuiModule) {
      let lastErr;
      for (const url of CUI_URLS) {
        try {
          cuiModule = ChromeUtils.importESModule(url).CustomizableUI;
          if (cuiModule) break;
        } catch (e) {
          lastErr = e;
        }
      }
      if (!cuiModule) throw lastErr || new Error("CustomizableUI not found");
    }
    return cuiModule;
  },
  /* The search service used to be Services.search; current Firefox (157+) has it as a plain
     module (moz-src:///toolkit/components/search/SearchService.sys.mjs). */
  get SearchService() {
    if (!searchModule) {
      try {
        searchModule = Services.search || null;
      } catch (e) {}
      if (!searchModule) {
        searchModule = ChromeUtils.importESModule(
          "moz-src:///toolkit/components/search/SearchService.sys.mjs").SearchService;
      }
    }
    return searchModule;
  },
};
let searchModule = null;
function userChangeReason(svc) {
  return svc.CHANGE_REASON?.USER ?? Ci.nsISearchService?.CHANGE_REASON_USER ?? "user";
}

function getPref(name, def) {
  try {
    switch (Services.prefs.getPrefType(name)) {
      case Services.prefs.PREF_BOOL: return Services.prefs.getBoolPref(name);
      case Services.prefs.PREF_INT: return Services.prefs.getIntPref(name);
      case Services.prefs.PREF_STRING: return Services.prefs.getStringPref(name);
    }
  } catch (e) {}
  return def;
}

function log(...args) {
  if (getPref("foxexplorer.debug", false)) {
    const msg = "[Fox Explorer 6] " + args.map(a => (typeof a == "string" ? a : String(a))).join(" ");
    console.log(msg);
    dump(msg + "\n");
  }
}

/* ------------------------------------------------------------------ colour scheme */
function effectiveScheme(win) {
  const s = getPref(PREF.scheme, "light");
  if (s === "dark" || s === "light") return s;
  try {
    return win.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  } catch (e) {
    return "light";
  }
}

/* Make Firefox's own UI (about: pages, panels) and websites follow the chosen scheme too.
 * "system" clears the override so the desktop setting wins. */
function applyGlobalScheme() {
  const s = getPref(PREF.scheme, "light");
  if (s === "system") {
    Services.prefs.clearUserPref("ui.systemUsesDarkTheme");
  } else {
    Services.prefs.setIntPref("ui.systemUsesDarkTheme", s === "dark" ? 1 : 0);
  }
}

function setScheme(value) {
  Services.prefs.setStringPref(PREF.scheme, value);
}

/* ------------------------------------------------------------------ toolbar widgets */
/* Each IE6 button is wired to a <command> element (Firefox's own mechanism for its toolbar
   buttons): the button carries command="…", so clicks work regardless of CustomizableUI
   internals, and buttons follow their command's disabled state (e.g. Stop). Firefox's
   built-in commands are used where one exists; ours are added to every window. */
const FE6_COMMANDS = {
  "fe6-cmd-favorites": win => toggleSidebar(win, "viewBookmarksSidebar"),
  "fe6-cmd-history": win => toggleSidebar(win, "viewHistorySidebar"),
  "fe6-cmd-go": (win, ev) => {
    if (win.gURLBar.value) win.gURLBar.handleCommand(ev);
    else win.gURLBar.focus();
  },
  "fe6-cmd-search": win => openSearchMenu(win),
  "fe6-cmd-refresh": (win, ev) => {
    const bypass = ev && (ev.shiftKey || ev.ctrlKey);
    const id = bypass ? "Browser:ReloadSkipCache" : "Browser:Reload";
    const cmd = win.document.getElementById(id);
    if (cmd) cmd.doCommand();
    else if (win.BrowserCommands) bypass ? win.BrowserCommands.reloadSkipCache() : win.BrowserCommands.reload();
  },
};
const BUTTON_COMMANDS = {
  "fe6-stop-button": "Browser:Stop",
  "fe6-refresh-button": "fe6-cmd-refresh",
  "fe6-search-button": "fe6-cmd-search",
  "fe6-favorites-button": "fe6-cmd-favorites",
  "fe6-history-button": "fe6-cmd-history",
  "fe6-mail-button": "Browser:SendLink",
  "fe6-print-button": "cmd_print",
  "fe6-go-button": "fe6-cmd-go",
};

function toggleSidebar(win, id) {
  if (win.SidebarController) win.SidebarController.toggle(id);
  else if (win.SidebarUI) win.SidebarUI.toggle(id);
}

function installCommands(win) {
  const doc = win.document;
  const set = doc.getElementById("mainCommandSet") || doc.querySelector("commandset");
  if (!set) return;
  for (const [id, fn] of Object.entries(FE6_COMMANDS)) {
    if (doc.getElementById(id)) continue;
    const c = doc.createXULElement("command");
    c.id = id;
    c.addEventListener("command", ev => {
      try {
        fn(win, ev.sourceEvent || ev);
      } catch (e) {
        console.error("[Fox Explorer 6]", id, e);
      }
    });
    set.append(c);
  }
}

let widgetsCreated = false;
function createWidgets() {
  if (widgetsCreated) return;
  widgetsCreated = true;
  const CUI = lazy.CustomizableUI;
  const button = (id, label, tooltip) => {
    try {
      CUI.createWidget({
        id, label, tooltiptext: tooltip, type: "button",
        defaultArea: null, removable: true,
        onCreated(node) {
          node.setAttribute("command", BUTTON_COMMANDS[id]);
        },
      });
    } catch (e) { log("createWidget failed", id, e); }
  };
  button("fe6-stop-button", "Stop", "Stop");
  button("fe6-refresh-button", "Refresh", "Refresh (Shift+click: reload without cache)");
  button("fe6-favorites-button", "Favorites", "Favorites");
  button("fe6-history-button", "History", "History");
  button("fe6-mail-button", "Mail", "Mail a link to this page");
  button("fe6-print-button", "Print", "Print");
  button("fe6-go-button", "Go", "Go to the address in the Address bar");

  /* Search: an ordinary IE6 button (icon + label, beside Favorites) that drops down a menu
     of the installed search engines. Picking one makes it the default and puts the cursor in
     the Address bar, ready to type. The menu lives in #mainPopupSet, see openSearchMenu(). */
  button("fe6-search-button", "Search", "Choose a search engine");

  try {
    CUI.createWidget({
      id: "fe6-address-label", type: "custom", removable: true, defaultArea: null,
      label: "Address label",
      onBuild(doc) {
        const item = doc.createXULElement("toolbaritem");
        item.id = "fe6-address-label";
        item.setAttribute("label", "Address label");
        item.setAttribute("removable", "true");
        item.className = "chromeclass-toolbar-additional";
        const l = doc.createXULElement("label");
        l.setAttribute("value", "Address");
        l.setAttribute("control", "urlbar-input");
        l.addEventListener("click", () => doc.ownerGlobal.gURLBar.select());
        item.append(l);
        return item;
      },
    });
  } catch (e) { log("address label widget", e); }

  try {
    CUI.createWidget({
      id: "fe6-throbber", type: "custom", removable: true, defaultArea: null, label: "Activity indicator",
      onBuild(doc) {
        const item = doc.createXULElement("toolbaritem");
        item.id = "fe6-throbber";
        item.setAttribute("label", "Activity indicator");
        item.setAttribute("removable", "true");
        item.setAttribute("tooltiptext", "Fox Explorer 6");
        const img = doc.createXULElement("image");
        img.id = "fe6-throbber-img";
        item.append(img);
        item.addEventListener("click", () => {
          const w = doc.ownerGlobal;
          w.openTrustedLinkIn(w.HomePage ? w.HomePage.get(w).split("|")[0] : "about:home", "tab");
        });
        return item;
      },
    });
  } catch (e) { log("throbber widget", e); }
}

/* Search engines are cached so the menu can be built synchronously (async work inside
   popupshowing left the menu empty on some Firefox versions). The list is published as
   soon as it is known; icons are filled in afterwards, because current Firefox fetches
   engine icons on demand and one slow icon must never hold up the whole menu. */
let engineCache = { engines: [], current: "" };
let enginesLoading = null;
const iconCache = new Map();   // engine name -> icon URL

function withTimeout(promise, ms) {
  let timer;
  return Promise.race([
    promise,
    new Promise((_, reject) => { timer = setTimeout(() => reject(new Error("timed out")), ms); }),
  ]).finally(() => clearTimeout(timer));
}

function rebuildSearchMenus() {
  for (const w of Services.wm.getEnumerator("navigator:browser")) {
    const popup = w.document.getElementById("fe6-search-popup");
    if (popup) {
      try { fillSearchMenu(w, popup); } catch (e) { console.error("[Fox Explorer 6] search menu", e); }
    }
  }
}

function engineIcon(e) {
  if (typeof e.getIconURL == "function") return e.getIconURL(16);
  return Promise.resolve(e.iconURI?.spec || "");
}

function refreshEngines() {
  if (enginesLoading) return enginesLoading;
  enginesLoading = (async () => {
    try {
      const svc = lazy.SearchService;
      const [list, def] = await withTimeout(Promise.all([svc.getVisibleEngines(), svc.getDefault()]), 15000);
      const engines = list.map(e => ({ name: e.name, icon: iconCache.get(e.name) || "", engine: e }));
      const sig = c => c.current + "|" + c.engines.map(x => x.name + x.icon).join(",");
      const next = { engines, current: def?.name || "" };
      if (sig(next) !== sig(engineCache)) {   // unchanged: leave open menus alone
        engineCache = next;
        rebuildSearchMenus();
      }
      // icons, in parallel and each with its own time limit
      let gotNew = false;
      await Promise.all(engines.map(async entry => {
        try {
          const url = (await withTimeout(engineIcon(entry.engine), 5000)) || "";
          if (url && url !== entry.icon) {
            entry.icon = url;
            iconCache.set(entry.name, url);
            gotNew = true;
          }
        } catch (err) {}
      }));
      if (gotNew && engineCache.engines === engines) rebuildSearchMenus();
    } catch (e) {
      console.error("[Fox Explorer 6] could not load search engines", e);
      if (!engineCache.engines.length) {
        engineCache = { engines: [], current: "", failed: true };
        rebuildSearchMenus();
      }
    } finally {
      enginesLoading = null;
    }
  })();
  return enginesLoading;
}

function openSearchMenu(win) {
  const doc = win.document;
  let popup = doc.getElementById("fe6-search-popup");
  if (!popup) {
    popup = doc.createXULElement("menupopup");
    popup.id = "fe6-search-popup";
    popup.addEventListener("popupshowing", ev => {
      if (ev.target !== popup) return;
      fillSearchMenu(win, popup);
      refreshEngines();
    });
    popup.addEventListener("popuphidden", ev => {
      if (ev.target !== popup) return;
      doc.getElementById("fe6-search-button")?.removeAttribute("open");
    });
    (doc.getElementById("mainPopupSet") || doc.documentElement).append(popup);
  }
  if (popup.state === "open" || popup.state === "showing") {
    popup.hidePopup();
    return;
  }
  fillSearchMenu(win, popup);
  refreshEngines();
  const btn = doc.getElementById("fe6-search-button");
  const visible = btn && btn.getBoundingClientRect().width > 0 && !btn.closest("#widget-overflow, #customization-palette");
  if (visible) {
    btn.setAttribute("open", "true");
    popup.openPopup(btn, "after_start");
  } else {
    popup.openPopup(win.gURLBar?.inputField || doc.getElementById("urlbar"), "after_start");
  }
}

function fillSearchMenu(win, popup) {
  const doc = win.document;
  const item = (label, fn, extra = {}) => {
    const mi = doc.createXULElement("menuitem");
    mi.setAttribute("label", label);
    for (const [k, v] of Object.entries(extra)) mi.setAttribute(k, v);
    mi.addEventListener("command", fn);
    return mi;
  };
  const focusBar = () => { win.gURLBar.focus(); win.gURLBar.select(); };
  const kids = [item("Search the Web…", focusBar, { "fe6-bold": "true" }), doc.createXULElement("menuseparator")];
  if (!engineCache.engines.length) {
    kids.push(item(engineCache.failed ? "(no search engines found)" : "(loading search engines…)",
                   () => {}, { disabled: "true" }));
  }
  for (const e of engineCache.engines) {
    const attrs = { class: "menuitem-iconic" };
    if (e.icon) attrs.image = e.icon;
    if (e.name === engineCache.current) {
      attrs["fe6-bold"] = "true";
      attrs.tooltiptext = "Current search engine";
    }
    kids.push(item(e.name, async () => {
      try {
        const svc = lazy.SearchService;
        await svc.setDefault(e.engine, userChangeReason(svc));
        engineCache.current = e.name;
      } catch (err) {
        log("setDefault", err);
      }
      focusBar();
    }, attrs));
  }
  kids.push(doc.createXULElement("menuseparator"), item("Manage Search Engines…", () => win.openPreferences("paneSearch")));
  popup.replaceChildren(...kids);
}

/* One-time default layout (IE6 Standard Buttons). Re-run by setting foxexplorer.layoutVersion to 0. */
function applyDefaultLayout() {
  const have = getPref(PREF.layout, 0);
  if (have >= LAYOUT_VERSION) return;
  const CUI = lazy.CustomizableUI;
  if (have === 2) {
    /* v2 -> v3: the Search button was briefly a different kind of widget and could drop off
       the toolbar; put it back beside Favorites without touching the rest of the layout. */
    try {
      if (!CUI.getPlacementOfWidget("fe6-search-button")) {
        const fav = CUI.getPlacementOfWidget("fe6-favorites-button");
        if (fav) CUI.addWidgetToArea("fe6-search-button", fav.area, fav.position);
      }
    } catch (e) { log("layout migration", e); }
    Services.prefs.setIntPref(PREF.layout, LAYOUT_VERSION);
    return;
  }
  try {
    CUI.beginBatchUpdate();
    const nav = CUI.AREA_NAVBAR;
    // remove modern defaults that IE6 never had (they stay in the Customize palette)
    for (const id of ["stop-reload-button", "fxa-toolbar-menu-button", "save-to-pocket-button", "sidebar-button",
                      "firefox-view-button", "vertical-spacer", "alltabs-button"]) {
      try {
        const p = CUI.getPlacementOfWidget(id);
        if (p && (id !== "alltabs-button")) CUI.removeWidgetFromArea(id);
      } catch (e) {}
    }
    for (const w of CUI.getWidgetIdsInArea(nav)) {
      if (w.startsWith("customizableui-special-spring")) CUI.removeWidgetFromArea(w);
    }
    const order = [
      "back-button", "forward-button", "fe6-stop-button", "fe6-refresh-button", "home-button",
      "SEP",
      "fe6-search-button", "fe6-favorites-button", "fe6-history-button",
      "SEP",
      "fe6-mail-button", "fe6-print-button",
    ];
    let pos = 0;
    for (const id of order) {
      if (id === "SEP") {
        CUI.addWidgetToArea("separator", nav, pos++);
      } else {
        CUI.addWidgetToArea(id, nav, pos++);
      }
    }
    // Address row
    CUI.addWidgetToArea("fe6-address-label", nav);
    CUI.moveWidgetWithinArea("urlbar-container", CUI.getWidgetIdsInArea(nav).length);
    CUI.addWidgetToArea("fe6-go-button", nav);
    // throbber at the right end of the menu bar
    CUI.addWidgetToArea("fe6-throbber", CUI.AREA_MENUBAR);
    CUI.setToolbarVisibility(CUI.AREA_MENUBAR, true);
    CUI.setToolbarVisibility(CUI.AREA_BOOKMARKS, true);
  } catch (e) {
    log("layout failed", e);
  } finally {
    try { CUI.endBatchUpdate(); } catch (e) {}
  }
  Services.prefs.setIntPref(PREF.layout, LAYOUT_VERSION);
}

/* ------------------------------------------------------------------ per-window UI */
function el(doc, tag, attrs = {}, children = []) {
  const e = doc.createXULElement(tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  for (const c of children) e.append(c);
  return e;
}

function syncWindowAttrs(win) {
  const root = win.document.documentElement;
  root.setAttribute("fe6-scheme", effectiveScheme(win));
  root.toggleAttribute("fe6-caption", getPref(PREF.caption, true));
  root.toggleAttribute("fe6-statusbar-hidden", !getPref(PREF.statusbar, true));
  root.toggleAttribute("fe6-show-appmenu", getPref(PREF.appMenu, false));
  const hist = win.document.getElementById("history-menu");
  if (hist) hist.hidden = !getPref(PREF.historyMenu, false);
}

function buildCaption(win) {
  const doc = win.document;
  if (doc.getElementById("fe6-caption")) return;
  const toolbox = doc.getElementById("navigator-toolbox");
  const capbtn = (id, tip, fn) => {
    const b = el(doc, "toolbarbutton", { id, class: "fe6-capbtn", tooltiptext: tip });
    b.addEventListener("command", fn);
    return b;
  };
  const caption = el(doc, "hbox", { id: "fe6-caption" }, [
    el(doc, "image", { id: "fe6-caption-icon", src: "resource://fe6/icons/logo.png" }),
    el(doc, "label", { id: "fe6-caption-title", crop: "end" }),
    capbtn("fe6-cap-min", "Minimize", () => win.minimize()),
    capbtn("fe6-cap-max", "Maximize", () => {
      win.windowState === win.STATE_MAXIMIZED ? win.restore() : win.maximize();
    }),
    capbtn("fe6-cap-close", "Close", () => {
      if (win.BrowserCommands?.tryToCloseWindow) win.BrowserCommands.tryToCloseWindow();
      else if (win.BrowserTryToCloseWindow) win.BrowserTryToCloseWindow();
      else win.close();
    }),
  ]);
  caption.addEventListener("dblclick", e => {
    if (e.button === 0 && !e.target.classList.contains("fe6-capbtn")) {
      win.windowState === win.STATE_MAXIMIZED ? win.restore() : win.maximize();
    }
  });
  toolbox.prepend(caption);

  // mirror the window title ("Page - Fox Explorer 6")
  const titleLabel = caption.querySelector("#fe6-caption-title");
  const update = () => {
    const t = (doc.title || "").replace(/ — /g, " - ");
    titleLabel.setAttribute("value", t);
  };
  update();
  const mo = new win.MutationObserver(update);
  const titleEl = doc.querySelector("title") || doc.head || doc.documentElement;
  mo.observe(titleEl, { childList: true, characterData: true, subtree: true });
  win.addEventListener("unload", () => mo.disconnect(), { once: true });
}

function buildStatusBar(win) {
  const doc = win.document;
  if (doc.getElementById("fe6-statusbar")) return;
  const pane = (id, cls, kids) => el(doc, "hbox", { id, class: "fe6-pane " + (cls || "") }, kids);
  const bar = el(doc, "hbox", { id: "fe6-statusbar" }, [
    pane("fe6-status-main", "", [
      el(doc, "image", { id: "fe6-status-icon" }),
      el(doc, "label", { id: "fe6-status-text", value: "Done", crop: "end", flex: "1" }),
    ]),
    pane("fe6-status-progress", "", [el(doc, "hbox", { id: "fe6-status-meter" })]),
    pane("fe6-status-lockpane", "fe6-blank", [el(doc, "image", { id: "fe6-status-lock", tooltiptext: "Secure connection" })]),
    pane("fe6-status-blank2", "fe6-blank", []),
    pane("fe6-status-zone", "", [
      el(doc, "image", { id: "fe6-status-zone-icon" }),
      el(doc, "label", { id: "fe6-status-zone-label", value: "Internet" }),
    ]),
    el(doc, "resizer", { id: "fe6-status-grip", dir: "bottomright" }),
  ]);
  const browser = doc.getElementById("browser");
  browser.after(bar);


  const text = bar.querySelector("#fe6-status-text");
  const meter = bar.querySelector("#fe6-status-meter");
  const progressPane = bar.querySelector("#fe6-status-progress");
  const lockPane = bar.querySelector("#fe6-status-lockpane");
  const zone = bar.querySelector("#fe6-status-zone");
  const zoneLabel = bar.querySelector("#fe6-status-zone-label");
  const throbber = () => doc.getElementById("fe6-throbber");

  const state = { busy: false };
  const refreshText = () => {
    const xbw = win.XULBrowserWindow;
    let t = xbw?.overLink || (xbw?.busyUI ? xbw?.status : "") || xbw?.defaultStatus || "";
    if (!t) t = state.busy ? "Opening page " + (win.gBrowser.currentURI?.displaySpec || "") + "..." : "Done";
    text.setAttribute("value", t);
  };
  const setBusy = busy => {
    state.busy = busy;
    doc.documentElement.toggleAttribute("fe6-busy", busy);
    throbber()?.toggleAttribute("busy", busy);
    progressPane.toggleAttribute("active", busy);
    if (!busy) meter.style.width = "0%";
    refreshText();
  };
  const refreshLocation = () => {
    const uri = win.gBrowser.currentURI;
    const scheme = uri?.scheme || "";
    const local = ["file", "about", "chrome", "resource", "moz-extension"].includes(scheme);
    zone.setAttribute("zone", local ? "local" : "internet");
    zoneLabel.setAttribute("value", local ? "My Computer" : "Internet");
  };

  // keep Firefox's status logic, show the result in our bar
  if (win.StatusPanel && !win.StatusPanel.__fe6) {
    const orig = win.StatusPanel.update.bind(win.StatusPanel);
    win.StatusPanel.update = function () {
      try { orig(); } catch (e) {}
      refreshText();
    };
    win.StatusPanel.__fe6 = true;
  }

  const Ci_WPL = Ci.nsIWebProgressListener;
  const listener = {
    QueryInterface: ChromeUtils.generateQI(["nsIWebProgressListener", "nsISupportsWeakReference"]),
    onStateChange(webProgress, request, flags) {
      if (!webProgress.isTopLevel) return;
      if (flags & Ci_WPL.STATE_IS_NETWORK) {
        if (flags & Ci_WPL.STATE_START) setBusy(true);
        else if (flags & Ci_WPL.STATE_STOP) setBusy(false);
      }
    },
    onProgressChange(webProgress, request, curSelf, maxSelf, curTotal, maxTotal) {
      if (maxTotal > 0) meter.style.width = Math.min(100, Math.round((curTotal / maxTotal) * 100)) + "%";
    },
    onLocationChange() { refreshLocation(); refreshText(); },
    onStatusChange() { refreshText(); },
    onSecurityChange(webProgress, request, st) {
      lockPane.toggleAttribute("secure", !!(st & Ci_WPL.STATE_IS_SECURE));
    },
    onContentBlockingEvent() {},
  };
  win.gBrowser.addProgressListener(listener);
  const onTabSelect = () => {
    const b = win.gBrowser.selectedBrowser;
    setBusy(!!win.gBrowser.selectedTab?.hasAttribute("busy"));
    refreshLocation();
    try {
      const st = b.securityUI?.state || 0;
      lockPane.toggleAttribute("secure", !!(st & Ci_WPL.STATE_IS_SECURE));
    } catch (e) {}
  };
  win.gBrowser.tabContainer.addEventListener("TabSelect", onTabSelect);
  win.addEventListener("unload", () => {
    try { win.gBrowser.removeProgressListener(listener); } catch (e) {}
  }, { once: true });
  onTabSelect();
}

/* Sidebar launcher (newer Firefox): give its tools Win98 icons. */
const SIDEBAR_ICONS = {
  viewHistorySidebar: "history",
  viewBookmarksSidebar: "favorites",
  viewTabsSidebar: "synced",
  viewGenaiChatSidebar: "chat",
  viewGenaiPageAssistSidebar: "reader",
  viewCPMSidebar: "key",
  viewResourceMonitorSidebar: "monitor",
  viewCustomizeSidebar: "customize",
};
const IE6_SIDEBAR_ICONS = { history: "history-hot.png", favorites: "favorites-hot.png" };
function themeSidebarTools(win) {
  const SC = win.SidebarController;
  if (!SC || !SC.sidebars) return;
  let changed = false;
  // the launcher reads copies held in toolsAndExtensions, so update both maps
  let tools = null;
  try { tools = SC.toolsAndExtensions; } catch (e) {}
  for (const [id, name] of Object.entries(SIDEBAR_ICONS)) {
    const url = hasIE6Icons() && IE6_SIDEBAR_ICONS[name]
      ? "resource://fe6/ie6/" + IE6_SIDEBAR_ICONS[name]
      : "resource://fe6/icons/" + name + ".svg";
    for (const entry of [SC.sidebars.get?.(id), tools?.get?.(id)]) {
      if (entry && entry.iconUrl !== url) {
        entry.iconUrl = url;
        changed = true;
      }
    }
  }
  if (changed) {
    const main = win.document.querySelector("sidebar-main");
    main?.requestUpdate?.();
  }
}

/* Firefox 150+ treats the mere presence of checked="…" as checked, so remove it to uncheck. */
function setChecked(node, on) {
  if (on) node.setAttribute("checked", "true");
  else node.removeAttribute("checked");
}

/* menus: File Edit View Favorites Tools Help */
function relabel(doc, id, label, accesskey) {
  const n = doc.getElementById(id);
  if (!n) return null;
  n.removeAttribute("data-l10n-id");
  n.setAttribute("label", label);
  if (accesskey) n.setAttribute("accesskey", accesskey);
  return n;
}

function buildMenus(win) {
  const doc = win.document;
  if (doc.getElementById("fe6-scheme-menu")) return;
  relabel(doc, "bookmarksMenu", "Favorites", "a");
  relabel(doc, "menu_bookmarkThisPage", "Add to Favorites...", "A");
  relabel(doc, "bookmarksShowAll", "Organize Favorites...", "O");

  // View > Status Bar, View > Color Scheme
  const viewPopup = doc.getElementById("menu_viewPopup");
  if (viewPopup) {
    const sb = el(doc, "menuitem", { id: "fe6-statusbar-item", type: "checkbox", label: "Status Bar", accesskey: "B" });
    sb.addEventListener("command", () => Services.prefs.setBoolPref(PREF.statusbar, !getPref(PREF.statusbar, true)));
    const popup = el(doc, "menupopup", { id: "fe6-scheme-popup" });
    const items = [["light", "Light (Classic)"], ["dark", "Dark"], ["system", "Use System Setting"]];
    for (const [v, l] of items) {
      const mi = el(doc, "menuitem", { type: "radio", name: "fe6-scheme", label: l, value: v });
      mi.addEventListener("command", () => setScheme(v));
      popup.append(mi);
    }
    popup.addEventListener("popupshowing", () => {
      const cur = getPref(PREF.scheme, "light");
      for (const mi of popup.children) setChecked(mi, mi.getAttribute("value") === cur);
    });
    viewPopup.addEventListener("popupshowing", () => setChecked(sb, getPref(PREF.statusbar, true)));
    const schemeMenu = el(doc, "menu", { id: "fe6-scheme-menu", label: "Color Scheme", accesskey: "C" }, [popup]);
    const anchor = doc.getElementById("viewToolbarsMenu");
    if (anchor) {
      anchor.after(sb);
      sb.after(schemeMenu);
    } else {
      viewPopup.prepend(sb, schemeMenu);
    }
  }

  // Tools > Internet Options...
  const tools = doc.getElementById("menu_ToolsPopup");
  if (tools) {
    const opt = el(doc, "menuitem", { id: "fe6-internet-options", label: "Internet Options...", accesskey: "O" });
    opt.addEventListener("command", () => win.openPreferences());
    tools.append(el(doc, "menuseparator"), opt);
  }
}

function initWindow(win) {
  const doc = win.document;
  if (doc.documentElement.getAttribute("windowtype") !== "navigator:browser") return;
  for (const [name, fn] of [["commands", installCommands], ["attrs", syncWindowAttrs], ["caption", buildCaption], ["statusbar", buildStatusBar], ["menus", buildMenus]]) {
    try {
      fn(win);
    } catch (e) {
      console.error(`[Fox Explorer 6] ${name} failed`, e);
    }
  }
  try {
    themeSidebarTools(win);
    win.setTimeout(() => { try { themeSidebarTools(win); } catch (e) {} }, 2500);
    win.SidebarController?.promiseInitialized?.then(() => themeSidebarTools(win)).catch(() => {});
  } catch (e) {
    console.error("[Fox Explorer 6] sidebar icons failed", e);
  }
  try {
    // follow desktop light/dark changes while in "system" mode
    const mq = win.matchMedia("(prefers-color-scheme: dark)");
    mq.addEventListener("change", () => syncWindowAttrs(win));
    win.setTimeout(() => {
      const r = doc.documentElement;
      log("root attrs:", [...r.attributes].map(a => a.name + "=" + a.value).join(" "));
      log("navbar:", lazy.CustomizableUI.getWidgetIdsInArea("nav-bar").join(","));
      log("menubar:", lazy.CustomizableUI.getWidgetIdsInArea("toolbar-menubar").join(","));
    }, 3000);
  } catch (e) {
    console.error("[Fox Explorer 6] window init failed", e);
  }
}

/* stylesheet goes in as early as possible so there's no flash of the stock UI */
function injectSheet(win) {
  try {
    if (win.__fe6Sheet) return;
    win.__fe6Sheet = true;
    win.windowUtils.loadSheetUsingURIString(CSS_URI, win.windowUtils.AUTHOR_SHEET);
    win.windowUtils.loadSheetUsingURIString(CHROME_CSS_URI, win.windowUtils.AUTHOR_SHEET);
    try {
      win.windowUtils.loadSheetUsingURIString(AGENT_CSS_URI, win.windowUtils.AGENT_SHEET);
    } catch (e) {
      log("agent sheet", e);
    }
    if (hasIE6Icons()) {
      win.windowUtils.loadSheetUsingURIString(IE6_CSS_URI, win.windowUtils.AUTHOR_SHEET);
    }
    win.document.documentElement?.setAttribute("fe6-scheme", effectiveScheme(win));
  } catch (e) {
    console.error("[Fox Explorer 6] stylesheet failed", e);
  }
}

/* ------------------------------------------------------------------ about:preferences */
function injectPreferences(win) {
  const doc = win.document;
  const build = () => {
    if (doc.getElementById("fe6-prefs")) return;
    const anchor = doc.getElementById("startupGroup") || doc.getElementById("webAppearanceGroup") ||
                   doc.querySelector('groupbox[data-category="paneGeneral"]');
    if (!anchor) return;
    const h = doc.createElementNS("http://www.w3.org/1999/xhtml", "h2");
    h.textContent = "Fox Explorer 6";
    const desc = doc.createXULElement("description");
    desc.className = "description-deemphasized";
    desc.textContent = "Classic look settings. Dark mode flips the Windows 98 colours; websites follow it too unless you pick something else under Website appearance.";
    const mkRadio = (v, l) => { const r = doc.createXULElement("radio"); r.setAttribute("value", v); r.setAttribute("label", l); return r; };
    const rg = doc.createXULElement("radiogroup");
    rg.id = "fe6-scheme-radios";
    rg.append(mkRadio("light", "Light (classic Windows 98)"), mkRadio("dark", "Dark (colours flipped)"), mkRadio("system", "Use system setting"));
    rg.value = getPref(PREF.scheme, "light");
    rg.addEventListener("command", () => setScheme(rg.value));
    const cb = (label, pref, def) => {
      const c = doc.createXULElement("checkbox");
      c.setAttribute("label", label);
      c.checked = getPref(pref, def);
      c.addEventListener("command", () => Services.prefs.setBoolPref(pref, c.checked));
      return c;
    };
    const box = doc.createXULElement("groupbox");
    box.id = "fe6-prefs";
    box.setAttribute("data-category", "paneGeneral");
    box.append(h, desc, rg,
      cb("Show the Windows 98 title bar (turn off to use your desktop's own)", PREF.caption, true),
      cb("Show the status bar", PREF.statusbar, true),
      cb("Show the History menu", PREF.historyMenu, false));
    anchor.before(box);
    const sync = () => { box.hidden = !/^#?(general)?$/.test(win.location.hash || ""); };
    win.addEventListener("hashchange", sync);
    sync();
  };
  if (doc.readyState === "complete") build();
  else win.addEventListener("load", () => win.setTimeout(build, 0), { once: true });
}

/* Win98 scroll bars everywhere (web pages, sidebars, dialogs): one global agent sheet,
   which Firefox also hands to content processes. */
function registerGlobalSheets() {
  try {
    const sss = Cc["@mozilla.org/content/style-sheet-service;1"].getService(Ci.nsIStyleSheetService);
    const uri = name => Services.io.newURI("resource://fe6/" + name);
    const base = uri("fe6-scrollbars.css");
    if (!sss.sheetRegistered(base, sss.AGENT_SHEET)) sss.loadAndRegisterSheet(base, sss.AGENT_SHEET);
    // colours follow Fox Explorer's own setting (not Firefox's guess from the desktop)
    const scheme = getPref(PREF.scheme, "light");
    const want = scheme === "dark" ? "fe6-scrollbars-dark.css" : scheme === "system" ? "fe6-scrollbars-auto.css" : null;
    for (const name of ["fe6-scrollbars-dark.css", "fe6-scrollbars-auto.css"]) {
      const u = uri(name);
      const has = sss.sheetRegistered(u, sss.AGENT_SHEET);
      if (name === want && !has) sss.loadAndRegisterSheet(u, sss.AGENT_SHEET);
      if (name !== want && has) sss.unregisterSheet(u, sss.AGENT_SHEET);
    }
  } catch (e) {
    console.error("[Fox Explorer 6] scroll bar sheet failed", e);
  }
}

/* ------------------------------------------------------------------ bootstrap */
let started = false;
/* Firefox's profile manager (File › Profiles, about:profilemanager) starts other profiles by
   running the firefox binary with just --profile. Fox Explorer itself runs as
   `firefox -app browser/foxexplorer6.ini`, which is what gives it its own profile group,
   window class and remoting name; without -app the new window can't find its profile and
   the profile pages come up blank. Add our launch arguments to every such relaunch. */
function patchProfileLaunching() {
  try {
    const ini = Services.dirsvc.get("GreD", Ci.nsIFile);
    ini.append("browser");
    ini.append("foxexplorer6.ini");
    if (!ini.exists()) return;
    const appData = Services.dirsvc.get("UAppData", Ci.nsIFile).path;
    if (!/foxexplorer6\/?$/.test(appData)) return;   // this process wasn't started via -app
    let mod = null;
    for (const url of ["resource:///modules/profiles/SelectableProfileService.sys.mjs",
                       "moz-src:///browser/components/profiles/SelectableProfileService.sys.mjs"]) {
      try {
        mod = ChromeUtils.importESModule(url);
        break;
      } catch (e) {}
    }
    const sps = mod?.SelectableProfileService;
    if (!sps || sps.fe6Patched) return;
    const ours = ["-app", ini.path, "--name", "foxexplorer6", "--class", "foxexplorer6"];
    const withOurs = args => [...ours, ...args.filter((a, i, all) => !(a === "-app" || all[i - 1] === "-app"))];
    if (typeof sps.execProcess == "function") {
      // Firefox 140+: every relaunch goes through execProcess(args)
      const exec = sps.execProcess.bind(sps);
      sps.execProcess = args => exec(withOurs(args));
    } else if (typeof sps.getExecutableProcess == "function") {
      // older: launchInstance() runs getExecutableProcess().runw(false, args, n)
      const getProc = sps.getExecutableProcess.bind(sps);
      sps.getExecutableProcess = () => {
        const proc = getProc();
        return {
          runw: (blocking, args) => { const a = withOurs(args); proc.runw(blocking, a, a.length); },
          run: (blocking, args) => { const a = withOurs(args); proc.run(blocking, a, a.length); },
          get pid() { return proc.pid; },
        };
      };
    } else {
      return;
    }
    sps.fe6Patched = true;
    log("profile launches will use", ours.join(" "));
    patchProfilePages(sps);
  } catch (e) {
    log("profile launching", e);
  }
}

/* about:editprofile and about:deleteprofile assume the profile group database is already
   open. about:profilemanager opens it (maybeSetupDataStore), but the edit/delete pages
   don't, so reaching them first (e.g. from File › Profiles) left them blank with
   "currentProfile is null". Open it on their behalf before their first request. */
function patchProfilePages(sps) {
  try {
    const mod = ChromeUtils.importESModule("resource:///actors/ProfilesParent.sys.mjs");
    const proto = mod?.ProfilesParent?.prototype;
    if (!proto || proto.fe6Patched || typeof proto.receiveMessage != "function") return;
    const receive = proto.receiveMessage;
    proto.receiveMessage = async function (message) {
      if (!sps.currentProfile && typeof sps.maybeSetupDataStore == "function") {
        try {
          await sps.maybeSetupDataStore();
        } catch (e) {
          console.error("[Fox Explorer 6] couldn't open the profile group", e);
        }
      }
      return receive.call(this, message);
    };
    proto.fe6Patched = true;
  } catch (e) {
    log("profile pages", e);
  }
}

export const FoxExplorer6 = {
  init() {
    if (started) return;
    started = true;
    applyGlobalScheme();
    registerGlobalSheets();

    Services.obs.addObserver(subject => {
      const doc = subject;
      const win = doc?.defaultView;
      if (!win) return;
      const href = doc.documentURI || "";
      if (href.startsWith("chrome://browser/content/browser.xhtml")) {
        injectSheet(win);
      } else if (CHROME_DOC_PREFIXES.some(p => href.startsWith(p))) {
        try {
          win.windowUtils.loadSheetUsingURIString(CHROME_CSS_URI, win.windowUtils.AUTHOR_SHEET);
          win.windowUtils.loadSheetUsingURIString(AGENT_CSS_URI, win.windowUtils.AGENT_SHEET);
        } catch (e) {
          log("chrome doc sheet", href, e);
        }
      } else if (href.startsWith("about:preferences") || href.startsWith("about:settings")) {
        win.addEventListener("DOMContentLoaded", () => injectPreferences(win), { once: true });
      }
    }, "document-element-inserted");

    Services.obs.addObserver(win => {
      // each step on its own, so a change in one Firefox version can't take out the rest
      for (const [name, step] of [["commands", () => installCommands(win)], ["profiles", patchProfileLaunching], ["widgets", createWidgets], ["layout", applyDefaultLayout], ["window", () => initWindow(win)]]) {
        try {
          step();
        } catch (e) {
          console.error(`[Fox Explorer 6] ${name} step failed`, e);
        }
      }
    }, "browser-delayed-startup-finished");

    const syncTitlebarPref = () => {
      // our caption needs Firefox to draw the title bar; turning it off gives it back to the desktop
      Services.prefs.setIntPref("browser.tabs.inTitlebar", getPref(PREF.caption, true) ? 1 : 0);
    };
    if (Services.prefs.prefHasUserValue(PREF.caption)) syncTitlebarPref();

    const prefObserver = {
      observe(subject, topic, data) {
        if (data === PREF.scheme) {
          applyGlobalScheme();
          registerGlobalSheets();
        }
        if (data === PREF.caption) syncTitlebarPref();
        for (const w of Services.wm.getEnumerator("navigator:browser")) syncWindowAttrs(w);
      },
    };
    Services.prefs.addObserver("foxexplorer.", prefObserver);
    Services.obs.addObserver(() => refreshEngines(), "browser-search-engine-modified");
  },
};
