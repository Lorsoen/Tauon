"""Tauon Music Box - Translation loader for extra modules"""

# Copyright © 2020, Taiko2k captain(dot)gxj(at)gmail.com

#     This file is part of Tauon Music Box.
#
#     Tauon Music Box is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     Tauon Music Box is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with Tauon Music Box.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import annotations

import io
import itertools
import json
import gettext
import logging
import threading
import time
import os
import platform
import sys
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING

from tauon.t_modules.t_config import Config
from tauon.t_modules import t_bootstrap
from tauon.t_modules import t_translations	# Loads translations. (requires os, platform and sys)

import requests

from tauon.t_modules.t_extra import Timer

if TYPE_CHECKING:
	from io import BytesIO

	from tauon.t_modules.t_extra import TauonPlaylist
	from tauon.t_modules.t_main import Tauon, TrackClass

class Translations:

	def loader(self) -> None:

		# Detect platform
		windows_native = False
		macos = False
		msys = False
		system = "Linux"
		arch = platform.machine()
		platform_release = platform.release()
		platform_system = platform.system()
		win_ver = 0
		if platform_system == "Windows":
			try:
				win_ver = int(platform_release)
			except Exception:
				logging.exception("Failed getting Windows version from platform.release()")

		if sys.platform == "win32":
			# system = 'Windows'
			# windows_native = False
			system = "Linux"
			msys = True
		else:
			system = "Linux"
			import fcntl

		if sys.platform == "darwin":
			macos = True

		if system == "Windows":
			import win32con
			import win32api
			import win32gui
			import win32ui
			import comtypes
			import atexit

		if system == "Linux":
			from tauon.t_modules import t_topchart

		if system == "Linux" and not macos and not msys:
			from tauon.t_modules.t_dbus import Gnome

		holder                 = t_bootstrap.holder
		install_directory      = str(holder.install_directory) # TODO(Martin): Convert to Path proper

		try:
			import pylast
			last_fm_enable = True
			if pyinstaller_mode:
				pylast.SSL_CONTEXT.load_verify_locations(os.path.join(install_directory, "certifi", "cacert.pem"))
		except Exception:
			logging.exception("PyLast module not found, last fm will be disabled.")
			last_fm_enable = False

		if not windows_native:
			import gi
			from gi.repository import GLib

			font_folder = os.path.join(install_directory, "fonts")
			if os.path.isdir(font_folder):
				import ctypes

				fc = ctypes.cdll.LoadLibrary("libfontconfig-1.dll")
				fc.FcConfigReference.restype = ctypes.c_void_p
				fc.FcConfigReference.argtypes = (ctypes.c_void_p,)
				fc.FcConfigAppFontAddDir.argtypes = (ctypes.c_void_p, ctypes.c_char_p)
				config = ctypes.c_void_p()
				config.contents = fc.FcConfigGetCurrent()
				fc.FcConfigAppFontAddDir(config.value, font_folder.encode())


		# Detect if we are installed or running portable
		install_mode = False
		flatpak_mode = False
		snap_mode = False
		if install_directory.startswith(("/opt/", "/usr/", "/app/", "/snap/")):
			install_mode = True
			if install_directory[:6] == "/snap/":
				snap_mode = True
			if install_directory[:5] == "/app/":
				# Flatpak mode
				logging.info("Detected running as Flatpak")

				# [old / no longer used] Symlink fontconfig from host system as workaround for poor font rendering
				if os.path.exists(os.path.join(home_directory, ".var/app/com.github.taiko2k.tauonmb/config")):

					host_fcfg = os.path.join(home_directory, ".config/fontconfig/")
					flatpak_fcfg = os.path.join(home_directory, ".var/app/com.github.taiko2k.tauonmb/config/fontconfig")

					if os.path.exists(host_fcfg):

						# if os.path.isdir(flatpak_fcfg) and not os.path.islink(flatpak_fcfg):
						#	 shutil.rmtree(flatpak_fcfg)
						if os.path.islink(flatpak_fcfg):
							logging.info("-- Symlink to fonconfig exists, removing")
							os.unlink(flatpak_fcfg)
						# else:
						#	 logging.info("-- Symlinking user fonconfig")
						#	 #os.symlink(host_fcfg, flatpak_fcfg)

				flatpak_mode = True

		# If we're installed, use home data locations
		if (install_mode and system == "Linux") or macos or msys:

			cache_directory  = Path(GLib.get_user_cache_dir()) / "TauonMusicBox"
			user_directory   = str(Path(GLib.get_user_data_dir()) / "TauonMusicBox")
			config_directory = Path(GLib.get_user_data_dir()) / "TauonMusicBox"

			if not Path(user_directory).is_dir():
				os.makedirs(user_directory)

			if not config_directory.is_dir():
				os.makedirs(config_directory)

			if snap_mode:
				logging.info("Installed as Snap")
			elif flatpak_mode:
				logging.info("Installed as Flatpak")
			else:
				logging.info("Running from installed location")

			logging.info("User files location: " + user_directory)

			if not Path(Path(user_directory) / "encoder").is_dir():
				os.makedirs(Path(user_directory) / "encoder")


		# elif (system == 'Windows' or msys) and (
		# 	'Program Files' in install_directory or
		# 	os.path.isfile(install_directory + '\\unins000.exe')):
		#
		#	 user_directory = os.path.expanduser('~').replace("\\", '/') + "/Music/TauonMusicBox"
		#	 config_directory = user_directory
		#	 cache_directory = user_directory / "cache"
		#	 logging.info(f"User Directory: {user_directory}")
		#	 install_mode = True
		#	 if not os.path.isdir(user_directory):
		#		 os.makedirs(user_directory)


		else:
			logging.info("Running in portable mode")

			user_directory = str(Path(install_directory) / "user-data")
			config_directory = Path(user_directory)

			if not Path(user_directory).is_dir():
				os.makedirs(user_directory)

		self.ui_lang = "auto"

		locale_dir = os.path.join(install_directory, "locale")
		prefs = Prefs()
		cf = Config()

		prefs.ui_lang = cf.sync_add(
				"string", "display-language", prefs.ui_lang, "Override display language to use if "
				"available. E.g. \"en\", \"ja\", \"zh_CH\". "
				"Default: \"auto\"")


		lang = ""

		locale_dir = os.path.join(install_directory, "locale")

		if flatpak_mode:
			locale_dir = "/app/share/locale"
		elif install_directory.startswith("/opt/") or install_directory.startswith("/usr/"):
			locale_dir = "/usr/share/locale"

		lang = []
		if prefs.ui_lang != "auto" or prefs.ui_lang == "":
			lang = [prefs.ui_lang]

		if lang:
			# Force set lang
			f = gettext.find("tauon", localedir=locale_dir, languages=lang)

			if f:
				translation = gettext.translation("tauon", localedir=locale_dir, languages=lang)
				translation.install()
				_ = translation.gettext

				logging.info("Translation file loaded for t_jellyfin")
			else:
				logging.info("No translation file available for t_jellyfin")

		else:
			# Auto detect lang
			f = gettext.find("tauon", localedir=locale_dir)

			if f:
				translation = gettext.translation("tauon", localedir=locale_dir)
				translation.install()
				_ = translation.gettext

				logging.info("Translation file loaded")
			# else:
			#	 logging.info("No translation file available")

		#----