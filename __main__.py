#!/usr/bin/python

# This file is part of mc2TeX, the mathcad to TeX converter.
#
# Copyright (c) 2016 Turysaz [turysaz@posteo.org]
#
# This program is free software. You can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License version 2 for more details.
#
# You should have received a copy of the GNU General Public
# version 2 along with this program. If not, visit 
# https://www.gnu.org/licenses/ or write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

import mc2tex
import easygui

program_version = "0.3, July 2016"

splash_msg = ("This is Turysaz' mc2TeX, the glorious Mathcad-To-TeX converter.\n" +
		"version " + program_version + "\n" +
		"\n" +
		"Copyright (c) 2016 by Turysaz" +
		"\n"+
		"mc2TeX is free software and it is published under the GNU General Public License version 2. "+
		"You are welcome to redistribute it under certain conditions. " +
		"For details visit https://www.gnu.org/licenses/\n" +
		"mc2TeX comes with ABSOLUTELY NO WARRANTY.\n" +
		"\nPlease report bugs to turysaz@posteo.org" 
		)

window_title = "mc2TeX - " + program_version


def main():
	easygui.msgbox(msg=splash_msg,
		title=window_title,
		ok_button="Yeah, whatever. Just do what you're made for!")
	
	inpath = easygui.fileopenbox(msg="choose input file (.xmcd)",
		title=window_title,
		filetypes="*.xmcd",
		)
	outpath = easygui.filesavebox(msg="choose output file (.tex)",
		title=window_title,
		default="out.tex",
		filetypes="*.xmcd"
		)
	if inpath == None or outpath == None:
		print("no file chosen, abort!")
		easygui.msgbox(msg="No file chosen. Abort.",
			title=window_title,
			ok_button="Exit")
	else:
		mc2tex.convert(inpath, outpath)
		easygui.msgbox(msg="Everything done as you wished " +
			"(well, hopefully. Better have a look at the results...)\n"+
			"Have a nice day!",
			title=window_title,
			ok_button="Exit")
	exit()
	
main()

