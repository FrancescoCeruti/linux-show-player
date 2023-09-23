import os
from pathlib import Path
from threading import Thread

import humanize
from PyQt5.QtCore import QT_TRANSLATE_NOOP, Qt
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QSpinBox,
    QHBoxLayout,
    QMessageBox,
)

from lisp import DEFAULT_CACHE_DIR
from lisp.core.plugin import Plugin
from lisp.core.signal import Signal, Connection
from lisp.plugins import get_plugin
from lisp.ui.settings.app_configuration import AppConfigurationDialog
from lisp.ui.settings.pages import SettingsPage
from lisp.ui.ui_utils import translate


class CacheManager(Plugin):
    Name = "CacheManager"
    Authors = ("Francesco Ceruti",)
    Description = "Utility to manage application cache"

    def __init__(self, app):
        super().__init__(app)
        # Register GStreamer settings widgets
        AppConfigurationDialog.registerSettingsPage(
            "plugins.cache_manager", CacheManagerSettings, CacheManager.Config
        )

        self.threshold_warning = Signal()
        self.threshold_warning.connect(
            self._show_threshold_warning, Connection.QtQueued
        )
        Thread(target=self._check_cache_size).start()

    def _check_cache_size(self):
        threshold = self.Config.get("sizeWarningThreshold", 0) * 1_000_000
        if threshold > 0:
            cache_size = self.cache_size()
            if cache_size > threshold:
                self.threshold_warning.emit(threshold, cache_size)

    def _show_threshold_warning(self, threshold, _):
        QMessageBox.warning(
            self.app.window,
            translate(
                "CacheManager",
                "Cache size",
            ),
            translate(
                "CacheManager",
                "The cache has exceeded {}. Consider clean it.\n"
                "You can do it in the application settings.",
            ).format(humanize.naturalsize(threshold)),
        )

    def cache_root(self):
        cache_dir = self.app.conf.get("cache.position", "")
        if not cache_dir:
            cache_dir = DEFAULT_CACHE_DIR

        return Path(cache_dir)

    def cache_size(self):
        """This could take some time if we have a lot of files."""
        return sum(
            entry.stat().st_size
            for entry in self.cache_root().glob("**/*")
            if entry.is_file() and not entry.is_symlink()
        )

    def purge(self):
        cache_dir = self.cache_root()
        if not cache_dir.exists():
            return

        for entry in cache_dir.iterdir():
            if not entry.is_symlink():
                if entry.is_dir():
                    self._remove_dir_content(entry)
                elif entry.is_file():
                    os.remove(entry)

    def _remove_dir_content(self, path: Path):
        for entry in path.iterdir():
            if entry.is_file() and not entry.is_symlink():
                os.remove(entry)


class CacheManagerSettings(SettingsPage):
    Name = QT_TRANSLATE_NOOP("SettingsPageName", "Cache Manager")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setLayout(QVBoxLayout())
        self.layout().setAlignment(Qt.AlignTop)

        self.warningGroup = QGroupBox(self)
        self.warningGroup.setLayout(QHBoxLayout())
        self.layout().addWidget(self.warningGroup)

        self.warningThresholdLabel = QLabel(self.warningGroup)
        self.warningGroup.layout().addWidget(self.warningThresholdLabel)

        self.warningThresholdSpin = QSpinBox(self.warningGroup)
        self.warningThresholdSpin.setRange(0, 10000)
        self.warningGroup.layout().addWidget(self.warningThresholdSpin)

        self.warningGroup.layout().setStretch(0, 3)
        self.warningGroup.layout().setStretch(1, 1)

        self.cleanGroup = QGroupBox(self)
        self.cleanGroup.setLayout(QVBoxLayout())
        self.layout().addWidget(self.cleanGroup)

        self.currentSizeLabel = QLabel(self.cleanGroup)
        self.currentSizeLabel.setAlignment(Qt.AlignCenter)
        self.cleanGroup.layout().addWidget(self.currentSizeLabel)

        self.cleanButton = QPushButton(self)
        self.cleanButton.clicked.connect(self.cleanCache)
        self.cleanGroup.layout().addWidget(self.cleanButton)

        self.retranslateUi()

        self.cacheManager = get_plugin("CacheManager")
        self.updateCacheSize()

    def retranslateUi(self):
        self.warningGroup.setTitle(
            translate("CacheManager", "Cache size warning")
        )
        self.warningThresholdLabel.setText(
            translate("CacheManager", "Warning threshold in MB (0 = disabled)")
        )

        self.cleanGroup.setTitle(translate("CacheManager", "Cache cleanup"))
        self.cleanButton.setText(
            translate("CacheManager", "Delete the cache content")
        )

    def loadSettings(self, settings):
        self.warningThresholdSpin.setValue(settings.get("sizeWarningThreshold"))

    def getSettings(self):
        return {"sizeWarningThreshold": self.warningThresholdSpin.value()}

    def updateCacheSize(self):
        self.currentSizeLabel.setText(
            humanize.naturalsize(self.cacheManager.cache_size())
        )

    def cleanCache(self):
        self.cacheManager.purge()
        self.updateCacheSize()
