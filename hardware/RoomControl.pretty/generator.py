#!/usr/bin/env python3
import sys

stdout = None

# shapes
CIRCLE = 0.5 # oval if width not equal to height
ROUNDRECT = 0.25 # 25% (KiCad default)
ROUNDRECT10 = 0.1 # 10%
ROUNDRECT5 = 0.05 # 5%
RECT = 0

# line widht of user drawings
userWidth = 0.1
userLayer = "Dwgs.User"

# line width of silkscreen drawings, double width at pin 1
silkScreenWidth = 0.1

# set sys.stdout and output footprint header to file
def header(name, top, maskMargin = 0, pasteMargin = 0, description = "", model = ""):
	print(f"{name}")
	
	# open a file for the footprint and redirect stdout to it
	global stdout
	stdout = sys.stdout
	sys.stdout = open(f"{name}.kicad_mod", 'w')
	
	print(f"(module {name} (layer F.Cu) (tedit 5EC043C1)")
	print(f"  (fp_text reference REF** (at 0 {top-2}) (layer F.SilkS) (effects (font (size 1 1) (thickness 0.15))))")
	print(f"  (fp_text value {name} (at 0 {top-0.8}) (layer F.Fab) (effects (font (size 1 1) (thickness 0.15))))")
	if maskMargin != 0:
		print(f"  (solder_mask_margin {maskMargin})")
	if pasteMargin != 0:
		print(f"  (solder_paste_margin {pasteMargin})")
	if description != "":
		print(f"  (descr \"{description}\")")
	if model != "":
		print(f"  (model {model} (at (xyz 0 0 0)) (scale (xyz 1 1 1)) (rotate (xyz 0 0 0)))")

# output footprint footer to file and restore sys.stdout
def footer():
	print(f")")
	
	# restore stdout
	sys.stdout.close()
	sys.stdout = stdout

# draw a line
def line(x1, y1, x2, y2, width, layer):
	print(f"  (fp_line (start {x1:.5g} {y1:.5g}) (end {x2:.5g} {y2:.5g}) (width {width}) (layer {layer}))")

# draw a package rectangle with pin 1 marking to fabrication layer
def fabRect(x1, y1, x2, y2):
	d = min(abs(x2 - x1), abs(y2 - y1)) * 0.2
	x = x1 + (d if x2 > x1 else -d)
	y = y1 + (d if y2 > y1 else -d)
	line(x1, y, x, y1, 0.1, "F.Fab")
	line(x, y1, x2, y1, 0.1, "F.Fab")
	line(x2, y1, x2, y2, 0.1, "F.Fab")
	line(x2, y2, x1, y2, 0.1, "F.Fab")
	line(x1, y2, x1, y, 0.1, "F.Fab")

# draw a rectangle to courtyard layer
def courtyardRect(x1, y1, x2, y2):
	line(x1, y1, x2, y1, 0.05, "F.CrtYd")
	line(x2, y1, x2, y2, 0.05, "F.CrtYd")
	line(x2, y2, x1, y2, 0.05, "F.CrtYd")
	line(x1, y2, x1, y1, 0.05, "F.CrtYd")

# draw a rectangle with pin 1 marking to silkscreen layer
def silkScreenRect(x1, y1, x2, y2):
	d = min(abs(x2 - x1), abs(y2 - y1)) * 0.2
	xa = x1 + (d if x2 > x1 else -d)
	ya = y1 + (d if y2 > y1 else -d)
	xb = xa + (0.4 if x2 > x1 else -0.4)
	yb = ya + (0.4 if y2 > y1 else -0.4)
	
	# pin 1 marking
	line(x1, y1, xa, y1, silkScreenWidth * 2, "F.SilkS")
	line(x1, y1, x1, ya, silkScreenWidth * 2, "F.SilkS")
	
	# remaining rectangle
	line(xb, y1, x2, y1, silkScreenWidth, "F.SilkS")
	line(x2, y1, x2, y2, silkScreenWidth, "F.SilkS")
	line(x2, y2, x1, y2, silkScreenWidth, "F.SilkS")
	line(x1, y2, x1, yb, silkScreenWidth, "F.SilkS")	

# draw a rectangle to user layer
def userRect(x1, y1, x2, y2):
	line(x1, y1, x2, y1, userWidth, userLayer)
	line(x2, y1, x2, y2, userWidth, userLayer)
	line(x2, y2, x1, y2, userWidth, userLayer)
	line(x1, y2, x1, y1, userWidth, userLayer)

