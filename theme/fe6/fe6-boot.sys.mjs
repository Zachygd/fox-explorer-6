/* Fox Explorer 6 — chrome customisation layer.
 * Loaded once per process by foxexplorer.cfg (Firefox autoconfig). Everything here uses
 * public Firefox chrome APIs (CustomizableUI, gBrowser, StatusPanel, prefs), so extensions,
 * tabs, customise mode and about:preferences keep working. */

const CSS_URI = "resource://fe6/fe6.css";
const AGENT_CSS_URI = "resource://fe6/fe6-agent.css";
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
const LAYOUT_VERSION = 1;
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
};

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
let widgetsCreated = false;
function createWidgets() {
  if (widgetsCreated) return;
  widgetsCreated = true;
  const CUI = lazy.CustomizableUI;
  const button = (id, label, tooltip, onCommand, extra = {}) => {
    try {
      CUI.createWidget({
        id, label, tooltiptext: tooltip, type: "button",
        defaultArea: null, removable: true,
        onCommand(event) { onCommand(event.target.ownerGlobal, event); },
        ...extra,
      });
    } catch (e) { log("createWidget failed", id, e); }
  };

  button("fe6-stop-button", "Stop", "Stop", win => win.BrowserCommands ? win.BrowserCommands.stop() : win.BrowserStop(), {
    onCreated(node) { node.setAttribute("disabled", "true"); },
  });
  button("fe6-refresh-button", "Refresh", "Refresh", (win, ev) => {
    const bypass = ev.shiftKey || ev.ctrlKey;
    if (win.BrowserCommands) {
      bypass ? win.BrowserCommands.reloadSkipCache() : win.BrowserCommands.reload();
    } else {
      bypass ? win.BrowserReloadSkipCache() : win.BrowserReload();
    }
  });
  button("fe6-search-button", "Search", "Search the Web", win => {
    win.gURLBar.focus();
    try {
      win.gURLBar.searchMode = { engineName: Services.search.defaultEngine?.name, entry: "other" };
    } catch (e) {}
    win.gURLBar.select();
  });
  const sidebar = (win, id) => {
    if (win.SidebarController) win.SidebarController.toggle(id);
    else if (win.SidebarUI) win.SidebarUI.toggle(id);
  };
  button("fe6-favorites-button", "Favorites", "Favorites", win => sidebar(win, "viewBookmarksSidebar"));
  button("fe6-history-button", "History", "History", win => sidebar(win, "viewHistorySidebar"));
  button("fe6-mail-button", "Mail", "Mail", win => {
    const uri = win.gBrowser.currentURI?.spec || "";
    const title = win.gBrowser.contentTitle || "";
    win.openTrustedLinkIn(`mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent(uri)}`, "current");
  });
  button("fe6-print-button", "Print", "Print", win => {
    if (win.PrintUtils?.startPrintWindow) {
      win.PrintUtils.startPrintWindow(win.gBrowser.selectedBrowser.browsingContext);
    } else {
      win.goDoCommand("cmd_print");
    }
  });
  button("fe6-go-button", "Go", "Go to the address in the Address bar", (win, ev) => {
    if (win.gURLBar.value) win.gURLBar.handleCommand(ev);
    else win.gURLBar.focus();
  });

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

/* One-time default layout (IE6 Standard Buttons). Re-run by setting foxexplorer.layoutVersion to 0. */
function applyDefaultLayout() {
  if (getPref(PREF.layout, 0) >= LAYOUT_VERSION) return;
  const CUI = lazy.CustomizableUI;
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
  const stopBtn = () => doc.getElementById("fe6-stop-button");

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
    const s = stopBtn();
    if (s) busy ? s.removeAttribute("disabled") : s.setAttribute("disabled", "true");
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
      for (const mi of popup.children) mi.setAttribute("checked", mi.getAttribute("value") === cur);
    });
    viewPopup.addEventListener("popupshowing", () => sb.setAttribute("checked", getPref(PREF.statusbar, true)));
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
  for (const [name, fn] of [["attrs", syncWindowAttrs], ["caption", buildCaption], ["statusbar", buildStatusBar], ["menus", buildMenus]]) {
    try {
      fn(win);
    } catch (e) {
      console.error(`[Fox Explorer 6] ${name} failed`, e);
    }
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

/* ------------------------------------------------------------------ bootstrap */
let started = false;
export const FoxExplorer6 = {
  init() {
    if (started) return;
    started = true;
    applyGlobalScheme();

    Services.obs.addObserver(subject => {
      const doc = subject;
      const win = doc?.defaultView;
      if (!win) return;
      const href = doc.documentURI || "";
      if (href.startsWith("chrome://browser/content/browser.xhtml")) {
        injectSheet(win);
      } else if (href.startsWith("about:preferences") || href.startsWith("about:settings")) {
        win.addEventListener("DOMContentLoaded", () => injectPreferences(win), { once: true });
      }
    }, "document-element-inserted");

    Services.obs.addObserver(win => {
      // each step on its own, so a change in one Firefox version can't take out the rest
      for (const [name, step] of [["widgets", createWidgets], ["layout", applyDefaultLayout], ["window", () => initWindow(win)]]) {
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
        if (data === PREF.scheme) applyGlobalScheme();
        if (data === PREF.caption) syncTitlebarPref();
        for (const w of Services.wm.getEnumerator("navigator:browser")) syncWindowAttrs(w);
      },
    };
    Services.prefs.addObserver("foxexplorer.", prefObserver);
  },
};
