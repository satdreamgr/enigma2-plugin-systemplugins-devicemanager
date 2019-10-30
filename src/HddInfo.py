# for localized messages
from . import _
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config
from Components.Sources.StaticText import StaticText
import os
import re

class HddInfo(ConfigListScreen, Screen):

	skin = """
		<screen name="HddInfo" position="center,center" size="560,430" title="Hard Drive Info">
			<ePixmap pixmap="buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget font="Regular;18" halign="left" name="model" position="20,45" size="540,25" valign="center" />
			<widget font="Regular;18" halign="left" name="serial" position="20,75" size="540,25" valign="center" />
			<widget font="Regular;18" halign="left" name="firmware" position="20,105" size="540,25" valign="center" />
			<widget font="Regular;18" halign="left" name="cylinders" position="20,135" size="540,25" valign="center" />
			<widget font="Regular;18" halign="left" name="heads" position="20,165" size="540,25" valign="center" />
			<widget font="Regular;18" halign="left" name="sectors" position="20,195" size="540,25" valign="center" />
			<widget font="Regular;18" halign="left" name="readDisk" position="20,225" size="540,25" valign="center" />
			<widget font="Regular;18" halign="left" name="readCache" position="20,255" size="540,25" valign="center" />
			<widget font="Regular;18" halign="left" name="temp" position="20,285" size="540,25" valign="center" />
			<widget name="config" position="20,325" scrollbarMode="showOnDemand" size="540,30" />
		</screen>"""

	def __init__(self, session, device, deviceinfo):
		Screen.__init__(self, session)
		self.setTitle(_("Device details"))
		self.device = device
		self.deviceinfo = deviceinfo
		self.list = []

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText("")

		if self.deviceinfo[2] and not self.deviceinfo[6]:
			self.list.append(getConfigListEntry(_("Hard disk standby after"), config.usage.hdd_standby))
			self["key_green"].setText(_("Save"))

		ConfigListScreen.__init__(self, self.list)

		self["model"] = Label(_("Model: unknown"))
		self["serial"] = Label(_("Serial: unknown"))
		self["firmware"] = Label(_("Firmware: unknown"))
		self["cylinders"] = Label(_("Cylinders: unknown"))
		self["heads"] = Label(_("Heads: unknown"))
		self["sectors"] = Label(_("Sectors: unknown"))
		self["readDisk"] = Label(_("Read disk speed: unknown"))
		self["readCache"] = Label(_("Read disk cache speed: unknown"))
		self["temp"] = Label(_("Disk temperature: unknown"))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"red": self.keyCancel,
			"green": self.keySave,
			"cancel": self.keyCancel,
		}, -2)

		self.onLayoutFinish.append(self.drawInfo)

	def drawInfo(self):
		device = "/dev/%s" % self.device
		#regexps
		modelRe = re.compile(r"Model Number:\s*([\w\-]+)")
		serialRe = re.compile(r"Serial Number:\s*([\w\-]+)")
		firmwareRe = re.compile(r"Firmware Revision:\s*([\w\-]+)")
		cylindersRe = re.compile(r"cylinders\s*(\d+)\s*(\d+)")
		headsRe = re.compile(r"heads\s*(\d+)\s*(\d+)")
		sectorsRe = re.compile(r"sectors/track\s*(\d+)\s*(\d+)")
		readDiskRe = re.compile(r"Timing buffered disk reads:\s*(.*)")
		readCacheRe = re.compile(r"Timing buffer-cache reads:\s*(.*)")
		tempRe = re.compile(r"%s:.*:(.*)" % device)

		# wake up disk... disk in standby may cause not correct value
		os.system("/sbin/hdparm -S 0 %s" % device)

		hdparm = os.popen("/sbin/hdparm -I %s" % device)
		for line in hdparm:
			model = re.findall(modelRe, line)
			if model:
				self["model"].setText(_("Model: %s") % model[0].lstrip())
			serial = re.findall(serialRe, line)
			if serial:
				self["serial"].setText(_("Serial: %s") % serial[0].lstrip())
			firmware = re.findall(firmwareRe, line)
			if firmware:
				self["firmware"].setText(_("Firmware: %s") % firmware[0].lstrip())
			cylinders = re.findall(cylindersRe, line)
			if cylinders:
				self["cylinders"].setText(_("Cylinders: %s (max) %s (current)") % (cylinders[0][0].lstrip(), cylinders[0][1].lstrip()))
			heads = re.findall(headsRe, line)
			if heads:
				self["heads"].setText(_("Heads: %s (max) %s (current)") % (heads[0][0].lstrip(), heads[0][1].lstrip()))
			sectors = re.findall(sectorsRe, line)
			if sectors:
				self["sectors"].setText(_("Sectors: %s (max) %s (current)") % (sectors[0][0].lstrip(), sectors[0][1].lstrip()))
		hdparm.close()
		hdparm = os.popen("/sbin/hdparm -t %s" % device)
		for line in hdparm:
			readDisk = re.findall(readDiskRe, line)
			if readDisk:
				self["readDisk"].setText(_("Read speed: %s") % readDisk[0].lstrip())
		hdparm.close()
		hdparm = os.popen("/sbin/hdparm -T %s" % device)
		for line in hdparm:
			readCache = re.findall(readCacheRe, line)
			if readCache:
				self["readCache"].setText(_("Read cache speed: %s") % readCache[0].lstrip())
		hdparm.close()
		hddtemp = os.popen("/usr/sbin/hddtemp -q %s" % device)
		for line in hddtemp:
			temp = re.findall(tempRe, line)
			if temp:
				self["temp"].setText(_("Disk temperature: %s") % temp[0].lstrip())
		hddtemp.close()
