#!/usr/bin/python
# -*- coding: utf-8 -*-
import pycurl
import xml.dom.minidom
import StringIO
import sys
from gi.repository import Gtk, Gdk, Notify
import os
import imghdr
import locale
import gettext
	
APP="Imgur Uploader"
DIR="locale"

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR)
gettext.textdomain(APP)
_ = gettext.gettext

##STRINGS
notimg = _("is not an image.")
notallowed = _("is not an allowed file type. Skipping.")
uploading = _("Uploading")
oneimage = _("1 image has been uploaded.")
multimages = _("images have been uploaded.")
uploadfailed = _("Unable to upload")

class Uploadr:
	def __init__(self, args):
		
		self.allowedTypes = ("jpeg", "jpg", "gif", "png", "apng", "tiff", "bmp", "pdf", "xcf")
		self.images = []
		self.urls = []
		self.broadcasts = []
		Notify.init("upload-to-imgur")
		if len(args) == 1:
			return
		else:
			for file in args:
				if file == args[0] or file == "":
					continue
				self.type = imghdr.what(file)
				if not self.type:
					self.broadcasts.append(file+" "+notimg)
				else:
					if self.type not in self.allowedTypes:
						self.broadcasts.append(self.type+" "+notallowed+file)
					else:
						self.images.append(file)
		for file in self.images:
			self.upload(file)
			
		self.setClipBoard()
		
		self.broadcast(self.broadcasts)
		
	def broadcast(self, l):
		message = '\n'.join(l)
		notification = Notify.Notification.new(_("Imgur Uploader"), message, None)
		notification.show()
		
		
	def upload(self, file):
		c = pycurl.Curl()
		
		values = [
				("key", "e85c0044b9222bc9a2813679a452f54f"),
				("image", (c.FORM_FILE, file))]
				
		buf = StringIO.StringIO()
		
		c.setopt(c.URL, "http://imgur.com/api/upload.xml")
		c.setopt(c.HTTPPOST, values)
		c.setopt(c.WRITEFUNCTION, buf.write)
		
		if c.perform():
			self.broadcasts.append(uploadfailed+" "+file+".")
			c.close()
			return

		self.result = buf.getvalue()
		c.close()

		doc = xml.dom.minidom.parseString(self.result)

		self.urls.append(doc.getElementsByTagName("original_image")[0].childNodes[0].nodeValue)
		
	def setClipBoard(self):
		display = Gdk.Display.get_default()
		selection = Gdk.Atom.intern("CLIPBOARD", False)
		clipboard = Gtk.Clipboard.get_for_display(display, selection)
		clipboard.set_text('\n'.join(self.urls), -1)
		clipboard.store()
		if len(self.urls) == 1:
			self.broadcasts.append(oneimage)
		elif len(self.urls) != 0:
			self.broadcasts.append(str(len(self.urls))+" "+multimages)

if __name__ == '__main__':
	uploadr = Uploadr(sys.argv)