# define a pad
def pad(index, kind, shape, x, y, width, height, drill = 0, offsetX = 0, offsetY = 0, clearance = 0, layers = ""):
	print(f"  (pad {index} {kind}", end = '')
	if shape <= RECT:
		print(f" rect", end = '')
	elif shape >= CIRCLE:
		if width == height:
			print(f" circle", end = '')
		else:
			print(f" oval", end = '')
	elif shape == ROUNDRECT:
		print(f" roundrect", end = '')
	else:
		print(f" roundrect (roundrect_rratio {shape})", end = '')
	print(f" (at {x:.5g} {y:.5g}) (size {width:.5g} {height:.5g})", end = '')
	if drill != 0:
		if type(drill) == tuple:
			(x, y) = drill 
			print(f" (drill oval {x:.5g} {y:.5g}", end = '')
		else:
			print(f" (drill {drill:.5g}", end = '')
		if offsetX != 0 or offsetY != 0:	
			print(f" (offset {offsetX:.5g} {offsetY:.5g})", end = '')
		print(f")", end = '')
	if clearance > 0:
		print(f" (clearance {clearance})", end = '')
	print(f" (layers {layers}))")

# define a through hole pad
def thruHolePad(index, shape, x, y, width, height, drill, offsetX = 0, offsetY = 0, clearance = 0, layers = "*.Cu *.Mask"):
	pad(index, "thru_hole", shape, x, y, width, height, drill, offsetX, offsetY, clearance, layers)

# define a smd pad
def smdPad(index, shape, x, y, width, height, clearance = 0, layers = "F.Cu F.Mask F.Paste"):
	pad(index, "smd", shape, x, y, width, height, clearance=clearance, layers=layers)

# define a smd exposed pad
def exposedPad(index, shape, x, y, width, height):
	pad(index, "smd", shape, x, y, width, height, layers="F.Cu F.Mask")
	nx = int(round(width / 1.25))
	ny = int(round(height / 1.25))
	w = width/nx
	h = height/ny
	for j in range(0, ny):
		for i in range(0, nx):
			pad('""', "smd", 0.25, x+(i-(nx-1)*0.5)*w, y+(j-(ny-1)*0.5)*h, w-0.3, h-0.3, layers="F.Paste")

# define a non plated through hole pad
def npthPad(x, y, width, height, clearance = 0, maskMargin = 0):
	print('  (pad "" np_thru_hole ', end = '')
	if width == height:
		print(f" circle (at {x:.5g} {y:.5g}) (size {width:.5g} {height:.5g}) (drill {width:.5g})", end = '')
	else:
		print(f" oval (at {x:.5g} {y:.5g}) (size {width:.5g} {height:.5g}) (drill oval {width:.5g} {height:.5g})", end = '')
	if clearance > 0:
		print(f" (clearance {clearance})", end = '')
	if maskMargin > 0:
		print(f" (solder_mask_margin {maskMargin})", end = '')
	print(f" (layers *.Cu *.Mask))")

# define a smd dual in-line footprint
def smdDilFootprint(name, packageWidth, packageHeight, count, shape, pitchX, pitchY, padWidth, padHeight,
		maskMargin = 0, pasteMargin = 0, description = "", model = ""):
	center = (count - 1) / 2

	# package
	packageRight = packageWidth / 2
	packageLeft = -packageRight
	packageBottom = packageHeight / 2
	packageTop = -packageBottom
	
	# pads
	rightPads = abs(pitchX / 2)
	rightPadsLeft = rightPads - padWidth / 2
	rightPadsRight = rightPads + padWidth / 2
	padsBottom = (count - 1 - center) * pitchY + padHeight / 2

	# courtyard encloses package and pads
	courtyardRight = max(packageRight, rightPadsRight + 0.1)
	courtyardLeft = -courtyardRight
	
	# don't print silkscreen onto pads
	silkScreenRight = min(packageRight, rightPadsLeft - silkScreenWidth) if packageRight < rightPads \
		else max(packageRight, rightPadsRight + silkScreenWidth) 
	if pitchX < 0:
		silkScreenRight = -silkScreenRight
	silkScreenLeft = -silkScreenRight
	silkScreenBottom = max(packageBottom, padsBottom + silkScreenWidth)
	silkScreenTop = -silkScreenBottom
	
	header(name, packageTop, maskMargin, pasteMargin, description, model)
	fabRect(packageLeft, packageTop, packageRight, packageBottom)
	courtyardRect(courtyardLeft, packageTop, courtyardRight, packageBottom)
	silkScreenRect(silkScreenLeft, silkScreenTop, silkScreenRight, silkScreenBottom)

	for i in range(0, count):
		smdPad(1 + i, shape, -pitchX / 2, (i - center) * pitchY, padWidth, padHeight)
		smdPad(count * 2 - i, shape, pitchX / 2, (i - center) * pitchY, padWidth, padHeight)


