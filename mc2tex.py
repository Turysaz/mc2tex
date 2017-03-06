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

import xml.etree.ElementTree
import easygui
import re

# ========== GLOBAL CONSTANTS =====================
ns = {"def" : "http://schemas.mathsoft.com/worksheet30",
		"ml" : "http://schemas.mathsoft.com/math30"}

tex_intro = """\\documentclass[11pt]{scrartcl}
\\usepackage{amsmath}
\\begin{document}"""

tex_outro = """
\\end{document}
"""

author_note_output = """% This file was created by Turysaz' Mathcad-to-TeX-Converter "mc2TeX".
% Report bugs to turysaz@posteo.org!

"""
greek_alphabet = { 
	u"\u0391" : r"A",
	u"\u0392" : r"B",
	u"\u0393" : r"\Gamma",
	u"\u0394" : r"D",
	u"\u0395" : r"E",
	u"\u0396" : r"Z",
	u"\u0397" : r"H",
	u"\u0398" : r"\Theta",
	u"\u0399" : r"I",
	u"\u039a" : r"K",
	u"\u039b" : r"\Lambda",
	u"\u039c" : r"M",
	u"\u039d" : r"N",
	u"\u039e" : r"\Xi",
	u"\u039f" : r"O",
	u"\u03a0" : r"\Pi",
	u"\u03a1" : r"P",
	#u"\u03a2" : r"",
	u"\u03a3" : r"\Sigma",
	u"\u03a4" : r"T",
	u"\u03a5" : r"\Upsilon",
	u"\u03a6" : r"\Phi",
	u"\u03a7" : r"X",
	u"\u03a8" : r"\Psi",
	u"\u03a9" : r"\Omega",
	#u"\u03aa" : r"", # very special
	#u"\u03ab" : r"", # very special
	#u"\u03ac" : r"", # very special
	u"\u03ad" : r"",
	u"\u03ae" : r"",
	u"\u03af" : r"",
	u"\u03b0" : r"",
	u"\u03b1" : r"\alpha",
	u"\u03b2" : r"\beta",
	u"\u03b3" : r"\gamma",
	u"\u03b4" : r"\delta",
	u"\u03b5" : r"\varepsilon",
	u"\u03b6" : r"\zeta",
	u"\u03b7" : r"\eta",
	u"\u03b8" : r"\theta",
	u"\u03b9" : r"\iota",
	u"\u03ba" : r"\kappa",
	u"\u03bb" : r"\lambda",
	u"\u03bc" : r"\mu",
	u"\u03bd" : r"\nu",
	u"\u03be" : r"\xi",
	u"\u03bf" : r"o",
	u"\u03c0" : r"\pi",
	u"\u03c1" : r"\rho",
	u"\u03c2" : r"\sigma", # "final sigma"
	u"\u03c3" : r"\sigma",
	u"\u03c4" : r"\tau",
	u"\u03c5" : r"\upsilon",
	u"\u03c6" : r"\varphi",
	u"\u03c7" : r"\chi",
	u"\u03c8" : r"\psi",
	u"\u03c9" : r"\omega",
	# special variants
	u"\u03f5" : r"\epsilon",
	u"\u03d1" : r"\vartheta",
	u"\u03d6" : r"\varpi",
	u"\u03f1" : r"\varrho",
	u"\u03db" : r"\varsigma",
	u"\u03d5" : r"\phi",
	}

known_functions = {
	"sin" : "\\sin",
	"cos" : "\\cos",
	"tan" : "\\tan",
	"cot" : "\\cot"
	}

abbrev_units = {
	"millimeter" : "mm",
	"meter"	: "m",
	"seconds" : "s",
	"minutes" : "min",
	"hours" : "h",
	"kilogram" : "kg",
	"minutes" : "min",
	"newton" : "N"
	}

special_symbols_text = {
	r"%" : r"\%",
	#"\\ " : r"\backslash",
	r"_" : r"\_",
	r"$" : r"\$"
	}

special_symbols_math = {
	u"\u00b0" : "^{\circ}"
	}
	

# ========= INTERPRETER AND CO. ===================== 

# ---- TEXT INTERPRETER ----------------
# search recursively for text so <p>s and similar will be ignored
def deepsearch_text(region):
	deepresult = ""

	for node in region.iter():
		if node.tag[-1] == "p":
			for t in node.itertext():
				deepresult += t
	return deepresult

