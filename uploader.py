#!/usr/bin/python
# -*- coding: utf-8 -*-
import pycurl
import json
import StringIO
import sys
from gi.repository import Gtk, Gdk, Notify
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

class ImgurUploader:
	def __init__(self, args):
		
		allowedTypes = ("jpeg", "jpg", "gif", "png", "apng", "tiff", "bmp", "pdf", "xcf")
		images = []
		urls = []

		#Temporarily holds notifications before showing them
		self.notifications = []
		
		Notify.init("upload-to-imgur")
		
		#Parse command line parameters
		if len(args) == 1:
			#No paths supplied
			return
		else:
			for file in args:
				if file == args[0] or file == "":
					continue

				#Check that the file type is allowed
				type = imghdr.what(file)
				if not type:
					self.notifications.append(file+" "+notimg)
				else:
					if type not in allowedTypes:
						self.notifications.append(type+" "+notallowed+file)
					else:
						images.append(file)

		for file in images:
			urls.append(self.upload(file))
			
		self.setClipBoard(urls)
		
		self.notify(self.notifications)
		
	def notify(self, messages):
		'''Creates a notification. Strings can be either a string or a list of strings.'''
		if isinstance(messages, list):
			message = '\n'.join(messages)
		elif isinstance(messages, str):
			message = messages

		notification = Notify.Notification.new(APP, message, None)
		notification.show()
		
		
	def upload(self, file):
		'''Uploads an image to imgur. Returns a URL.'''
		c = pycurl.Curl()
		
		values = [
				("key", "e85c0044b9222bc9a2813679a452f54f"),
				("image", (c.FORM_FILE, file))]
				
		buf = StringIO.StringIO()
		
		c.setopt(c.URL, "http://imgur.com/api/upload.json")
		c.setopt(c.HTTPPOST, values)
		c.setopt(c.WRITEFUNCTION, buf.write)
		
		if c.perform():
			self.notifications.append(uploadfailed+" "+file+".")
			c.close()
			return

		result = buf.getvalue()
		c.close()

		data = json.loads(result)

		return data['rsp']['image']['original_image']
		
	def setClipBoard(self, urls):
		'''Adds a string to the clipboard. urls should be a list of strings.'''
		display = Gdk.Display.get_default()
		selection = Gdk.Atom.intern("CLIPBOARD", False)
		clipboard = Gtk.Clipboard.get_for_display(display, selection)
		clipboard.set_text('\n'.join(urls), -1)

		#Store the text, so that it is available even if this application has been closed.
		clipboard.store()

		#Add a notification upon completing.
		if len(urls) == 1:
			self.notifications.append(oneimage)
		elif len(urls) != 0:
			self.notifications.append(str(len(urls))+" "+multimages)

if __name__ == '__main__':
	uploader = ImgurUploader(sys.argv)