# bunding box
right = 13.0 / 2.0
left = -right
top = -(1.27 * 4.5 + 2.6)
bottom = 1.27 * 4.5 + 3.97
header("E73-2G4M08S1C-52840", top)
fabRect(right, bottom, left, top)
courtyardRect((left - 0.1), (top - 0.1), (right + 0.1), (bottom + 0.1))

# pads
size = 0.8
outerSize = 1.4
outerOffset = -1.0 / 2 + (outerSize - 1) / 2
bottomSize = 0.6
shape = 0.05 / size
pitch = 1.27
drill = 0.3

# right
for i in range(0, 10):
	smdPad(1 + i, shape, (right + outerOffset), (4.5 - i) * pitch, outerSize, size)

# top
for i in range(0, 8):
	smdPad(11 + i * 2, shape, (3.5 - i) * pitch, (top - outerOffset), size, outerSize)
for i in range(0, 7):
	smdPad(12 + i * 2, shape, (3 - i) * pitch, (top + 2.1), size, size)
	thruHolePad(12 + i * 2, ROUNDRECT, (3 - i) * pitch, (top + 2.1), bottomSize, size, drill)

# left
for i in range(0, 10):
	smdPad(26 if i == 0 else 25 + i * 2, shape, (left - outerOffset), (-4.5 + i) * pitch, outerSize, size)
for i in range(0, 8):
	smdPad(28 + i * 2, shape, (left + 2.1), (-3 + i) * pitch, size, size)
	thruHolePad(28 + i * 2, ROUNDRECT, (left + 2.1), (-3 + i) * pitch, size, bottomSize, drill)
footer()



# wago clamps
for pinCount in [3, 5, 6, 7]:
	# bounding box
	pitch = 5
	right = 6.5
	left = -7.5
	L = pinCount * pitch + 2.3
	bottom = (pinCount - 1) * pitch + 3.5
	top = bottom - L
	header(f"Wago_236-4{pinCount:02d}", top)
	fabRect(left, top, right-1.5, bottom)
	courtyardRect(left, top, right, bottom)
	silkScreenRect(left, top, right, bottom)
		
	# pads
	width = 1.8
	offset = 0.1
	height = 1.8
	drill = 1.1
	for i in range(0, pinCount):
		thruHolePad(1 + i, ROUNDRECT, -2.5, i * pitch, width, height, drill, offsetX=offset)
		thruHolePad(1 + i, ROUNDRECT, 2.5, i * pitch, width, height, drill, offsetX=-offset)
	footer()
	


# ST STM32F042F6 microcontroller
smdDilFootprint("STM32F042F6", 4.20, 6.60, 10, ROUNDRECT, 7.10 - 1.35, 0.65, 1.35, 0.40,
	description="https://www.st.com/resource/en/datasheet/stm32f042f6.pdf")
footer()



# On NCV7718, NCV7720, NCV7726 motor driver
smdDilFootprint("On_NCV77xx", 3.90, 8.65, 12, ROUNDRECT, 6.40 - 1.15, 0.65, 1.15, 0.40,
	description="https://www.onsemi.com/pub/Collateral/NCV7718-D.PDF https://www.onsemi.com/pub/Collateral/NCV7719-D.PDF https://www.onsemi.com/pub/Collateral/NCV7720-D.PDF")
exposedPad(25, ROUNDRECT5, 0, 0, 2.8, 5.6)
footer()



# On NCV7428MW lin driver
smdDilFootprint("On_NCV7428MW", 3.00, 3.00, 4, ROUNDRECT10, 3.30 - 0.60, 0.65, 0.60, 0.40,
	description="https://www.onsemi.com/pub/Collateral/NCV7428-D.PDF")
exposedPad(9, ROUNDRECT5, 0, 0, 1.60, 2.56)
footer()



# Texas TPS82130 buck regulator
smdDilFootprint("Texas_TPS82130", 2.9, 3.0, 4, ROUNDRECT10, 2.1, 0.65, 0.5, 0.4,
	description="Texas SIL0008D MicroSiP, 8 Pin (http://www.ti.com/lit/ds/symlink/tps82130.pdf#page=19)",
	model="${KISYS3DMOD}/Package_LGA.3dshapes/Texas_SIL0008D_MicroSiP-8-1EP_2.8x3mm_P0.65mm_EP1.1x1.9mm.wrl")
exposedPad(9, ROUNDRECT5, 0, 0, 1.1, 1.9)
epDrill = 0.3
for i in range(0, 3):
	thruHolePad(9, CIRCLE, 0, (-1 + i) * 0.75, epDrill + 0.1, epDrill + 0.1, epDrill, layers="*.Cu")