# end def deepsearch


# ---- MATH INTERPRETER -------------------
def interpr_math(region):
	
	res = ""
	for node in region:
		if not ns["ml"] in node.tag:
			continue
		res += interpr_math_rec(node)
	return res

# end def interpr_math


def interpr_math_rec(formular, toplevel=False):
	res = ""

	if not ns["ml"] in formular.tag:
		return res

	if formular.tag[-10:] == "provenance":
		for elem in formular:
			res += interpr_math_rec(elem, toplevel = True)
		return res

	if formular.tag[-6:] == "define":
		res += interpr_math_rec(formular[0], toplevel=True)
		res += " = "
		for elem in formular[1:]:
			res += interpr_math_rec(elem, toplevel=True)
		return res

	if formular.tag[-4:] == "eval":
		for elem in formular:
			res += interpr_math_rec(elem, toplevel=True)
		return res
	
	if formular.tag[-7:] == "symEval":
		for elem in formular:
			res += interpr_math_rec(elem,toplevel=True)
		return res
	
	if formular.tag[-6:] == "parens":
		for elem in formular:
			res += interpr_math_rec(elem)
		return res

	if formular.tag[-12:] == "unitOverride":
		#res += interpr_math_rec(formular[0])
		return res
	
	if formular.tag[-11:] == "unitedValue":
		for elem in formular:
			res += interpr_math_rec(elem)
		return res
	
	if formular.tag[-12:] == "unitMonomial":
		res += " \\cdot "
		count = len(formular) 
		unit_list = []
		numerator = []
		denominator = []
		
		# parse every single unit
		for elem in formular:
			unit_list += [interpr_math_rec(elem)]

		# sort numerator / denominator by sign of the power
		for elem in unit_list:
			if "^" in elem:
				if elem[elem.index("^")+2] == "-":
					elem = elem.replace("-", "")
					denominator += [elem]
				else:
					numerator += [elem]
			else:
				numerator += [elem]

		# render unit term
		if len(denominator) >0:
			res += "\\frac{"
			if len(numerator) == 0:
				res += "1}{"
			else:
				count = len(numerator) - 1
				for elem in numerator:
					res += elem
					count -= 1
					if count > 0:
						res += " \\cdot "
				res += "}{"

				count = len(denominator) - 1
				for elem in denominator:
					res += elem
					count -= 1
					if count > 0:
						res += " \\cdot "
				res += "}"
		else:
			for elem in numerator:
				res += elem
				res += " \\cdot "

		return res
	# end unit interpretation
	
	if formular.tag[-5:] == "apply":
		calcsign = " "
		leave_nodes_at_beginning = 1

		# check if it os add, sub, mul, div or pow
		if formular[0].tag[-4:] == "mult":
			calcsign = " \\cdot "
		elif formular[0].tag[-3:] == "div":
			if len(formular) > 3:
				calcsign = " / "
			else:
				res += r"\frac{"
				res += interpr_math_rec(formular[1])
				res += "}{"
				res += interpr_math_rec(formular[2])
				res += "}"
				return res
		elif formular[0].tag[-3:] == "pow":
			calcsign = "^"
		elif formular[0].tag[-4:] == "plus":
			calcsign = " + "
		elif formular[0].tag[-5:] == "minus":	
			calcsign = " - "

		elif formular[0].tag[-4:] == "sqrt":
			res += "\\sqrt{"
			res += interpr_math_rec(formular[1], toplevel=True)
			res += "}"
			return res

		elif formular[0].tag[-7:] == "nthRoot":
			res += "\\sqrt[" + interpr_math_rec(formular[1]) + "]{"
			res += interpr_math_rec(formular[2], toplevel=True)
			res += "}"
			return res

		elif formular[0].tag[-6:] == "absval":
			res += " | "
			res += interpr_math_rec(formular[1], toplevel=True)
			res += " | "
			return res

		elif formular[0].tag[-3:] == "neg":
			res += " - "
			toplevel = True

		elif formular[0].tag[-5:] == "equal":
			res += interpr_math_rec(formular[1])
			res += " = "
			res += interpr_math_rec(formular[2])
			return res

		elif formular[0].tag[-7:] == "indexer":
			res += interpr_math_rec(formular[1])
			res += "_{"
			res += interpr_math_rec(formular[2])
			res += "} "
			return res
	
		elif formular[0].tag[-9:] == "factorial":
			res += interpr_math_rec(formular[1]) + "!"
			return res

		elif formular[0].tag[-9:] == "transpose":
			res += interpr_math_rec(formular[1])
			res += "^T"
			return res
		
		elif formular[0].tag[-9:] == "summation":
			#inits
			specified_bounds = False
			summand = None
			variables = None

			#analysis
			for elem in formular[1:]:
				if elem.tag[-6:] == "bounds":
					specified_bounds = [
						interpr_math_rec(elem[0]),
						interpr_math_rec(elem[1])
						]
					continue
				elif elem.tag[-6:] == "lambda":
					variables = interpr_math_rec(elem[0])
					summand = interpr_math_rec(elem[1])
					continue
			#end analysis for loop

			#variables
			if specified_bounds != False:
				res += "\\sum_{" + variables + " = " + specified_bounds[0]
				res += "}^{" + specified_bounds[1] + "}"
			else:
				res += "\\sum_{" + variables + "}"

			#summand
			res += " " + summand

			return res

		elif formular[0].tag[-7:] == "product":
			#inits
			specified_bounds = False
			factor = None
			variables = None

			#analysis
			for elem in formular[1:]:
				if elem.tag[-6:] == "bounds":
					specified_bounds = [
						interpr_math_rec(elem[0]),
						interpr_math_rec(elem[1])
						]
					continue
				elif elem.tag[-6:] == "lambda":
					variables = interpr_math_rec(elem[0])
					factor = interpr_math_rec(elem[1])
					continue
			#end analysis for loop

			#variables
			if specified_bounds != False:
				res += "\\prod_{" + variables + " = " + specified_bounds[0]
				res += "}^{" + specified_bounds[1] + "}"
			else:
				res += "\\prod_{" + variables + "}"

			#factor
			res += " " + factor

			return res


		elif formular[0].tag[-8:] == "integral":
			#inits
			specified_bounds = False
			integrand = None
			variables = None

			#analysis
			for elem in formular[1:]:
				if elem.tag[-6:] == "bounds":
					specified_bounds = [
						interpr_math_rec(elem[0]),
						interpr_math_rec(elem[1])
						]
					continue
				elif elem.tag[-6:] == "lambda":
					variables = interpr_math_rec(elem[0])
					integrand = interpr_math_rec(elem[1])
					continue
			#end analysis for loop

			#variables
			if specified_bounds != False:
				res += "\\int\\limits_{" + specified_bounds[0]
				res += "}^{" + specified_bounds[1] + "}"
			else:
				res += "\\int"

			#summand
			res += " " + integrand
			res += "\\mathrm{d} " + variables #+ ")"

			return res

		else:
			#leave_nodes_at_beginning = 0
			res += interpr_math_rec(formular[0])
			res += "("
			res += interpr_math_rec(formular[1])
			res += ")"
			return res

		if not toplevel:
			res += " ( "

		count = len(formular) - leave_nodes_at_beginning

		for elem in formular[leave_nodes_at_beginning:]:
			res += interpr_math_rec(elem)
			count -= 1
			if count > 0:
				res += calcsign
			
		if not toplevel:
			res += " ) "

		return res
	# end "apply"
	
	if formular.tag[-6:] == "result":
		res += " = "
		res += interpr_math_rec(formular[0])
		return res

	if formular.tag[-9:] == "symResult":
		res += " = "
		res += interpr_math_rec(formular[0])
		return res
		
	if formular.tag[-4:] == "real":
		brackets = False
		if formular.text[0] == "-":
			brackets = True
			res += "{"
		raw_num = formular.text
		if "." in raw_num:
			res += str(float(formular.text))
		else:
			res += raw_num
		if brackets:
			res += "}"
		return res
	
	if formular.tag[-8:] == "function":
		res += interpr_math_rec(formular[0])
		res += "("
		res += interpr_math_rec(formular[1])
		res += ")"
		return res
	
	# TODO this is not how the bound vars work
	# maybe it is even better to handle them in a separate def:
	if formular.tag[-9:] == "boundVars":
		count = len(formular)
		for elem in formular:
			res += interpr_math_rec(elem)
			count -= 1
			if count > 0:
				res += ", "
		return res
	
	if formular.tag[-8:] == "sequence":
		count = len(formular)
		for elem in formular:
			res += interpr_math_rec(elem)
			count -= 1
			if count > 0:
				res += ", "
		return res
	
	if formular.tag[-5:] == "range":
		res += interpr_math_rec(formular[0])
		res += " \\dotsc " # dots with commas " ,..., "
		res += interpr_math_rec(formular[1])
		return res

	if formular.tag[-2:] == "id":
		name = formular.text
		subs = ""
		# name globally known function?
		if name in known_functions:
			name = known_functions[name]
		# subscript
		if "subscript" in formular.attrib:
			subs = "_{" + formular.get("subscript")	+ "}"
		res += name + subs
		return res
	

	#TODO what if the matrix is too long to be rendered?
	#		shall the user do that or shall i define a maximum
	#		size?
	if formular.tag[-6:] == "matrix":
		cols = int(formular.get("cols"))
		rows = int(formular.get("rows"))

		entries = []
		for i in range(cols*rows):
			entries += [interpr_math_rec(formular[i], toplevel=True)]

		res += "\n\\begin{pmatrix}\n"
		for row in range(rows):
			for col in range(cols):
				res += entries[row + col*rows]
				if col < cols-1:
					res += " & "
				else:
					if row < rows -1:
						res += "\\\\"
					res += "\n"
		res += "\\end{pmatrix}"
		return res

	if formular.tag[-13:] == "unitReference":
		power = ""
		unit = formular.get("unit")
		
		if unit in abbrev_units:
			unit = abbrev_units[unit]
		
		if "power-numerator" in formular.attrib:
			power = "^{" + formular.get("power-numerator") + "}"

		res += unit + power
		return res

	print("math parser warning: unknown tag!")
	print(formular.tag)
	return res

