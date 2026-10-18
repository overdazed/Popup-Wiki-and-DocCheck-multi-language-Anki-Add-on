from aqt import mw
from aqt.qt import QAction, QDockWidget, QVBoxLayout, QUrl, Qt, QInputDialog, QLineEdit
from PyQt6.QtWebEngineWidgets import QWebEngineView
from anki.hooks import addHook
import re
from aqt.utils import showInfo
from aqt.addons import AddonManager

class DocCheckPanel(QDockWidget):
    def __init__(self):
        QDockWidget.__init__(self, mw)
        self.setWindowTitle("DocCheck Panel")
        self.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)

        self.doccheck_webview = QWebEngineView()
        self.setWidget(self.doccheck_webview)

        mw.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self)
        self.hide()

doccheck_panel = DocCheckPanel()

def toggle_panel():
    if doccheck_panel.isVisible():
        doccheck_panel.hide()
    else:
        doccheck_panel.show()

def open_doccheck_article():
    selected_text = mw.web.selectedText()
    if not selected_text:
        return

    words = re.findall(r'\w+', selected_text)
    if not words:
        return

    term = " ".join(words)
    doccheck_url = f"https://flexikon.doccheck.com/de/{term.replace(' ', '_')}"
    doccheck_panel.doccheck_webview.load(QUrl(doccheck_url))
    doccheck_panel.show()

def open_wikipedia_article():
    selected_text = mw.web.selectedText()
    if not selected_text:
        return

    words = re.findall(r'\w+', selected_text)
    if not words:
        return

    term = " ".join(words)
    language = get_wikipedia_language()
    wikipedia_url = f"https://{language}.wikipedia.org/wiki/{term.replace(' ', '_')}"
    doccheck_panel.doccheck_webview.load(QUrl(wikipedia_url))
    doccheck_panel.show()

def add_action_to_context_menu(webview, menu):
    doccheck_action = QAction("Open DocCheck article", menu)
    doccheck_action.triggered.connect(open_doccheck_article)
    menu.addAction(doccheck_action)

    wikipedia_action = QAction("Open Wikipedia article", menu)
    wikipedia_action.triggered.connect(open_wikipedia_article)
    menu.addAction(wikipedia_action)

addHook("AnkiWebView.contextMenuEvent", add_action_to_context_menu)

toggle_panel_action = QAction("DocCheck Panel", mw)
toggle_panel_action.triggered.connect(toggle_panel)
mw.form.menuTools.addAction(toggle_panel_action)

def get_wikipedia_language():
    config = mw.addonManager.getConfig(__name__)
    return config.get("wikipedia_language", "de")

default_config = {
    "wikipedia_language": "de"
}

if not mw.addonManager.getConfig(__name__):
    mw.addonManager.writeConfig(__name__, default_config)

def on_config_button_click():
    config = mw.addonManager.getConfig(__name__)
    language = config["wikipedia_language"]
    language, ok = QInputDialog.getText(mw, "Wikipedia Language", "Please enter the Wikipedia language code (e.g., 'en' for English):", QLineEdit.EchoMode.Normal, language)
    if ok and language:
        config["wikipedia_language"] = language
        mw.addonManager.writeConfig(__name__, config)
        showInfo(f"Wikipedia language changed to '{language}'.")

addonManager = AddonManager(mw)
addonManager.setConfigAction(__name__, on_config_button_click)