footer()



# Bosch BME680 air sensor, clockwise pin numbering
smdDilFootprint("Bosch_BME680", 3.0, 3.0, 4, ROUNDRECT10, -2.40, 0.80, 0.45, 0.45,
	description="Bosch BME680 air sensor (https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors-bme680/)")
footer()



# bounding box
right = 2.54 + 1.11
left = -2.54 - 1.11
top = -1.05
bottom = top + 14.8
header("Omron_G6SU-2", top,
	description="Relay Omron G6SU-2, see http://omronfs.omron.com/en_US/ecb/products/pdf/en-g6s.pdf",
	model="{KISYS3DMOD}/Relay_THT.3dshapes/Relay_DPDT_Omron_G6S-2.wrl")
fabRect(left, top, right, bottom)
courtyardRect(left, top, right, bottom)
silkScreenRect(left, top, right, bottom)

# pads
width = 1.8
offset = 0.1
height = 1.4
drill = 1
for i in range(0, 5):
	if i != 1:
		thruHolePad(1 + i, ROUNDRECT, -2.54, i * 2.54, width, height, drill, offsetX=offset)
		thruHolePad(12 - i, ROUNDRECT, 2.54, i * 2.54, width, height, drill, offsetX=-offset)
footer()



# bounding box
right = 5.8 / 2
left = -right
bottom = 12.8 / 2
top = -bottom
header("Omron_D2F-01", top,
	description="Switch Omron D2F-01, see https://omronfs.omron.com/en_US/ecb/products/pdf/en-d2f.pdf")
fabRect(left, top, right, bottom)
courtyardRect(left, top, right, bottom)
silkScreenRect(left, top, right, bottom)

# pads
width = 1.5
height = 2
drill = 1.1
pitch = 5.08
thruHolePad(3, ROUNDRECT, 0, 0, width, height, drill)
thruHolePad(2, ROUNDRECT, 0, -pitch, width, height, drill)
thruHolePad(1, ROUNDRECT, 0, pitch, width, height, drill)
footer()



# switch mount
def switchMountDrawing(coords):
	# mirror at x/y
	i = len(coords)
	while i > 0:
		i -= 1
		(x, y) = coords[i]
		coords += [(y, x)]
	
	# mirror at y
	i = len(coords)
	while i > 0:
		i -= 1
		(x, y) = coords[i]
		coords += [(-x, y)]
	
	# mirror at x
	i = len(coords)
	while i > 0:
		i -= 1
		(x, y) = coords[i]
		coords += [(x, -y)]
	
	for i in range(0, len(coords)):
		line(*coords[i], *coords[(i+1) % len(coords)], userWidth, userLayer)

header("Switch_Mount", 0)
switchMountDrawing([(25.5, 7), (22.8, 7), (22.8, 13.2), (24, 13.2), (24, 18.2), (23, 18.2)])
switchMountDrawing([(25.5, 7), (22.8, 7), (22.8, 13.2), (22, 13.2), (22, 17.8)])

#userRect(24, 4, -24, 7)
#userRect(24, -4, -24, -7)
userRect(24, 7, -24, -7)
userRect(5.6/2, 34.4/2, -5.6/2, 40/2)
userRect(5.6/2, -34.4/2, -5.6/2, -40/2)

# mounting holes
width = 3
height = 7
frontClearance = 1.5
backClearance = 0.3
thruHolePad(1, CIRCLE, 30, 0, width+backClearance*2, height+backClearance*2, (width, height))
smdPad(1, CIRCLE, 30, 0, width+frontClearance*2, height+frontClearance*2, layers="F.Cu F.Mask")
thruHolePad(2, CIRCLE, -30, 0, width+backClearance*2, height+backClearance*2, (width, height))
smdPad(2, CIRCLE, -30, 0, width+frontClearance*2, height+frontClearance*2, layers="F.Cu F.Mask")
thruHolePad(3, CIRCLE, 0, 30, height+backClearance*2, width+backClearance*2, (height, width))
smdPad(3, CIRCLE, 0, 30, height+frontClearance*2, width+frontClearance*2, layers="F.Cu F.Mask")
thruHolePad(4, CIRCLE, 0, -30, height+backClearance*2, width+backClearance*2, (height, width))
smdPad(4, CIRCLE, 0, -30, height+frontClearance*2, width+frontClearance*2, layers="F.Cu F.Mask")
npthPad(20.5, -6.6, 5, 3, clearance=1)
npthPad(-20.5, -6.6, 5, 3, clearance=1)
footer()