#end recursive interpretation


# ========= POSTPROCESSING ===================

def clear_string(line):
	newl = line
	while newl[0] == "\t":
		newl = newl[1:]
	while newl[-1] == "\t":
		newl = newl[:-1]
	while newl.find("\t\t") != -1:
		newl = newl.replace("\t\t", "\t")

	while re.search(r"\)[ ]+\)", newl):
		newl = re.sub(r"\)[ ]+\)", "))", newl)
	while re.search(r"\([ ]+\(", newl):
		newl = re.sub(r"\([ ]+\(", "((", newl)
	
	newl = re.sub(r"\{[\s]*\(", "{", newl)
	newl = re.sub(r"\)[\s]*\}", "}", newl)

	while re.search(r"\n[\s]*\n", newl):
		newl = re.sub(r"\n[\s]*\n", "\n", newl)
	

	newl += "\n\n"
	return newl

# end def clean string

def texify_text(line):
	for sym in special_symbols_text:
		if sym in line:
			line = line.replace(sym, special_symbols_text[sym])
	return line
# end texify_text

def texify_math(line):
	for sym in special_symbols_math:
		if sym in line:
			line = line.replace(sym, special_symbols_math[sym])
	return line

def ungreek(line, regiontype):
	for symbol in greek_alphabet:
		if symbol in line:
			if regiontype == "math":
				line = line.replace(symbol, greek_alphabet[symbol])
			elif regiontype == "text":
				line = line.replace(symbol, "$ " + greek_alphabet[symbol] + " $")
	return line


# ======= CONVERSION MAIN ===========================

def convert(inpath, outpath):
	
	print("reading file: " + inpath)
	
	mcf = xml.etree.ElementTree.parse(inpath).getroot()
	
	regions = mcf.find("def:regions", ns)
	templines = []
	
	for region in regions:
		print("parsing region: " + region.get("region-id") )
		
		regiontype = region[0].tag[-4:]
		
		line = None

		if regiontype == "text":
			line = deepsearch_text(region[0])
			line = texify_text(line)
		if regiontype == "math":
			line = "$ " + interpr_math(region[0]) + " $"
			line = texify_math(line)
		
		if line == None:
			continue
		
		line = clear_string(line)
		line = ungreek(line, regiontype)
		templines += [line]
	
	print("parsing done.")

	outlines = templines
	
	print("writing to tex-file.")
	outfile = open(outpath, "w")

	outfile.write(author_note_output)
	outfile.write(tex_intro)

	for l in outlines:
		outfile.write(l.encode("utf8"))
	
	outfile.write(tex_outro)

	outfile.close()
	
	print("Everything done as you wished (hopefully)!\nHave a nice day!")

# end def convert
